# Rev-S3 — review trước khi đồng bộ parity VBUS USB-C

Mục tiêu: giải quyết bốn cảnh báo schematic–PCB tại J21 A4/A9/B4/B9. Kiến trúc USB-C chỉ truyền dữ liệu; nguồn 12 V tại J1 cấp board khi nạp. Không đổi kiến trúc nguồn, GPIO hoặc footprint J21.

## IC/SI/PI

- Schematic để bốn chân VBUS của J21 không nối. PCB hiện gán hai net tự sinh `Net-(J21-VBUS_L)` và `Net-(J21-VBUS_R)` cho bốn pad này, trong khi không có track hoặc zone VBUS. Hai cặp pad A4/B9 và A9/B4 chồng đúng cùng tọa độ theo footprint GCT.
- Đồng bộ PCB về trạng thái không net cho đúng ý định schematic; không nối VBUS vào 12 V, 5 V hoặc 3,3 V. Không đụng D+/D−, CC1/CC2, ESD, GND hoặc đường hồi USB.
- Sau sửa chạy ERC, DRC có schematic parity và xác nhận 0 unconnected. Kiểm tra USB thực tế sau khi nhận mẫu bằng nguồn 12 V và cáp data ở cả hai chiều cắm.

## DFM/DFA

- Hình học pad USB-C, mã GCT USB4105-GF-A, paste/mask, Gerber và khoan phải giữ nguyên. Xác nhận bằng so sánh hash lớp Gerber và drill trước/sau; nếu khác thì cần review riêng.
- Không dùng cách tắt cảnh báo parity hoặc hạ DRC rule. Gói Gerber cũ được giữ để backup; nếu chỉ metadata net thay đổi và fabrication layers giống hệt, không cần thay ZIP đặt hàng.

## Kết quả

- Thử xóa net khỏi bốn pad PCB không phù hợp: hai cặp pad trùng vị trí tạo 2 lỗi clearance, parity vẫn 4. Đã hoàn tác thử nghiệm đó.
- Tạo ký hiệu J21 riêng trong `libs/fv_rev_s3.kicad_sym`, với A4/B9 thuộc `USB_VBUS_UNUSED_L` và A9/B4 thuộc `USB_VBUS_UNUSED_R`. Mỗi cặp pad đồng vị trí có cùng net; hai net không nối với nguồn hay track khác. Đồng bộ thư viện schematic tương đối và tên net của đúng bốn pad PCB.
- ERC 0 lỗi/cảnh báo; DRC 0 violation, 0 unconnected và 0 schematic parity issue. Báo cáo ở `reports/rev_s3/work/RevS3-USB-VBUS-final-erc.rpt` và `RevS3-USB-VBUS-final-drc.json`.
- `git diff` PCB chỉ thay bốn chuỗi tên net của pad J21. Không đổi tọa độ pad, copper, mask, paste, track, via, lỗ khoan hoặc outline. ZIP Gerber 0,30 mm trước đó có cùng hình học sản xuất; không cần tải lại chỉ vì sửa metadata VBUS. Chức năng USB vẫn cần thử trên board đã lắp và cấp 12 V.
