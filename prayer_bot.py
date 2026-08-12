"""
Bot horaires de prière -> Discord (via Webhook)
Conçu pour tourner via GitHub Actions (gratuit), toutes les 5 minutes.
 
Aucune application à faire tourner sur ton iPhone : tout se passe dans le cloud.
Il suffit d'activer les notifications Discord sur ton téléphone, et ta Xiaomi
Band 10 les affichera automatiquement (relais via Mi Fitness/Zepp).
"""
 
import os
import sys
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
 
WEBHOOK_URL = os.environ["WEBHOOK_URL"]
LAT = os.environ["LAT"]
LON = os.environ["LON"]
CITY = os.environ.get("CITY", "")
TEST_MODE = os.environ.get("TEST_MODE", "false").lower() == "true"
METHODE_CALCUL = 2  # 2 = Islamic Society of North America ; change si besoin (voir doc Aladhan)
TOLERANCE_MINUTES = 5  # doit correspondre à la fréquence du cron GitHub Actions
 
 
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
 
 
def main():
    print(f"LAT={LAT} LON={LON} CITY={CITY} TEST_MODE={TEST_MODE}")
 
    times, tz_name = get_prayer_times()
    now_local = datetime.now(ZoneInfo(tz_name))
    print(f"Fuseau horaire détecté : {tz_name}")
    print(f"Heure locale actuelle : {now_local.strftime('%Y-%m-%d %H:%M:%S')}")
    print("Horaires du jour :")
    for name, (h, m) in times.items():
        print(f"  {name} : {h:02d}:{m:02d}")
 
    if TEST_MODE:
        label = f" ({CITY})" if CITY else ""
        send_discord(f"✅ Test réussi{label} — le bot est bien connecté à Discord.")
        return
 
    sent_any = False
    for name, (h, m) in times.items():
        prayer_dt = now_local.replace(hour=h, minute=m, second=0, microsecond=0)
        delta_minutes = (now_local - prayer_dt).total_seconds() / 60
        if 0 <= delta_minutes < TOLERANCE_MINUTES:
            label = f" ({CITY})" if CITY else ""
            send_discord(f"🕌 **{name}** — {h:02d}:{m:02d}{label}")
            sent_any = True
 
    if not sent_any:
        print("Aucune prière dans la fenêtre actuelle, rien à envoyer (normal).")
 
 
if __name__ == "__main__":
    main()
 
