# Dashboard bàn thử FreshVend

Dashboard chạy cục bộ cho firmware ESP32-S3 S1_TOP tại `../`. Dashboard kết nối MQTT
qua cầu nối Python; mật khẩu broker và chứng chỉ CA chỉ lưu ở backend. Đây là công
cụ thử nghiệm, chưa có hệ thống nhiều tài khoản/phân quyền hoặc nhật ký kiểm toán cho
môi trường vận hành.

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
