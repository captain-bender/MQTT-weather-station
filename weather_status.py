import json
import time
import paho.mqtt.client as mqtt
from datetime import datetime
import os

BROKER   = "localhost"
PORT     = 1883
USER     = os.getenv("MQTT_USER", "publisher")
PW       = os.getenv("MQTT_PW", "taf")
STATUS_T = "weather/athens/status"

# 1) Create client and set LWT **before** connect
client = mqtt.Client(client_id="status-publisher", clean_session=False, protocol=mqtt.MQTTv311)
client.username_pw_set(USER, PW)
client.will_set(
    STATUS_T,
    payload=json.dumps({"status": "offline"}),
    qos=1,
    retain=True
)

# 2) Connect and immediately publish “online” status
client.connect(BROKER, PORT)
client.loop_start()
client.publish(
    STATUS_T,
    payload=json.dumps({"status": "online"}),
    qos=1,
    retain=True
)
print(f"[{datetime.now().strftime('%H:%M:%S')}] Published ONLINE status, now idling…")

# 3) Keep running until killed
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Clean exit")
finally:
    client.loop_stop()
    client.disconnect()
