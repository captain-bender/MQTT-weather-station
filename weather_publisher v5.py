import os
import json
import time
import requests
import paho.mqtt.client as mqttClient
from paho.mqtt.client import CallbackAPIVersion

from datetime import datetime

# --- Configuration from environment or defaults ---
CITY      = "Athens,GR"
BROKER    = "localhost"
PORT      = 1883
USERNAME  = os.getenv("MQTT_USER", "publisher")
PASSWORD  = os.getenv("MQTT_PW", "taf")
API_KEY   = os.getenv("OWM_KEY", "bfc782bf00b083403159e319903d7d59")
TOPIC     = f"weather/athens/raw"
INTERVAL  = 5    # 10 minutes in seconds
UNITS     = "metric"   # or "imperial"

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"[{datetime.now():%H:%M:%S}] Connected (code={reason_code})")
    # You could check properties if needed:
    # print("Conn ack properties:", properties)

def on_publish(client, userdata, mid, reason_code, properties):
    # reason_code is the MQTT v5 PUBACK reason, properties are v5 PUBACK properties
    print(f"[{datetime.now():%H:%M:%S}] Message {mid} published (rc={reason_code})")

def on_disconnect(client, userdata, *args):
    reason_code = args[0] if args else None
    print(f"[{datetime.now():%H:%M:%S}] Disconnected (code={reason_code})")


client = mqttClient.Client(
    callback_api_version=CallbackAPIVersion.VERSION2,
    client_id="weather_publisher_v2",
    protocol=mqttClient.MQTTv5,
    
)

client.username_pw_set(USERNAME, PASSWORD)
client.on_connect    = on_connect
client.on_publish    = on_publish
client.on_disconnect = on_disconnect

# Connect (no special v5 properties here)
client.connect(BROKER, PORT)
client.loop_start()

# --- Main loop ---
try:
    while True:
        # 1) Fetch weather data
        resp = requests.get(
            "http://api.openweathermap.org/data/2.5/weather",
            params={"q": CITY, "appid": API_KEY, "units": UNITS},
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()

        # 2) Build payload
        payload = {
            "ts": int(time.time()),
            "city": CITY,
            "temp": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
        }

        # 3) Publish with QoS=1 (retain=False for live data)
        result = client.publish(
            TOPIC,
            json.dumps(payload),
            qos=1,
            retain=False
        )
        # You can inspect result.rc or rely on on_publish callback
        print("Publish result:", result)

        # 4) Optional local log
        with open("weather_log.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")

        # 5) Wait until next interval
        time.sleep(INTERVAL)

except KeyboardInterrupt:
    print("\nInterrupted by user, shutting down…")
finally:
    client.loop_stop()
    client.disconnect()