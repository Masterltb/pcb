# RevB — review trước thay nguồn 5V sang RECOM

Ngày 2026-10-25. Người dùng đồng ý kiểm chứng RECOM thay Pololu và giữ đầu nối
Phoenix tới khi có đủ dữ liệu. Không đổi GPIO, hai XL4015 hoặc kiến trúc rail.

## JaeBin — IC / SI / PI

Chọn R-78E5.0-1.0 (không phải bản0,5A): 12V vào,5V/1A ra. Datasheet9/2024
xác nhận Vin8–28V, tải tụ tối đa220µF, ripple tối đa120mVpp với100nF ngõ ra,
độ chính xác đầu ra±5% max. Đường derating giữ100% tải tới60°C, còn60% ở85°C.
Các số này là giới hạn tài liệu, không phải phép đo RevB.

Budget bảo thủ theo giới hạn LDO: 0,800A tải3V3 + 0,010A dự phòng dòng riêngLDO
+ 2×(5,25−1,0)/114A LEDIR (hai nhánh120Ω−5%, bỏ qua VCE để tính cao)
+ (5,25−1,5)/1425A LED5V = 0,8872A ngõ5V. Điện ápVF1V/1,5V là giả định
budget bảo thủ cần đối chiếu LED nhận được; không thay dòng thực/datasheetLED.
Servo không lấy nguồn5V. Không cấp thêm tải ngoài khiến LDO vượt định mức hoặc
nguồn5V vượt budget. Ở gần85°C không còn đủ dòng; mục tiêu thử mẫu0…50°C
ambient gần module và phải đo điểm nóng. Không tuyên bố đạt nhiệt hộp.

Tụ5V C5+C11=20µF, cộng100nF mới và tổng tụ3V3 hiện hữu (khoảng60µF) vẫn thấp
hơn220µF về tổng danh định; phải thử khởi động/inrush qua LDO, không suy nghiệm
thu từ phép cộng. Bổ sung10µF đầu12V gầnmodule vì nhiều buck dùng chung rail,
và100nF đầu5V. GiữLDO3V3 và tụ10µF vào/ra; tối thiểu5V dựa riêng±5% là4,75V,
còn phải đo ripple, sụt áp và dropout khi Wi-Fi phát. TVS12V không bảo vệ6V;
đo overshoot/hotplug Vin để không vượt giới hạn module. Datasheet yêu cầu chú ý
soft-start đầu vào; nguồn12V thật chưa được xác nhận đáp ứng.

Không thêm filterEMC rồi tuyên bố đạt chuẩn. Nguồn rẻ vẫn cần đoRF/nhiệt/xung
và kiểm tra flashbrownout. Module mới chỉ đủ cơ sở thiết kế mẫu có điều kiện.

## Jbungia — DFM / DFA

Bản vẽ trang4: body11,6×8,5×10,4mm;3pin thẳng bước2,54mm,1VIN/2GND/3VOUT;
chân rộng0,70(+0,10/−0,05)mm,dày0,25±0,05mm. Chọn lỗ hoàn thiện1,0mm theo
footprintKiCad cùng envelope; kiểm mẫu thật trước lắp. Footprint dùng tọa độ
hãng, không lấy từ ảnh. Dùng model envelopeKiCad R-78E0,5 cùng kích thước làm
minh họa, không coi là chứng minh thông số điện hoặc nhãn sản phẩm1A.

Lắp3chânTHT trực tiếp, có thể tháo hàn để bảo trì; không cắm vào socketPololu
cũ hoặc socket bất kỳ chưa kiểm kích thước. J4 là bộ chuyển đổi gắn trênboard,
không phải điểm hàn dây ngoài. Giữ toàn bộ đầu nối ngoài và bảo vệ.

Thay riêng vùngJ4, thêm hai tụ ở vùng trống do bỏmodulePololu lớn. Không sửa
RF/crystal hoặc autoroute toànboard. ERC/DRC/parity sau từng bước; chưaGerber.

## Nguồn hãng

https://g.recomcdn.com/media/Datasheet/pdf/.ft_PFiEZ/.tac185dad0176a7816122/Datasheet-274/R-78E-1_0.pdf

https://www.st.com/resource/en/datasheet/ld1117.pdf

## Kế hoạch / bằng chứng

- [x] Kiểm bản vẽ hãng, review hai góc trước thay.
- [ ] Cập nhật symbol/footprint/spec; ERC và DRC/parity ghi rõ bước trung gian.
- [ ] Đổi J4 và đi lại cục bộ, thêm tụ; kiểm tra cuối sạch.
- [ ] Đồng bộ BOM/hình/ZIPreview/trạng thái; commit/push.
- [ ] Mẫu thật: Vin/inrush/rail5V tải tới0,9A/ripple/thermal/USB/Wi-Fi/IR.

Hai góc review nội bộ, không phải chứng nhận độc lập. Chưa mua hoặc gửi xưởng.
