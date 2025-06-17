import os
import json
import time
import requests
import paho.mqtt.client as mqtt
from datetime import datetime

# --- Configuration from environment or defaults ---
CITY      = "Athens,GR"
BROKER    = "localhost"
PORT      = 1883
USERNAME  = os.getenv("MQTT_USER", "publisher")
PASSWORD  = os.getenv("MQTT_PW", "taf")
API_KEY   = os.getenv("OWM_KEY", "bfc782bf00b083403159e319903d7d59")
TOPIC     = f"weather/athens/raw"
INTERVAL  = 10    # 10 minutes in seconds
UNITS     = "metric"   # or "imperial"

# --- Setup MQTT client ---
client = mqtt.Client()
client.username_pw_set(USERNAME, PASSWORD)
client.connect(BROKER, PORT)
client.loop_start()

# --- Main loop ---
while True:
    try:
        # Fetch data
        resp = requests.get(
            "http://api.openweathermap.org/data/2.5/weather",
            params={"q": CITY, "appid": API_KEY, "units": UNITS},
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()

        # Build payload
        payload = {
            "ts": int(time.time()),
            "city": CITY,
            "temp": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
        }

        # Publish with QoS=1
        client.publish(TOPIC, json.dumps(payload), qos=1)
        print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Published: {payload}")

    except Exception as e:
        print(f"[Error] {e}")

    time.sleep(INTERVAL)
