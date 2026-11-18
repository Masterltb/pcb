#!/usr/bin/env python3
"""Local authenticated MQTT bridge and test dashboard for the Rev-S3 bench firmware."""
from __future__ import annotations

import json
import os
import secrets
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

import paho.mqtt.client as mqtt

DEVICE_ID = os.getenv("FV_DEVICE_ID", "rev-s3-s1-bench-01")
PREFIX = f"freshvend/{DEVICE_ID}"
COMMAND_TOPIC = f"{PREFIX}/admin/command"
ACK_TOPIC = f"{PREFIX}/admin/ack"
STATUS_TOPIC = f"{PREFIX}/status"
AVAILABILITY_TOPIC = f"{PREFIX}/availability"
WEB_DIR = Path(__file__).with_name("web")
ADMIN_TOKEN = os.getenv("FV_ADMIN_TOKEN", "")


class Bridge:
    def __init__(self) -> None:
        self.lock = threading.RLock()
        self.availability = "unknown"
        self.status: dict = {}
        self.broker = "connecting"
        self.updated_at: str | None = None
        self.commands: list[dict] = []
        host = os.environ["FV_MQTT_HOST"]
        port = int(os.getenv("FV_MQTT_PORT", "8883"))
        username = os.environ["FV_MQTT_USERNAME"]
        password = os.environ["FV_MQTT_PASSWORD"]
        ca_file = os.environ["FV_MQTT_CA"]
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                                  client_id=f"fv-admin-dashboard-{uuid4().hex[:10]}")
        self.client.username_pw_set(username, password)
        self.client.tls_set(ca_certs=ca_file)
        self.client.reconnect_delay_set(min_delay=1, max_delay=30)
        self.client.will_set(AVAILABILITY_TOPIC, "offline", qos=1, retain=True)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.host, self.port = host, port

    def start(self) -> None:
        self.client.connect_async(self.host, self.port, keepalive=30)
        self.client.loop_start()

    def stop(self) -> None:
        self.client.loop_stop()
        self.client.disconnect()

    def on_connect(self, client, _userdata, _flags, reason_code, _properties) -> None:
        with self.lock:
            self.broker = "online" if reason_code == 0 else f"connect error: {reason_code}"
        if reason_code == 0:
            client.subscribe([(ACK_TOPIC, 1), (STATUS_TOPIC, 1), (AVAILABILITY_TOPIC, 1)])

    def on_disconnect(self, _client, _userdata, _flags, reason_code, _properties) -> None:
        with self.lock:
            self.broker = f"offline ({reason_code})"

    def on_message(self, _client, _userdata, message) -> None:
        try:
            value = message.payload.decode("utf-8")
            with self.lock:
                if message.topic == AVAILABILITY_TOPIC:
                    self.availability = value[:32]
                elif message.topic == STATUS_TOPIC:
                    self.status = json.loads(value)
                    self.updated_at = datetime.now(timezone.utc).isoformat()
                elif message.topic == ACK_TOPIC:
                    ack = json.loads(value)
                    match = next((item for item in self.commands
                                  if item.get("command_id") == ack.get("command_id")), None)
                    if match:
                        match.update(ack)
                    else:
                        self.commands.insert(0, ack)
                    self.commands = self.commands[:50]
                    if ack.get("pulse_us") is not None:
                        self.status["pulse_us"] = ack["pulse_us"]
                    if ack.get("output_enabled") is not None:
                        self.status["output_enabled"] = ack["output_enabled"]
                    self.updated_at = datetime.now(timezone.utc).isoformat()
        except (UnicodeDecodeError, json.JSONDecodeError):
            with self.lock:
                self.broker = "invalid MQTT payload received"

    def snapshot(self) -> dict:
        with self.lock:
            return {"device_id": DEVICE_ID, "broker": self.broker,
                    "availability": self.availability, "status": self.status,
                    "updated_at": self.updated_at, "commands": list(self.commands)}

    def publish(self, action: str, reason: str, pulse_us: int | None = None) -> dict:
        command_id = uuid4().hex
        payload = {"device_id": DEVICE_ID, "command_id": command_id,
                   "action": action, "issued_at": int(time.time()), "reason": reason[:160]}
        if pulse_us is not None:
            payload["pulse_us"] = pulse_us
        entry = {"device_id": DEVICE_ID, "command_id": command_id,
                 "action": action, "state": "sent", "reason": reason[:160],
                 "created_at": datetime.now(timezone.utc).isoformat()}
        with self.lock:
            self.commands.insert(0, entry)
            self.commands = self.commands[:50]
        info = self.client.publish(COMMAND_TOPIC, json.dumps(payload), qos=1, retain=False)
        if info.rc != mqtt.MQTT_ERR_SUCCESS:
            with self.lock:
                entry["state"] = "failed"
                entry["detail"] = "Chưa kết nối được MQTT broker; lệnh chưa được gửi"
            raise RuntimeError(entry["detail"])
        return entry


def make_handler(bridge: Bridge):
    class Handler(BaseHTTPRequestHandler):
        def respond(self, code: int, value, content_type="application/json; charset=utf-8"):
            body = value if isinstance(value, bytes) else json.dumps(value).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'")
            self.end_headers()
            self.wfile.write(body)

        def authorized(self) -> bool:
            return secrets.compare_digest(self.headers.get("Authorization", ""),
                                          f"Bearer {ADMIN_TOKEN}")

        def do_GET(self):
            path = urlparse(self.path).path
            if path == "/":
                self.respond(200, (WEB_DIR / "index.html").read_bytes(), "text/html; charset=utf-8")
            elif path == "/app.js":
                self.respond(200, (WEB_DIR / "app.js").read_bytes(), "text/javascript; charset=utf-8")
            elif path == "/api/snapshot":
                if not self.authorized():
                    self.respond(401, {"error": "Cần mã quản trị"})
                    return
                self.respond(200, bridge.snapshot())
            else:
                self.respond(404, {"error": "Không tìm thấy đường dẫn"})

        def do_POST(self):
            if urlparse(self.path).path != "/api/command":
                self.respond(404, {"error": "Không tìm thấy đường dẫn"})
                return
            if not self.authorized():
                self.respond(401, {"error": "Cần mã quản trị"})
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 1 <= size <= 2048:
                    raise ValueError("Kích thước yêu cầu không hợp lệ")
                request = json.loads(self.rfile.read(size))
                action = request.get("action")
                reason = str(request.get("reason", "")).strip()[:160]
                if action not in {"restart", "status", "servo.center", "servo.off", "servo.on", "servo.set"}:
                    raise ValueError("Lệnh không được hỗ trợ")
                if action == "restart" and len(reason) < 3:
                    raise ValueError("Hãy nhập lý do khởi động lại")
                pulse = request.get("pulse_us")
                if action == "servo.set" and (type(pulse) is not int or not 1000 <= pulse <= 2000):
                    raise ValueError("Độ rộng xung phải là số nguyên từ 1000 đến 2000 micro giây")
                result = bridge.publish(action, reason, pulse)
                self.respond(202, result)
            except (ValueError, TypeError, RuntimeError, json.JSONDecodeError) as error:
                self.respond(400 if not isinstance(error, RuntimeError) else 503,
                             {"error": str(error)})

        def log_message(self, *_args):
            pass

    return Handler


def main() -> None:
    if len(ADMIN_TOKEN) < 24:
        raise SystemExit("Hãy đặt FV_ADMIN_TOKEN thành mã ngẫu nhiên dài ít nhất 24 ký tự")
    bridge = Bridge()
    bridge.start()
    host = os.getenv("FV_DASHBOARD_HOST", "127.0.0.1")
    port = int(os.getenv("FV_DASHBOARD_PORT", "8787"))
    server = ThreadingHTTPServer((host, port), make_handler(bridge))
    print(f"Dashboard bàn thử FreshVend: http://{host}:{port} (thiết bị {DEVICE_ID})", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        bridge.stop()


if __name__ == "__main__":
    main()
