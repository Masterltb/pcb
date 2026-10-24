# RevB — khảo sát linh kiện và giá để giảm chi phí

Ngày tra cứu: 2026-10-24. Trạng thái: RESEARCH, chưa thay BOM/PCB, chưa đặt hàng. Giá là niêm yết hoặc snapshot tìm kiếm của bên bán, không phải RFQ xác nhận. Giá LCSC không đồng nghĩa giá linh kiện được lắp tại JLCPCB.

## Phạm vi và quyết định

Giữ ESP32 chip rời, anten SMA, hai XL4015/rail 6 V độc lập và toàn bộ bảo vệ. Ưu tiên giảm chi phí nguồn 5 V và đầu nối. Không dùng linh kiện thay thế vào file hiện hành khi chưa review IC/SI/PI và DFM/DFA, xác nhận bản vẽ, rồi ERC/DRC.

Quy đổi minh họa 26.000 VND/USD là giả định tính ngân sách, không phải tỷ giá ngân hàng đã xác minh. Chưa gồm phí vận chuyển, thuế nhập khẩu, phí đổi ngoại tệ, PCBA, X-ray, MOQ/hao hụt. VAT nội địa chỉ tính theo mô tả cụ thể bên bán.

## Nguồn và đầu nối — ứng viên thay thế

| Vị trí / nhu cầu | Sản phẩm | SL/máy | Giá đơn vị quan sát | Link mua | Mức sẵn sàng |
|---|---|---:|---:|---|---|
| J4 hiện hành, mốc so sánh | Pololu D24V25F5 #2850 | 1 | USD25,95 mua1; USD23,87 mua5 | https://www.pololu.com/product/2850 | Đúng BOM; khoảng674.700đ/cái mua1, chưa ship |
| J4 phương án hãng | RECOM R-78E5.0-1.0, 5V/1A | 1 | USD4,46 mua1 tại RS US | https://us.rs-online.com/product/recom-power-inc-/r-78e5-0-1-0/71896956/ | Khoảng115.960đ; khác pinout/footprint Pololu; cần budget tải và derating/nhiễu trước khi chốt |
| J4 phương án mẫu giá thấp | MP1584EN module cố định5V, Đức Huy K1_55 | 1 | 14.000đ | https://dientuduchuy.com/products/mp1584en-mach-ha-ap-giam-ap-dc-5v-dc-3a-khong-dieu-chinh-dien-ap | Không có bản vẽ tọa độ chân xác nhận; không cắm trực tiếp footprint cũ. Nhãn3A không phải nghiệm thu module |
| J4 phương án dự phòng | MP1584EN chỉnh áp, CXT A060202 | 1 | 16.000đ mua1;15.000đ mua5 | https://linhkien.cxtvn.com/1734-module-nguon-mp1584.html | Phải chỉnh5V trước nối tải; bản vẽ/footprint cần xác nhận; ưu tiên cố định5V cho máy vận hành |
| J1 ứng viên | KF2EDG5.08 2P, DKE mã2189 | 1 | 3.240đ gồmVAT theo trang;3.000đ chưaVAT | https://dke.vn/connector/domino/domino-5.08-kf2edg-2p | Chưa xác nhận giá gồm cả plug/header; cần drawing, hướng cắm, lỗ khoan, chất lượng dòng tiếp điểm |
| J2/J3 ứng viên | KF2EDG5.08 4P, DKE mã2191 | 2 | 5.400đ/bộ gồmVAT;5.000đ chưaVAT | https://dke.vn/connector/domino/domino-5.08-kf2edg-4p | Trang mô tả gồm đầu đực+đầu cái. Cùng pitch không chứng minh tương thích Phoenix; cần đối chiếu drawing và thử mẫu |
| Buck servo ngoài, giữ kiến trúc | XL4015 module, Chipstack | 2 | 30.000đ/cái | https://chipstack.vn/san-pham/module-nguon-dc-dc-dieu-chinh-dien-ap-5a-xl4015/ | Chỉnh từng module6V; thử tải/khởi động/kẹt/nhiệt. Không lấy5A quảng cáo làm dòng liên tục được xác nhận |

Không hàn dây trực tiếp lên mainboard. Nếu chọn module gá ngoài phải có đầu nối tháo rời; nếu chọn cắm board phải có pinout/bản vẽ chính xác và chân/header phù hợp. MP1584 module chỉ là ứng viên làm mẫu, chưa là thay thế đạt production.

RECOM có tài liệu hãng/kích thước và nguồn cung rõ hơn module OEM, nên ưu tiên khảo sát phương án này nếu budget logic phù hợp1A. Nó không cấp servo. Trước chốt cần xác nhận Vin khi có xung12V, tải5V gồm LDO+IR+USB và nhiệt hộp, response tải/nhiễu. Datasheet hãng: https://recom-power.com/en/products/switching-regulators/switching-regulators-sip/rec-p-R-78E5.0-1.0.html .

MP1584 IC hãng: https://www.monolithicpower.com/en/products/power-management/switching-converters-controllers/step-down-buck/converters/mp1584.html . Thông số IC không chứng minh chất lượng module OEM. MPS có đề xuất họ IC khác cho thiết kế mới; không chọn MP1584 IC làm thiết kế nguồn tích hợp mới chỉ vì module rẻ.

## IC đang dùng — nguồn cung để giữ thiết kế

| Ref | MPN / mã mua | Giá tham khảo mua lẻ | Link | Lưu ý |
|---|---|---:|---|---|
| U1 | ESP32-D0WD-V3 / C967021 | USD2,7775 ~72.215đ | https://www.lcsc.com/product-detail/C967021.html | Giá từ snapshot tìm kiếm; trang trực tiếp không xuất lại bảng giá trong lượt này; kiểm giỏ trước mua. Đúng QFN48 5x5, không mua WROOM/DevKit |
| U2 | CP2102N-A02-GQFN24R / C969151 | USD1,991 ~51.766đ | https://www.lcsc.com/product-detail/USB-ICs_SKYWORKS-SILICON-LABS-CP2102N-A02-GQFN24R_C969151.html | Bảng giá/stock hiển thị trực tiếp; hậu tốR đóng cuộn so với BOM khôngR: đối chiếu ordering hãng và chấp thuận MPN trước đổi BOM; cùng chức năng/package theo datasheet |
| U2 đúng MPN BOM | CP2102N-A02-GQFN24 / C1550551 | Snapshot USD2,5853; chưa chốt | https://www.lcsc.com/product-detail/C1550551.html | Snapshot ghi hết hàng; không coi đây là nguồn có sẵn để lên lịch |
| U3 | LD1117V33 / C283467 | USD0,4927 ~12.810đ | https://www.lcsc.com/product-detail/C283467.html | Giá snapshot; TO220 đúng BOM, giữ giá trị và kiểm nhiệt thực |
| U4 | W25Q32JVSSIQ / C179173 | Cần xác nhận giá hiện tại | https://www.lcsc.com/product-detail/C179173.html | Có giá indexed cũ nhưng không dùng làm báo giá; không thay SOIC208mil bằng SOP hẹp |
| U5 | TLV803EA30DBZR / C5218924 | Cần xác nhận | https://www.lcsc.com/product-detail/C5218924.html | Không đổi biến thể pinout hoặc threshold/delay để mua rẻ |

CP2102N ordering/datasheet: https://www.silabs.com/documents/public/data-sheets/cp2102n-datasheet.pdf . Không suy từ chữR sang thay đổi pinout; đối chiếu đúng mã A02/GQFN24.

## Mức giảm có cơ sở

- Mua1: Pololu25,95USD → RECOM4,46USD: giảm21,49USD ~558.740đ/board, trước ship/thuế và chi phí sửa.
- Mua5: Pololu23,87USD/cái → giả sử RECOM vẫn4,46USD/cái: giảm ~504.660đ/board, ~2.523.300đ/5board.
- Pololu mua1 → module14.000đ: giảm tiền linh kiện khoảng660.700đ/board; chưa tính gá/đầu nối/sửaPCB/thử tải. Không cam kết rẻ hơn về tổng chi phí phát triển nếu phải sửa lại.
- Chưa tính mức giảm đầu nối vì chưa có giá Phoenix hiện tại và chưa chốt giá đủ cặp2P; không tự dựng baseline.

## Những khoản chưa có báo giá đầy đủ

Chưa chốt cả149 reference: RF0201/crystal/SMA/USB, TVS/MOSFET/PTC/cầu chì, tụ điện phân, JST/header/dây, điện trở/tụ nhỏ và công lắp. Giữ các MPN bảo vệ hiện hành cho tới khi có thay thế được đối chiếu. Không cộng các dòng đã có giá thành giá toàn mainboard. Khoản3–6triệu/board nói trước chỉ là dự trù tổng làm một mẫu, chưa được xác nhận bằng RFQ.

Tách yêu cầu mua mẫu: 1–2nguồn5V/loại, 1bộconnector2P+2bộ4P, 2XL4015. Chưa mua hộ hoặc gửi file cho nhà cung cấp. Báo giá SMT phải chốt riêng tại JLCPCB với BOM/CPL/DFM đã duyệt; giá lẻLCSC không phải giá lắpJLCPCB.

## Trạng thái task

- DONE: tra nguồn5V/connector giá thấp, link giá, kiểm tác động thay thế và phân biệt giá xác minh/snapshot/chưa có.
- DONE: đối chiếu IC cốt lõi với BOM hiện hành, ghi nguồn thay đóng góiCP2102N có điều kiện.
- OPEN: xác nhận báo giá đủBOM149reference, giỏhàng/stock/ship/thuế, drawingconnectorOEM và thử mẫu5V, báo giáPCBA.
- NOT IMPLEMENTED: không sửa schematic/layout/GPIO/kiến trúc, không xuấtGerber, không nghiệm thu linh kiện thay.
