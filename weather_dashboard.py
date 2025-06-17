#!/usr/bin/env python3
import os
import json
import queue
import threading
import time
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime

# ─── Configuration ───────────────────────────────────────
BROKER = "localhost"
PORT   = 1883
USER   = os.getenv("MQTT_USER", "viewer")
PW     = os.getenv("MQTT_PW", "taf")
TOPIC  = "weather/athens/raw"
QOS    = 1

# ─── Thread‐safe queue for incoming payloads ─────────────
data_q = queue.Queue()

# ─── MQTT callbacks ──────────────────────────────────────
def on_connect(client, userdata, flags, rc):
    client.subscribe(TOPIC, qos=QOS)
    print(f"[{datetime.now():%H:%M:%S}] Subscribed to {TOPIC}")

def on_message(client, userdata, msg):
    try:
        # Try to parse only valid JSON payloads
        payload = json.loads(msg.payload.decode())
        data_q.put(payload)
    except Exception:
        # Skip anything that isn't valid JSON
        pass

# ─── Start MQTT client in background thread ──────────────
def mqtt_thread():
    client = mqtt.Client(protocol=mqtt.MQTTv311)  # v3.1.1
    client.username_pw_set(USER, PW)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT)
    client.loop_forever()

threading.Thread(target=mqtt_thread, daemon=True).start()

# ─── Set up Matplotlib plot ──────────────────────────────
fig, ax = plt.subplots()
line_temp, = ax.plot([], [], label="Temp (°C)")
line_hum,  = ax.plot([], [], label="Humidity (%)")

ax.set_xlabel("Time")
ax.set_ylabel("Value")
ax.legend(loc="upper left")
ax.grid(True)

# Buffers for the last N points
MAX_POINTS = 50
times, temps, hums = [], [], []

# ─── Animation update function ──────────────────────────
def update(frame):
    # Drain the queue
    while not data_q.empty():
        d = data_q.get()
        ts = datetime.fromtimestamp(d.get("ts", time.time()))
        times.append(ts)
        temps.append(d.get("temp", None))
        hums.append(d.get("humidity", None))

    # Keep only the last MAX_POINTS
    xs = times[-MAX_POINTS:]
    ys1 = temps[-MAX_POINTS:]
    ys2 = hums[-MAX_POINTS:]

    # Update line data
    line_temp.set_data(xs, ys1)
    line_hum.set_data(xs, ys2)

    # Rescale axes
    ax.relim()
    ax.autoscale_view()

    # Return updated artists
    return line_temp, line_hum

ani = animation.FuncAnimation(fig, update, interval=1000)
plt.show()
