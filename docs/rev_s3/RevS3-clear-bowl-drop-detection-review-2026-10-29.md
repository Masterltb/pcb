# Rev-S3 — nhận biết tô trong suốt đã rơi và không kẹt (2026-10-29)

## Dữ liệu đã xác nhận

- Bản vẽ `banve.paint` mô tả tủ hai cột; 80 cm và 60 cm là **kích thước tủ**, không phải hành trình rơi của từng tô. Chưa có cao độ cửa giữ, cửa ra và bề rộng lọt lòng từng ống.
- Tô PET/PP trong suốt, miệng khoảng 17 cm, cao 6 cm, khoảng 300 g khi đầy (PROJECT.md). Phải thử bằng đúng tô thực tế, cả khi có nước/ánh sáng nền/bụi.
- Người dùng sửa cơ chế servo: MG996R đưa cơ cấu đến vị trí mở và quay ngược về vị trí đóng; không giả định điều khiển quay liên tục 360° theo thời gian.
- Cần kiểm tra nhãn/servo thật: MG996R chuẩn thường điều khiển theo vị trí trong hành trình giới hạn; bản đã sửa để quay liên tục chỉ điều khiển chiều/tốc độ và cần công tắc hành trình hoặc phản hồi khác để xác nhận vị trí đóng/mở.
- PCB Rev-S3 hiện có J11/J12, mỗi đầu 5 V, TRIG chung, **một ngõ SENSE riêng** qua chia áp 5 V → khoảng 3,3 V. Không có sẵn bốn ngõ cảm biến rơi độc lập trên hai đầu này.

## Đề xuất theo độ tin cậy

1. Mỗi cột đặt cảm biến **A ngay dưới cơ cấu nhả** và cảm biến **B tại cửa ra/khay nhận**. Lắp ngang theo bề rộng của máng, không chiếu dọc 60–80 cm của tủ. Vị trí cuối cần tránh để các tô khác hoặc tay người đi qua tia.
2. Vì tô trong suốt, dùng cảm biến quang **chuyên phát hiện vật trong suốt** hoặc cơ cấu xác nhận cơ học tại cửa ra. Ví dụ họ Omron E3Z-B có bản NPN 12–24 V cho chai nhựa trong; đây chỉ là ứng viên để thử, không cắm trực tiếp vào J11/J12 5 V. Cần mạch giao tiếp bảo vệ/đổi mức và nguồn riêng theo datasheet.
3. Logic mỗi lần xuất: xác nhận A/B ban đầu thông; mở cơ cấu; thấy A tác động; sau đó B tác động trong cửa sổ thời gian đo thực tế; A rồi B nhả trở lại. Chỉ báo thành công sau chuỗi này. A bị chắn lâu hoặc B không tác động trước timeout → đóng cơ cấu về trạng thái an toàn, dừng cột và báo kẹt/chưa rơi. Nếu A không tác động, chưa thể phân biệt hết tô với kẹt ở phía trên nếu không thêm cảm biến tồn kho.
4. Phương án thử chi phí thấp: mỗi cột dùng một cảm biến tại cửa ra trên J11/J12, canh tia qua gờ/vành tô và kiểm tra `chắn → thông` với timeout. Phương án này chỉ xác nhận đã đi qua một mặt cắt; **không đủ** để khẳng định toàn bộ đường rơi không kẹt. Phải test tỷ lệ bỏ sót với tô trong suốt trước khi dùng vận hành.

## Phương án cơ khí chi phí thấp để thử mẫu

- Ưu tiên **một cánh gạt rất nhẹ tại cửa ra của mỗi cột**, cánh gạt tác động công tắc hành trình micro-load, ví dụ Omron D2F-01L. Tô chỉ chạm cánh gạt; công tắc nằm ngoài đường rơi để tránh bụi và tác động trực tiếp. Cánh gạt phải tự trở về, không cản tô rỗng nhẹ nhất và dễ vệ sinh.
- Board hiện tại có thể thử với **một công tắc NO mỗi cột**: nối J11/J12 chân 1 (+5 V) qua tiếp điểm NO sang chân 3 (SENSE). Chân 2 TRIG không dùng. R16/R18 = 1 kΩ và R17/R19 = 2 kΩ trên PCB tạo khoảng 3,33 V ở GPIO khi công tắc đóng, 0 V khi mở; dòng qua tiếp điểm khoảng 1,67 mA. Chỉ sử dụng công tắc được hãng cho phép ở tải tín hiệu thấp; D2F-01L có mức tối thiểu tham khảo 5 V/1 mA. Cần debounce và kiểm tra nhiễu/cáp thật.
- Tín hiệu `mở → đóng → mở` tại cửa ra xác nhận tô đã chạm cánh gạt rồi đi qua. Nếu không tác động trong timeout hoặc kẹt ở trạng thái đóng, báo lỗi. Một công tắc không chứng minh được tô không kẹt **phía trên** điểm đặt; hai điểm/cột vẫn là cấu hình đầy đủ, cần thêm hai ngõ vào.

Nguồn công tắc: https://components.omron.com/sites/default/files/datasheet_pdf/B036-E1.pdf ; https://components.omron.com/us-en/faq/switches/FAQE20012

## Ảnh hưởng đến board hiện tại

- Hai cảm biến tổng cộng (mỗi cột một) có thể dùng J11/J12 nếu là loại 5 V, tín hiệu số 0–5 V và dòng tiêu thụ nằm trong ngân sách nguồn 5 V; pin 1 = +5 V, pin 2 = TRIG, pin 3 = SENSE, pin 4 = GND. Đối chiếu đúng model trước khi đấu.
- Bốn cảm biến tổng cộng cần **hai ngõ vào độc lập bổ sung** và dây/đầu nối thích hợp. Có thể xem xét module I²C ở J9 hoặc sửa Rev-S3 sau khi duyệt GPIO/kiến trúc; không nối hai ngõ ra chung vào một chân. Cảm biến công nghiệp 12–24 V NPN/PNP cần interface riêng, không đưa điện áp đó vào chân J11/J12.
- Trước khi chốt linh kiện, đo khoảng cách ngang thực giữa hai vách ống, cao độ cơ cấu nhả/cửa ra, thời gian rơi tối thiểu/tối đa của tô thật và điều kiện ánh sáng/bẩn. 80 × 60 cm của tủ không tự quyết định tầm quét cảm biến.

Nguồn tham khảo: https://www.ia.omron.com/products/family/3919/specification.html ; https://www.bannerengineering.com/us/en/company/expert-insights/benefits-polarized-coaxial-optics-clear-object-detection.html ; https://towerpro.com.tw/product/mg995-robot-servo-180-rotation/
