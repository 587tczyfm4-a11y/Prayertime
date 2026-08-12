"""
Bot horaires de prière -> Discord (via Webhook)
Conçu pour tourner via GitHub Actions (gratuit), toutes les 5 minutes.

Aucune application à faire tourner sur ton iPhone : tout se passe dans le cloud.
Il suffit d'activer les notifications Discord sur ton téléphone, et ta Xiaomi
Band 10 les affichera automatiquement (relais via Mi Fitness/Zepp).
"""

import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

WEBHOOK_URL = os.environ["WEBHOOK_URL"]
LAT = os.environ["LAT"]
LON = os.environ["LON"]
CITY = os.environ.get("CITY", "")
METHODE_CALCUL = 2  # 2 = Islamic Society of North America ; change si besoin (voir doc Aladhan)
TOLERANCE_MINUTES = 5  # doit correspondre à la fréquence du cron GitHub Actions


def get_prayer_times():
    r = requests.get(
        "http://api.aladhan.com/v1/timings",
        params={"latitude": LAT, "longitude": LON, "method": METHODE_CALCUL},
        timeout=15,
    )
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
    requests.post(WEBHOOK_URL, json={"content": message}, timeout=15)


def main():
    times, tz_name = get_prayer_times()
    now_local = datetime.now(ZoneInfo(tz_name))

    for name, (h, m) in times.items():
        prayer_dt = now_local.replace(hour=h, minute=m, second=0, microsecond=0)
        delta_minutes = (now_local - prayer_dt).total_seconds() / 60
        if 0 <= delta_minutes < TOLERANCE_MINUTES:
            label = f" ({CITY})" if CITY else ""
            send_discord(f"🕌 **{name}** — {h:02d}:{m:02d}{label}")


if __name__ == "__main__":
    main()
