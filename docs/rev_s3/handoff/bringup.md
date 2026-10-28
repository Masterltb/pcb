# Bring-up mẫu Rev-S3 sau khi nhận PCB/PCBA

Áp dụng cho mẫu đã lắp đúng linh kiện bảo vệ, RECOM, tụ và đầu nối. Ghi serial PCB, firmware, tải, số đo và lỗi vào [rev-notes](../../project/rev-notes.md). Không coi checklist này là chứng nhận an toàn điện hoặc nghiệm thu production.

1. **Kiểm tra khi chưa cấp điện:** so BOM đã lắp với vị trí thật; cực tính tụ/diode/LED, chân USB-C, mối hàn U1 và lỗ được fill/cap; đảm bảo F1 có cầu chì cartridge, F2/F3 có PTC hoặc kế hoạch hàn hoàn tất. Kiểm tra không chập giữa 12 V, 6 V A/B, 5 V, 3,3 V và GND.
2. **Nguồn chính:** chưa cắm servo/cảm biến, cấp 12 V vào J1 từ nguồn giới hạn dòng. Đo TP1 → TP6 GND; quan sát dòng nghỉ và nhiệt D7/F1/J4. Nếu áp sai hoặc nóng bất thường, ngắt nguồn và tìm lỗi trước bước sau.
3. **Buck ngoài:** chỉnh riêng từng XL4015 ra 6,0 V khi chưa nối servo. Cắm từng buck qua J2/J3 đúng chiều, GND chung; đo TP2 và TP3, xác nhận hai đầu ra không nối song song.
4. **Logic:** đo TP4 khoảng 5 V, TP5 khoảng 3,3 V; kiểm tra LED nguồn. Thử lại với cảm biến dự kiến và theo dõi ripple/nhiệt J4/U3.
5. **USB và RF:** giữ nguồn 12 V, kết nối USB-C bằng cáp dữ liệu, thử nhận cổng và nạp chương trình ở cả hai chiều cắm. Gắn anten IPEX đúng loại trước khi thử Wi-Fi; ghi mức tín hiệu và độ ổn định tại vị trí lắp thực tế.
6. **Servo/cảm biến:** kiểm tra PWM từng kênh không tải rồi chạy từng servo với cơ cấu thật, có giới hạn hành trình. Đo sụt áp 6 V/12 V, nhiệt PTC/connector và xung hồi khi mở/đóng. Thử cảm biến cho từng cột với tô nhựa trong suốt có trái cây đóng gói, gồm trường hợp kẹt/hết tô.
7. **Tích hợp:** thử chu trình mở–đóng liên tục, mất điện/khởi động lại và firmware interlock. Chỉ sau mẫu mới đánh giá lại chọn PTC/cầu chì, dòng nguồn, kích thước hộp và khoảng hở tụ C1/C2 cao 25 mm.

Nguồn AC của bộ nguồn tổ ong 12 V phải có vỏ che, nối đất vỏ và bảo vệ phù hợp do người có chuyên môn điện kiểm tra trước khi vận hành máy.
