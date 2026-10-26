# Quy ước cấu trúc repository

- `hardware/revb/` là nguồn RevB hiện hành; `hardware/reva2/` là bản tham khảo, `hardware/archive/reva/` giữ lịch sử RevA. Không đổi tên file sheet con hoặc tách chúng khỏi schematic gốc.
- `libs/` dùng chung. Mỗi project có bảng thư viện riêng với đường dẫn tương đối về `libs/`.
- `docs/revb/bom/`, `assembly/`, `schematic/` lần lượt chứa linh kiện, lắp ráp và bản đọc schematic. Tài liệu review để ngay trong `docs/revb/`.
- `reports/revb/verified/` chỉ chứa kết quả xác minh hiện hành. Log, checkpoint PCB, DSN/SES và ảnh debug để `reports/revb/work/`, được bỏ qua bởi Git. Báo cáo trung gian đã được theo dõi trước đây nằm trong `history/`.
- `releases/revb/` giữ ZIP review hiện hành, ZIP Gerber/handoff mẫu có ngày và manifest. Gói mẫu đầu tiên được xuất ngày 2026-10-26; chưa có nghiệm thu sản xuất. Bản cũ, Gerber/handover lịch sử nằm `releases/archive/`; không coi đó là Gerber của RevB.
- Giữ dữ liệu và các sửa đổi cục bộ; không xóa bản cũ để làm sạch thư mục. Trong đợt sắp xếp, nội dung 18 file dirty có sẵn được kiểm tra SHA256 trước/sau. Các sửa đổi đó tiếp tục ở trạng thái chưa commit tại đường dẫn archive tương ứng.
- Không chạy generator để kiểm tra việc đổi thư mục. Dùng ERC/DRC, verifier, đối chiếu đường dẫn thư viện, kiểm tra checksum và kiểm tra ZIP sau giải nén.

Đợt này chỉ đổi vị trí file, đường dẫn công cụ, bảng thư viện và tài liệu hướng dẫn; không đổi GPIO, net, linh kiện hoặc hình học copper của RevB. ZIP được tạo lại theo cấu trúc mới. Việc sắp xếp không đồng nghĩa duyệt sản xuất hoặc phát hành Gerber.
