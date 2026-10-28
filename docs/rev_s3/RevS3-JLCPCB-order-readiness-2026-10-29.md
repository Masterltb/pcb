# Rev-S3 — kiểm tra trước khi đặt PCB/PCBA tại JLCPCB (2026-10-29)

**Trạng thái: CHƯA ĐƯỢC TẢI GÓI CŨ LÊN JLCPCB.** Người dùng chọn JLCPCB lắp cả SMT và THT. Đây là review cho mẫu thử, chưa nghiệm thu production.

## Nguồn thiết kế và kiểm tra trên file

- PCB/schematic hiện tại ở `hardware/rev_s3/`, HEAD lúc review `238401d`.
- ERC 0 lỗi/cảnh báo; DRC 0 violation/0 unconnected; parity còn 4 cảnh báo tại VBUS J21. Xem `reports/rev_s3/RevS3-after-holes-{erc.rpt,drc.json}`.
- Board 100 × 100 mm, 2 lớp, đồng danh định 1 oz, bề rộng track nhỏ nhất 0,15 mm. JLCPCB công bố năng lực 1 oz 0,10/0,10 mm, nhưng điều này không xác nhận dòng tải, nhiệt, USB hoặc lắp linh kiện thực tế: https://jlcpcb.com/capabilities/pcb-capabilities/
- `releases/rev_s3/FV-CTRL_RevS3-Gerber.zip` và manifest là gói từ commit `5c4371f`, trước các sửa đường nguồn ở `f676345`, `d76042f`, `238401d`. Không dùng gói này cho đơn hàng.

## Chặn đơn PCBA đầy đủ

1. **J21 không khớp BOM–footprint.** PCB dùng `Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal`; BOM cũ chọn HRO `TYPE-C-31-M-12`, C165948. KiCad 10 cho thấy pad GCT lệch khoảng 0,36 mm theo Y so với footprint HRO và độ dài pad khác 0,30 mm. Không được tự thay hai đầu nối này. Khuyến nghị chọn GCT `USB4105-GF-A`, C3020560, đúng họ footprint; xác nhận availability và biến thể cơ khí khi chọn linh kiện trong JLCPCB. https://jlcpcb.com/partdetail/3542626-USB4105_GFA/C3020560 và https://gct.co/files/drawings/usb4105.pdf
2. **BOM/CPL release chỉ gồm 39 SMT.** JLCPCB chỉ lắp những linh kiện được chọn trong bước match. Đơn đầy đủ phải có cả THT trong BOM và tọa độ/rotation lắp ráp được JLCPCB chấp nhận. https://jlcpcb.com/help/article/pcb-assembly-faqs và https://jlcpcb.com/help/article/component-matching-guidelines-for-pcba-orders
3. **Nhiều C-code THT trong engineering BOM cũ sai.** `F2/F3` C514332 thực ra là cảm biến ADIS16209CCCZ, không phải PTC; `J11/J12` C157930 thực ra là JST ZH 2 chân 1,5 mm, không phải XH 4 chân 2,5 mm. `J2/J3` C8446 là terminal block Ningbo, không phải Phoenix ghi trong BOM; chưa xác nhận kích thước/mating có thay được. Các mã C2902347 (J4), C2911299 (F1) chưa được đối chiếu như BOM ghi. Không nạp các mã này vào đơn PCBA.
4. **Ứng viên đúng đã tìm thấy:** Schurter `0031.8201` C3204125 cho F1; JST `B4B-XH-A` C41422491 cho J11/J12; RECOM `R-78E5.0-1.0` C3033024 cho J4, nhưng trang JLCPCB báo hết hàng khi review. Cần đối chiếu bản vẽ footprint và tình trạng kho tại lúc đặt. https://jlcpcb.com/partdetail/SCHURTER-00318201/C3204125 ; https://jlcpcb.com/partdetail/JST-B4B_XHA/C41422491 ; https://jlcpcb.com/partdetail/RecomPower-R_78E5_0_10/C3033024
5. **Chưa khóa tất cả THT còn lại:** tụ C1/C2/C57, PTC F2/F3, Phoenix J1/J2/J3 và header 4 chân J9/J10 cần MPN/C-code đúng, bản vẽ hãng và xác nhận JLCPCB nhận lắp. Thiếu hàng có thể cần pre-order, global sourcing hoặc consignment; không tự thay giá trị/footprint. https://jlcpcb.com/help/article/pcba-parts-sourcing-instruction
6. **Cầu chì và PTC cần chốt giá trị riêng.** C3204125 là *đế cầu chì* 5 × 20 mm; phải chọn thêm cầu chì 5 A đúng loại và xác nhận JLCPCB có lắp cầu chì vào đế không. Bourns MF-RHT300 có `Ihold = 3,0 A` tại 23 °C, trong khi tên giá trị trên PCB ghi `PTC 2.5A`; cần duyệt dòng giữ/trip theo tải servo và nhiệt môi trường. https://jlcpcb.com/partdetail/SCHURTER-00318201/C3204125 ; https://www.bourns.com/docs/product-datasheets/mf-rht.pdf

## Gate cuối trước khi xuất file fabrication mới

- IC/SI/PI: đo hoặc xác nhận dòng đỉnh hai servo, sụt áp đường dương và GND, nhiệt D7/F1/F2/F3/J4/U3, ripple 6 V/5 V/3,3 V; kiểm tra USB D+/D−/ESD và anten IPEX trên mẫu. Các phép tính đường đồng trong `RevS3-prechange-risk-review-2026-10-29.md` chưa thay thế đo tải.
- DFM/DFA: khóa MPN theo footprint, hướng cắm connector, cực tính tụ/diode/LED, vùng mép PCB của J21, vị trí mô-đun/cáp anten; xác nhận JLCPCB review 2D/3D và tất cả linh kiện được chọn trong BOM match.
- Sau khi sửa BOM/CPL và chốt linh kiện, chạy lại ERC/DRC/parity, trình rủi ro layout cuối cho người dùng duyệt; sau duyệt mới xuất Gerber/drill từ HEAD, kiểm tra ZIP bằng Gerber viewer, so BOM/CPL với PCB và tải lên/đặt hàng theo yêu cầu.

## Thông số đặt mẫu đề xuất sau khi các gate đạt

- PCB 100 × 100 mm, 2 lớp FR-4, 1,6 mm, 1 oz; số lượng mẫu 5 tấm (giá thực tế xem tại checkout).
- Chọn PCBA hai công nghệ SMT + THT, lắp mặt trên theo BOM/CPL hoàn chỉnh. JLCPCB hỗ trợ mixed assembly nhưng chỉ lắp linh kiện được chọn tại bước match.
- Trên preview: kiểm tra outline, lỗ khoan PTH/NPTH, top/bottom, USB-C ở mép, chiều J1/J2/J3, cực tính C1/C2/C57 và D1/D7, vị trí tất cả THT; giữ ảnh/quote để đối chiếu. Không thanh toán trước khi preview và parts match được xác nhận.
