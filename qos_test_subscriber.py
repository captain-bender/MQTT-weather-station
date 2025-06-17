# qos_test_subscriber.py
import time
import json
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT   = 1883
USER   = "viewer"
PW     = "taf"
TOPIC  = "weather/athens/raw"
PUBLISH_INTERVAL = 5    # publisher is sending every 5s

def on_message(client, userdata, msg):
    print(msg.payload.decode())

for qos in (0, 1, 2):
    print(f"\n--- Testing QoS {qos} ---")

    # 1) Initial subscribe & receive 2 messages
    client = mqtt.Client(
        client_id="viewer-test",
        clean_session=False,
        protocol=mqtt.MQTTv311
    )
    client.username_pw_set(USER, PW)
    client.on_message = on_message
    client.connect(BROKER, PORT)
    client.subscribe(TOPIC, qos=qos)
    client.loop_start()

    print("Receiving 2 live messages…")
    time.sleep(PUBLISH_INTERVAL * 2 + 1)  # wait for ~2 publishes

    client.loop_stop()
    client.disconnect()

    # 2) Go offline during 3 publishes
    offline_time = PUBLISH_INTERVAL * 3 + 1
    print(f"Subscriber offline for ~{offline_time}s…")
    time.sleep(offline_time)

    # 3) Reconnect & catch **only** the queued messages
    client = mqtt.Client(
        client_id="viewer-test",
        clean_session=False,
        protocol=mqtt.MQTTv311
    )
    client.username_pw_set(USER, PW)
    client.on_message = on_message
    client.connect(BROKER, PORT)
    client.subscribe(TOPIC, qos=qos)
    client.loop_start()

    print("Receiving backlog (should be 3 msgs if QoS>0)…")
    time.sleep(1)   # only backlog, before next publish

    client.loop_stop()
    client.disconnect()
