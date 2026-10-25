# FreshVend RevB — mô phỏng ESP32, servo, IR và server

Đây là **bộ mô phỏng chức năng**, không phải firmware nạp vào máy thật hoặc mô phỏng
điện đầy đủ của PCB. Không thay đổi GPIO, KiCad hoặc lựa chọn ESP32 QFN của RevB.
Hình DevKit trong Wokwi chỉ đại diện CPU ESP32. Bốn servo 0–180° là chỉ báo độ rộng
xung; không mô phỏng servo quay liên tục, tải tô, góc iris hoặc lực giữ thực.

## 1. Mở và chạy

**Cách A — Wokwi trên trình duyệt:** tạo project ESP32 ở https://wokwi.com/projects/new/esp32 .
Thay nội dung `sketch.ino`, thêm file `controller.h`, thay `diagram.json` bằng các
file cùng tên trong thư mục này. Không cần thư viện Arduino bên ngoài. Nhấn Run.
Code dùng API LEDC của Arduino-ESP32 2.x; bản PlatformIO đã khóa phiên bản bên dưới
là đường build đã kiểm tra. Nếu compiler online đổi sang core3.x, dùng cách B;
không đổi chân hoặc thay ngẫu nhiên API để ép build.

**Cách B — VS Code + PlatformIO + Wokwi:** mở chính thư mục `simulation/revb`
làm workspace, không mở root repo thay thế. Build:

```powershell
pio run --project-dir F:\project\repo-github\pcb\pcb\simulation\revb
```

Sau đó chạy lệnh VS Code **Wokwi: Start Simulator**. `wokwi.toml` trỏ tới BIN/ELF
trong `.pio/build/esp32dev/`. Extension/CLI cần quyền sử dụng Wokwi phù hợp;
không lưu license/token vào Git. Không chạy `pio run -t upload` vào board thật.

## 2. Thử xuất một tô

Mở Serial Monitor 115200 baud, gửi từng dòng có newline:

```text
status
arm
vend demo-1 1
```

Trước `arm`: cả hai công tắc IR ở **LEFT=CLEAR**. Xác nhận trạng thái khởi đầu
giả định TOP OPEN / BOTTOM CLOSED. Lệnh `arm` không tự homing và không chạy servo.

Quan sát log và hình bốn servo:

```text
ACK id=demo-1 col=1 ACCEPTED
STATE id=demo-1 col=1 OPEN_BOTTOM
STATE id=demo-1 col=1 WAIT_DROP
```

Khi thấy WAIT_DROP, gạt IR1 sang **RIGHT=BLOCKED**, giữ ít nhất50ms, rồi gạt
về LEFT=CLEAR. Sau đó xuất hiện CLOSE_BOTTOM → OPEN_TOP → RESULT ... DONE.
Gửi lại `vend demo-1 1`: nhận DUPLICATE, không chuyển động thêm.
Thử cột2 bằng `vend demo-2 2` và IR2.

Các mức xung mô phỏng: stop1500µs, close1100µs, open1900µs, chu kỳ20ms.
Mỗi chuyển động350ms, timeoutIR3000ms, debounce20ms. **Tất cả là tham số giả định**,
không phải giá trị đã hiệu chuẩn cho MG996R/iris thật.

## 3. Các tình huống cần thử

| Tình huống | Thao tác | Kết quả mong đợi |
|---|---|---|
| Chưa arm | Gửi vend ngay | NOT_ARMED |
| IR đã chắn | IR sang phải trước arm/lệnh | Từ chối arm hoặc BEAM_NOT_CLEAR |
| Không có tô | Không gạt IR sau WAIT_DROP | IR_TIMEOUT, dừng xung chuyển động, cột ở Fault |
| IR kẹt mức | Gạt phải nhưng không trả trái | Không báo DONE; timeout |
| Nhiễu ngắn | Xung IR ngắn hơn20ms | Không coi là tô đã qua |
| Lệnh trùng | Gửi lại cùngID/cột | DUPLICATE, không chạy lại |
| CùngID khác cột | Gửi ID cũ với cột khác | ID_CONFLICT |
| Hai cột | Gửi haiID/cột khác khi đang chạy qua serial | Hai cột độc lập, mỗi cột một motor chạy |
| Dừng | `stop` | Dừng cả hai, cần phục hồi thủ công và arm lại |
| Reset giữa chừng | `reset` trong lúc đang chuyển động | Boot khóa; ID dang dở thành INTERRUPTED; không tự chạy lại |
| Limit thiếu | `stop`, `limits on`, `arm`, vend | Nếu TOP không được xác nhận đóng, TOP_LIMIT_TIMEOUT |

Khôi phục sau lỗi: `stop`, kiểm tra/đặt lại trạng thái cơ khí giả định, trả IR
về CLEAR, rồi `arm`. Cơ cấu không được tự chạy để đoán vị trí sau reset.

Limit là **tùy chọn/DNP** trong PCB; simulation mặc định `limits off`, nhưng luôn
đọc bốn chân. Khi bật, LOW nghĩa là xác nhận đóng. Mặc định các switch TOP=OPEN,
BOTTOM=CLOSED; hãy đổi switch TOP sang CLOSED khi mô phỏng nó đã đóng.
Kiểm tra limit ở cuối thời gian di chuyển không thay thế mô hình hành trình thực.

IR được nhập ở mức logic **sau receiver**: CLEAR=LOW, BLOCKED=HIGH.
Không mô phỏng quang học, burst nhận/AGC, ánh sáng môi trường hoặc đứt dây thật.
GPIO23 phát38kHz có cửa sổ1ms bật/1ms tắt bằng timer-task, độc lập HTTP;
logic analyzer cho phép quan sát, nhưng thời gian thực phải đo lại trên phần cứng.

## 4. Server local ↔ ESP32 qua Wi-Fi

Terminal1 trên Windows:

```powershell
python simulation/revb/server.py serve
```

Trong Wokwi: chạy simulator, gửi `arm`, rồi `net on`.
Firmware kết nối Wokwi-GUEST, truy cập `http://host.wokwi.internal:8765`.
**Server trên máy bạn cần Private IoT Gateway** (hoặc gateway đi kèm extension
có quyền truy cập local); Public Gateway không truy cập localhost/LAN.
Quyền dùng gateway/extension phụ thuộc tài khoản Wokwi. Không tự mở port/router
hoặc đưa server này ra Internet. Server mẫu chỉ bind127.0.0.1 và phục vụ một máy.

Terminal2:

```powershell
python simulation/revb/server.py vend net-1 1
python simulation/revb/server.py status
```

Gạt IR theo bước2. Khi yên, ESP32 gửi trạng thái lên server và chờ phản hồi
đúng `id:status`; nếu mất phản hồi sẽ thử lại. Server không đếm trùng sự kiện.
`net off` tạm ngắt mạng; `net on` kết nối lại. Khi mất mạng giữa chu trình,
máy mô phỏng tiếp tục chu trình cục bộ tới kết quả hoặc timeout, rồi gửi lại
kết quả khi mạng trở lại. HTTP chỉ được gọi khi cơ cấu không bận, để không kéo
dài thời gian chạy servo. Vì vậy ACK server có thể tới sau toàn chu trình.

API:
- POST `/enqueue`: `{"id":"net-1","column":1}`.
- GET `/next`: trả `vend net-1 1`; lặp tới khi nhận được sự kiện của ID.
- POST `/events`: `{"id":"net-1","column":1,"status":"DONE"}`.
- GET `/metrics`: sốID duy nhất đã tạo, đã nhận báo cáo, có kết quả và thành công.

Các tỷ lệ là kết quả kiểm thử giao dịch local, **không phải tỷ lệ gói Wi-Fi hoặc
độ tin cậy thực của PCB**. `received_fraction` dựa trên ACCEPTED hoặc terminal
report; p95 là thời gian server quan sát được, có cả chờ cơ khí/polling. Chưa có
mẫu thì trả null, không hiển thị100%. Chưa đủ dữ liệu để tính tỷ lệ uplink độc
lập nếu không biết tổng số sự kiện ESP32 đã tạo mà server chưa nhận.

Server lưu SQLite trong `.local/server.sqlite`. ESP32 lưu tối đa16ID trong NVS,
không tự xóa ID cũ để tái sử dụng. Hết chỗ trả LEDGER_FULL. `reset` CPU không xóa
NVS. Persistence qua stop/start phiên Wokwi phụ thuộc flash snapshot/runtime;
chưa được xác minh trong môi trường này. Không coi đây là cơ sở dữ liệu giao
dịch production hoặc cơ chế bảo mật/TLS. Chỉ tạo môi trường flash/DB mới có
chủ đích khi muốn bắt đầu bộ thử mới; không xóa lịch sử để xử lý retry.

## 5. Kiểm tra và kịch bản tự động

Từ root repo:

```powershell
.\simulation\revb\check.ps1
```

Script build ESP32, kiểm tra protocol/wiring bằng Python3.11+ và chạy C++ native.
Nếu chưa có compiler native trên Windows:

```powershell
pio pkg install --global --tool platformio/toolchain-gccmingw32
```

Ba file trong `scenarios/` dành cho Wokwi CLI có token hợp lệ, chạy từ thư mục này:

```powershell
wokwi-cli --timeout 15000 --scenario scenarios/success.yaml
wokwi-cli --timeout 15000 --scenario scenarios/timeout.yaml
wokwi-cli --timeout 15000 --scenario scenarios/restart.yaml
```

Dùng một phiên flash mới có chủ đích cho mỗi kịch bản lặp, hoặc đổi ID mới;
nếu giữ NVS cũ, ID trùng phải bị chặn. Token cấu hình qua môi trường theo tài
liệu Wokwi, không dán vào file nguồn. Các YAML đã chuẩn bị nhưng chưa chạy engine.

Đóng ZIP gồm source, BIN/ELF đã build và bằng chứng kiểm tra:

```powershell
python simulation/revb/package.py
```

ZIP nằm `.local/FreshVend-RevB-simulation.zip`, có manifestSHA256 và giữ cấu trúc
thư mục. Sau giải nén mở `simulation/revb` bằng VS Code. Đây không phải gói Gerber.

## 6. Giới hạn và nguồn

Không mô phỏng XL4015/Pololu/LDO/ripple/ESD/nhiệt/RF/EMC, khả năng hàn QFN,
dòng kẹt, iris giữ1,2kg, hoặc tô rơi thật. Nguồn VIN5V trong diagram chỉ nuôi
model servo Wokwi, không thay hai rail6V của PCB. Stop1500µs và interlock phần
mềm không bảo đảm motor thật dừng/iris thật khóa nếu phần cơ hoặc nguồn lỗi.

- https://docs.wokwi.com/guides/esp32
- https://docs.wokwi.com/parts/wokwi-servo
- https://docs.wokwi.com/guides/esp32-wifi
- https://docs.wokwi.com/vscode/project-config
- https://docs.wokwi.com/wokwi-ci/automation-scenarios

Trạng thái và bằng chứng: `../../docs/project/revb-simulation-task.md`,
`../../reports/revb/verified/RevB-simulation-check.json`.
