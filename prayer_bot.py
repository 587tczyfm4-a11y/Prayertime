"""
Bot horaires de prière -> Discord (via Webhook)
Conçu pour tourner via GitHub Actions, déclenché par cron-job.org.

- Récupère les horaires du jour via l'API Aladhan.
- Envoie un message Discord (texte simple, sans Markdown/emoji, pour un
  affichage propre sur la Xiaomi Band).
- Retient dans le fichier last_sent.json quelles prières ont déjà été
  notifiées aujourd'hui, pour ne jamais envoyer deux fois le même message
  même si le workflow est déclenché plusieurs fois dans la fenêtre.
"""

import os
import sys
import json
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

WEBHOOK_URL = os.environ["WEBHOOK_URL"]
LAT = os.environ["LAT"]
LON = os.environ["LON"]
CITY = os.environ.get("CITY", "")
TEST_MODE = os.environ.get("TEST_MODE", "false").lower() == "true"
METHODE_CALCUL = 2  # 2 = ISNA ; change si besoin (voir doc Aladhan)
TOLERANCE_MINUTES = 15  # marge pour absorber les retards de déclenchement
STATE_FILE = "last_sent.json"


def get_prayer_times():
    r = requests.get(
        "http://api.aladhan.com/v1/timings",
        params={"latitude": LAT, "longitude": LON, "method": METHODE_CALCUL},
        timeout=15,
    )
    r.raise_for_status()
    data = r.json()["data"]
    timings = data["timings"]
    tz_name = data["meta"]["timezone"]
    order = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
    result = {}
    for name in order:
        h, m = map(int, timings[name].split(":")[:2])
        result[name] = (h, m)
    return result, tz_name


def send_discord(message):
    r = requests.post(WEBHOOK_URL, json={"content": message}, timeout=15)
    if r.status_code >= 300:
        print(f"ERREUR envoi Discord : status {r.status_code} - {r.text}")
        sys.exit(1)
    print(f"Message envoyé avec succès : {message}")


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def main():
    print(f"LAT={LAT} LON={LON} CITY={CITY} TEST_MODE={TEST_MODE}")

    times, tz_name = get_prayer_times()
    now_local = datetime.now(ZoneInfo(tz_name))
    today_str = now_local.strftime("%Y-%m-%d")
    print(f"Heure locale actuelle : {now_local.strftime('%Y-%m-%d %H:%M:%S')}")
    print("Horaires du jour :")
    for name, (h, m) in times.items():
        print(f"  {name} : {h:02d}:{m:02d}")

    if TEST_MODE:
        label = f" ({CITY})" if CITY else ""
        send_discord(f"Test réussi{label} — le bot est bien connecté à Discord.")
        return

    state = load_state()
    already_sent_today = state.get(today_str, [])

    sent_any = False
    for name, (h, m) in times.items():
        if name in already_sent_today:
            continue

        prayer_dt = now_local.replace(hour=h, minute=m, second=0, microsecond=0)
        delta_minutes = (now_local - prayer_dt).total_seconds() / 60
        if 0 <= delta_minutes < TOLERANCE_MINUTES:
            label = f" ({CITY})" if CITY else ""
            send_discord(f"{name} — {h:02d}:{m:02d}{label}")
            already_sent_today.append(name)
            sent_any = True

    if sent_any:
        # On ne garde que le jour courant dans le fichier, pour qu'il reste léger
        save_state({today_str: already_sent_today})
    else:
        print("Aucune nouvelle prière à envoyer (déjà notifiée ou hors fenêtre).")


if __name__ == "__main__":
    main()
