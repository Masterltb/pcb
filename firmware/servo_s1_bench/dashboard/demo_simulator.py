#!/usr/bin/env python3
"""MQTT-only bench device simulator for the local dashboard demo."""
import json
import os
import threading
import time

import paho.mqtt.client as mqtt

DEVICE_ID = os.getenv("FV_DEVICE_ID", "rev-s3-s1-bench-01")
HOST = os.getenv("FV_MQTT_HOST", "127.0.0.1")
PORT = int(os.getenv("FV_MQTT_PORT", "1883"))
ROOT = f"freshvend/{DEVICE_ID}"
COMMAND = f"{ROOT}/admin/command"
ACK = f"{ROOT}/admin/ack"
STATUS = f"{ROOT}/status"
AVAILABILITY = f"{ROOT}/availability"

state_lock = threading.Lock()
restart_event = threading.Event()
restart_command: dict | None = None
processed_ids: set[str] = set()
pulse_us = 1500
output_enabled = True
reset_reason = 1
client: mqtt.Client | None = None


def publish_ack(command_id: str, state: str, detail: str) -> None:
    with state_lock:
        payload = {"device_id": DEVICE_ID, "command_id": command_id,
                   "state": state, "detail": detail,
                   "pulse_us": pulse_us, "output_enabled": output_enabled}
        current_client = client
    if current_client and current_client.is_connected():
        current_client.publish(ACK, json.dumps(payload), qos=0, retain=False)


def publish_status() -> None:
    with state_lock:
        payload = {"device_id": DEVICE_ID, "firmware": "demo-simulator-1",
                   "ip": "mô phỏng cục bộ", "reset_reason": reset_reason,
                   "pulse_us": pulse_us, "output_enabled": output_enabled}
        current_client = client
    if current_client and current_client.is_connected():
        current_client.publish(STATUS, json.dumps(payload), qos=1, retain=True)


def on_message(_client, _userdata, message) -> None:
    global pulse_us, output_enabled, restart_command
    try:
        request = json.loads(message.payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return
    command_id = request.get("command_id", "")
    action = request.get("action", "")
    now = int(time.time())
    issued_at = request.get("issued_at", 0)
    if (message.topic != COMMAND or request.get("device_id") != DEVICE_ID or
            not isinstance(command_id, str) or not 1 <= len(command_id) <= 48 or
            type(issued_at) is not int or abs(now - issued_at) > 60):
        return
    if command_id in processed_ids:
        publish_ack(command_id, "duplicate", "ID lệnh đã được xử lý")
        return

    if action == "restart":
        processed_ids.add(command_id)
        restart_command = request
        publish_ack(command_id, "accepted", "Đã nhận yêu cầu khởi động lại CPU mô phỏng")
        restart_event.set()
        return
    if action == "servo.set":
        value = request.get("pulse_us")
        if type(value) is not int or not 1000 <= value <= 2000:
            publish_ack(command_id, "rejected", "Xung phải nằm trong dải 1000–2000 µs")
            return
        pulse_us = value
        output_enabled = True
    elif action == "servo.center":
        pulse_us, output_enabled = 1500, True
    elif action == "servo.on":
        output_enabled = True
    elif action == "servo.off":
        output_enabled = False
    elif action != "status":
        publish_ack(command_id, "rejected", "Lệnh không được hỗ trợ")
        return

    processed_ids.add(command_id)
    publish_ack(command_id, "done", "Đã cập nhật trạng thái mô phỏng")
    if action != "status":
        publish_status()


def start_client() -> mqtt.Client:
    global client
    while True:
        new_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                                 client_id=f"fv-demo-device-{DEVICE_ID}")
        new_client.will_set(AVAILABILITY, "offline", qos=1, retain=True)
        new_client.on_connect = lambda c, _u, _f, rc, _p: c.subscribe(COMMAND, qos=1) if rc == 0 else None
        new_client.on_message = on_message
        try:
            new_client.connect(HOST, PORT, keepalive=20)
            break
        except OSError as error:
            print(f"Đang chờ MQTT broker demo: {error}", flush=True)
            time.sleep(2)
    client = new_client
    new_client.loop_start()
    for _ in range(50):
        if new_client.is_connected():
            break
        time.sleep(0.1)
    new_client.publish(AVAILABILITY, "online", qos=1, retain=True)
    publish_status()
    return new_client


def main() -> None:
    global client, reset_reason, pulse_us, output_enabled
    start_client()
    print(f"Thiết bị mô phỏng {DEVICE_ID} đã kết nối MQTT", flush=True)
    while True:
        if not restart_event.wait(0.2):
            continue
        restart_event.clear()
        request = restart_command or {}
        command_id = request.get("command_id", "")
        old_client = client
        output_enabled = False
        publish_ack(command_id, "restarting", "PWM tắt; mô phỏng đang khởi động lại")
        if old_client:
            old_client.publish(AVAILABILITY, "offline", qos=1, retain=True)
            time.sleep(0.2)
            old_client.loop_stop()
            old_client.disconnect()
        time.sleep(2.0)
        reset_reason = 3
        pulse_us, output_enabled = 1500, True
        start_client()
        print(f"Thiết bị mô phỏng đã khởi động lại command_id={command_id}", flush=True)


if __name__ == "__main__":
    main()
