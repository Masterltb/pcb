# Dashboard bàn thử FreshVend

Dashboard chạy cục bộ cho firmware ESP32-S3 S1_TOP tại `../`. Dashboard kết nối MQTT
qua cầu nối Python; mật khẩu broker và chứng chỉ CA chỉ lưu ở backend. Đây là công
cụ thử nghiệm, chưa có hệ thống nhiều tài khoản/phân quyền hoặc nhật ký kiểm toán cho
môi trường vận hành.

## Chạy demo đầy đủ không cần board

Cần Docker Desktop đang chạy. Demo gồm Mosquitto, dashboard và một thiết bị ESP32
mô phỏng. Broker chỉ nằm trong mạng Docker, không mở cổng MQTT ra máy chủ; dashboard
chỉ mở tại `127.0.0.1`.

```powershell
cd F:\project\repo-github\pcb\pcb\firmware\servo_s1_bench\dashboard
docker compose -f compose.demo.yaml up --build -d
docker compose -f compose.demo.yaml logs -f
```

Mở `http://127.0.0.1:8787`, nhập mã demo mặc định
`freshvend-demo-admin-token-change-me`. Có thể đặt mã riêng trước khi chạy bằng
`$env:FV_ADMIN_TOKEN = "mã-ngẫu-nhiên-dài-hơn-24-ký-tự"`.

Thử theo thứ tự:

1. Chờ thiết bị báo **Đang hoạt động** và trạng thái hiện **Thiết bị mô phỏng**.
2. Thử **Đặt xung** với `1500`, **Tắt PWM**, rồi **Bật PWM**; lịch sử phải nhận ACK.
3. Nhập lý do, nhấn **Khởi động lại board**, rồi xác nhận.
4. Kỳ vọng lịch sử hiện **Đã nhận lệnh** rồi **Đang khởi động lại**; trạng thái thoáng
   chuyển ngoại tuyến, sau đó trực tuyến lại. Nguyên nhân khởi động hiển thị **Reset
   phần mềm**, xung trở về `1500 µs`.

Lệnh trong demo chỉ đổi trạng thái phần mềm; không điều khiển servo vật lý. Dừng demo:

```powershell
docker compose -f compose.demo.yaml down
```

## Chuyển sang board thật

Tắt demo trước để simulator không chiếm cùng `device_id`. Nạp firmware bench sau khi
cấu hình `secrets.h`, rồi chạy dashboard backend theo phần bên dưới với broker TLS
thật, ACL giới hạn theo topic và tài khoản riêng. Board phải truy cập được broker
qua mạng Wi-Fi. Dashboard demo Docker không mở broker cho board thật.

Trước khi nạp, tháo tải servo hoặc cố định cơ cấu an toàn: firmware phát xung giữa
1500 µs ở GPIO16 mỗi lần boot, kể cả sau reset từ xa. Không dùng firmware một-servo
này cho máy bán hàng đang vận hành.

1. Mở `firmware/servo_s1_bench/secrets.h` trên máy và điền SSID/mật khẩu Wi-Fi,
   MQTT host/port, tài khoản thiết bị và chứng chỉ CA của broker. Không gửi các bí mật
   này vào chat; file `secrets.h` đã được Git bỏ qua.
2. Kiểm tra board xuất hiện đúng cổng COM trong `platformio.ini` (hiện đặt `COM4`),
   rồi build và nạp:

   ```powershell
   pio run --project-dir F:\project\repo-github\pcb\pcb\firmware\servo_s1_bench
   pio run --project-dir F:\project\repo-github\pcb\pcb\firmware\servo_s1_bench --target upload
   ```

3. Chạy backend dashboard trên máy tính với cùng broker TLS, nhưng dùng tài khoản
   backend riêng theo ACL bên dưới. Ví dụ:

   ```powershell
   cd F:\project\repo-github\pcb\pcb\firmware\servo_s1_bench\dashboard
   $env:FV_MQTT_HOST = "mqtt.example.net"
   $env:FV_MQTT_PORT = "8883"
   $env:FV_MQTT_USERNAME = "rev-s3-dashboard"
   $env:FV_MQTT_PASSWORD = "đặt-cục-bộ-trên-máy"
   $env:FV_MQTT_CA = "C:\path\to\broker-root-ca.pem"
   $env:FV_ADMIN_TOKEN = "mã-ngẫu-nhiên-dài-hơn-24-ký-tự"
   python server.py
   ```

4. Mở `http://127.0.0.1:8787`, đăng nhập mã quản trị, chờ board báo **Đang hoạt
   động**, rồi mới thử lệnh reset. Nếu board không online, xem Serial Monitor ở
   115200 baud và kiểm tra Wi-Fi/NTP/TLS/broker trước; không gửi lệnh retained.

## Broker setup

Tạo hai tài khoản TLS với ACL riêng:

| Tài khoản | Được publish | Được subscribe |
|---|---|---|
| Device (`MQTT_USERNAME` trong `secrets.h`) | `freshvend/rev-s3-s1-bench-01/admin/ack`, `.../status`, `.../availability` | `freshvend/rev-s3-s1-bench-01/admin/command` |
| Dashboard backend | `freshvend/rev-s3-s1-bench-01/admin/command` | `freshvend/rev-s3-s1-bench-01/admin/ack`, `.../status`, `.../availability` |

Cho phép lưu retained cho trạng thái và availability; lệnh quản trị phải được gửi
với `retain=false`. Board kiểm tra `device_id`, thời điểm phát lệnh, ID trùng và
xung servo 1000–2000 µs trước khi thực hiện.

## Chạy trên Windows PowerShell

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

Mở `http://127.0.0.1:8787` rồi nhập mã quản trị. Máy chủ HTTP chỉ lắng nghe loopback
theo mặc định. Nếu cần truy cập từ máy khác, đặt dashboard sau reverse proxy dùng
HTTPS; giữ thông tin broker trong backend, không đưa thông tin này vào mã trình duyệt
và không mở trực tiếp HTTP ra mạng.

## Các chức năng

- **Làm mới trạng thái** yêu cầu board gửi trạng thái bàn thử hiện tại.
- **Đặt xung / Về giữa / Bật PWM / Tắt PWM** chỉ điều khiển GPIO16 trên bàn thử.
- **Khởi động lại board** yêu cầu nhập lý do và xác nhận; firmware tắt PWM, khởi động
  lại CPU, rồi dashboard chờ board ngoại tuyến/trực tuyến và trạng thái retained mới.
- Lịch sử hiển thị ID lệnh MQTT và ACK từ board. Gửi lệnh thành công chưa có nghĩa
  phần cứng đã phục hồi; hãy kiểm tra trạng thái online và mã nguyên nhân reset.

Trước khi thử phần cứng, hãy cố định cơ cấu hoặc tháo liên kết servo. Mỗi lần boot,
firmware hiện phát xung giữa 1500 µs như hành vi mặc định.
