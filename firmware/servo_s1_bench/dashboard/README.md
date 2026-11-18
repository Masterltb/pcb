# FreshVend bench dashboard

Dashboard cục bộ cho firmware ESP32-S3 S1_TOP tại `../`. Nó dùng MQTT qua một
Python bridge; broker password và CA certificate chỉ nằm ở backend. Đây là công
cụ thử bench, chưa có tài khoản/role nhiều người dùng hay audit service production.

## Broker setup

Tạo hai tài khoản TLS với ACL riêng:

| Account | Publish | Subscribe |
|---|---|---|
| Device (`MQTT_USERNAME` trong `secrets.h`) | `freshvend/rev-s3-s1-bench-01/admin/ack`, `.../status`, `.../availability` | `freshvend/rev-s3-s1-bench-01/admin/command` |
| Dashboard backend | `freshvend/rev-s3-s1-bench-01/admin/command` | `freshvend/rev-s3-s1-bench-01/admin/ack`, `.../status`, `.../availability` |

Cho phép retained status/availability; lệnh admin phải được broker gửi với
`retain=false`. Device kiểm tra `device_id`, thời gian phát lệnh, ID lặp và xung
servo 1000–2000 µs trước khi thao tác.

## Run on Windows PowerShell

```powershell
cd F:\project\repo-github\pcb\pcb\firmware\servo_s1_bench\dashboard
python -m pip install -r requirements.txt
$env:FV_MQTT_HOST = "mqtt.example.net"
$env:FV_MQTT_PORT = "8883"
$env:FV_MQTT_USERNAME = "rev-s3-dashboard"
$env:FV_MQTT_PASSWORD = "set-this-locally"
$env:FV_MQTT_CA = "C:\path\to\broker-root-ca.pem"
$env:FV_ADMIN_TOKEN = "set-a-random-token-of-at-least-24-characters"
python server.py
```

Open `http://127.0.0.1:8787` and enter the admin token. The local HTTP server binds
to loopback by default. To use the dashboard from another machine, place it behind
an HTTPS reverse proxy and keep broker credentials on this backend; do not expose
the plain HTTP listener or place broker credentials in browser code.

## Dashboard actions

- **Refresh status** asks the device for current bench state.
- **Set pulse / Center / PWM on / PWM off** control only GPIO16 on the bench fixture.
- **Restart board** requires a reason and browser confirmation; it disables PWM,
  restarts the CPU, then waits for the device's offline/online and retained status.
- Command rows show the MQTT command ID and device ACK (`done`, `accepted`,
  `restarting`, `duplicate`, or `rejected`). Sending a command is not proof of
  hardware recovery; check online status and the reset reason after restart.

For hardware tests, secure the mechanism or disconnect the servo linkage first.
Firmware starts by applying its existing 1500 µs center pulse after every boot.
