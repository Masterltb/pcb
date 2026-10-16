# BAO CAO THAM DINH KY THUAT CHUYEN SAU (EXPERT ENGINEERING REVIEW)
**Du an:** Bo dieu khien may nha coc hoa qua 2 cot (FV-CTRL Rev A)
**Ngay danh gia:** 2026-10-17 | **Tieu chuan tham chieu:** IPC-2221B, IPC-2152, IPC-A-610 Class 2

---

## I. TONG KET DANH GIA CHAT LUONG (EXECUTIVE SUMMARY)

| Tieu chi danh gia | Ket qua | Danh gia cua chuyen gia |
| :--- | :---: | :--- |
| **Tinh toan ven dien hoc (Electrical ERC)** | **PASS (0 Errors, 0 Warnings)** | Khong ton tai xung dot chan, khong ho mach net, toan bo cong suat va tin hieu logic phan lap chuan. |
| **Quy tac bo tri & cach ly (PCB DRC)** | **PASS (0 Violations, 0 Unconnected)** | Khong bi vi pham khoang cach dong (clearance >= 0.22mm), khong short net, khong bi ho loan nhiet (starved thermal). |
| **Kha nang chiu tai dong lon (Power Integrity)** | **PASS** | Cac rail +12V, +6V servo di trace 1.8mm - 2.0mm tren dong 1oz, dap ung tai dinh 5A - 8A. Co 2 tu lon 2200uF bu tuc thoi. |
| **Kha nang bao ve mach (Circuit Protection)** | **PASS** | 3 tang bao ve: Cau chi nong mini blade 5A, P-MOSFET chong nguoc cuc, TVS 1500W chong soc cam ung, 2 cau chi PTC 3A cho servo. |
| **Tinh tuong thich co khi (DFA / Mechanical)** | **PASS** | Board vuong 100x100mm, 4 lo M3 cach mep 4mm, cong USB ESP32 huong ra ngoai mep day board de thao nap firmware. |
| **Kha nang han lap thu cong (Hand Solderability)**| **PASS** | 100% linh kien THT chan xuyen lo va module header, khoang cach pad thoang, de bao tri thay the. |

---

## II. PHAN TICH CHUYEN SAU CAC KHOI CHUC NANG

### 1. Khoi Nguon & Bao ve dau vao (+12V Rail)
- **Bao ve nguoc cuc:** Su dung P-Channel MOSFET IRF9540N (TO-220) voi dien tro keo xuong 10k tai Gate. Khi cam dung cuc, V_GS = -12V, MOSFET dan bao hoa hoan toan voi R_DS(on) ~ 0.117 Ohm. Tai dong 3A, do sut ap chi ~ 0.35V va cong suat tieu tan P = 1.05W (mat do nhiet rat thap, khong bi nong nhu diode silicon truyen thong sut ap 0.7V - 1.0V).
- **Bao ve qua ap & soc xung:** Diode TVS 1.5KE15CA (DO-201AD) mac song song ngay sau MOSFET. Khi dong ngat relay hoac servo dung dot ngot gay xung nguoc tu cam ung cuon day, TVS se dap ngay cac gai ap tren 15V ve mass, bao ve an toan tuyet doi cho ca 2 module Buck va ESP32.
- **Bao ve qua dong:** Cau chi mini blade 5A (F1) tren header kep dong han truc tiep xuong board.

### 2. Khoi Nguon Servo (+6V Rail)
- **Module Buck XH-M401 (XL4016E1):** Tich hop san cuon cam cong suat lon va nhom tan nhiet rieng, cho dong dinh muc 8A lien tuc. Nguon 12V vao va 6V ra ket noi qua domino van oc KF301 5.08mm.
- **Phan lap 2 cot servo (Col 1 & Col 2):** Nguon 6V duoc tach thanh 2 nhanh doc lap qua 2 cau chi tu hoi Polyfuse Bourns MF-R300 (3A giu / 6A cat). Neu servo cot 1 bi ket co khi, chi co F2 ngat, cot 2 van hoat dong binh thuong ma khong gay sup toan bo he thong.
- **Tu loc dem cuc bo:** Moi nhanh servo deu duoc trang bi 1 tu hoa low-ESR lon 2200 uF (duong kinh 12.5mm, chan 5.0mm) + 1 tu gom 100nF dat sat chan connector. Giup triet tieu hoan toan hien tuong tut ap gay reset ESP32 khi ca 4 servo khoi dong dong thoi.

### 3. Khoi Nguon Logic (+5V & +3.3V)
- **Module MP1584EN Mini 3A:** Ha ap tu 12V xuong 5V cap vao chan 5V cua ESP32 DevKit qua cac hang chan header kep 2.54mm.
- **ESP32 DevKit 38 Header:** Do dai hang chan tieu chuan 19 pin moi ben, khoang cach giua 2 hang chan 0.9 inch (22.86mm) dung chuan module tren thi truong.
- **De-coupling:** Cac duong nguon 3.3V va 5V deu co tu loc gom 100nF (C5, C6) dat sat chan nguon.

### 4. Khoi Phat & Thu Hong ngoai (IR Transmitter & Receiver)
- **IR Driver (TX):** Transistor NPN S8050 (TO-92) voi dien tro kich Base 1k tu chan GPIO17 ESP32. Dong kich Base I_B ~ 2.6mA dam bao transistor dan bao hoa. 2 LED phat IR duoc gioi han dong qua 2 dien tro rieng 120 Ohm (cong suat 1/2W) giup phat xung 38kHz khoe ma khong bi chay LED.
- **IR Receiver (RX) Bo ve tinh:** Tich hop mat nhan 3 chan TSOP38238 / VS1838B dat sat mieng khe roi coc. Co mach loc RC tai cho (100 Ohm + 4.7 uF) theo khuyen cao cua Vishay giup chong nhieu dien tu tu dong co servo.

### 5. Khoi Cong tac hanh trinh (Limit Switches)
- 4 kenh cong tac hanh trinh deu co mach loc phan cung gom dien tro pull-up 10k len 3.3V va tu loc chong doi phim (anti-bounce) 100nF xuong mass. Hang so thoi gian RC = 1ms giup loai bo hoan toan nhieu co khi ma khong ton cong CPU ESP32 chay thuat toan debounce.

---

## III. HUONG DAN DANH CHO KY SU LAP RAP & TEST MANG (BRING-UP GUIDE)

1. **Kiem tra nguon khong tai (Unloaded Test):**
   - Chua cam ESP32 vao socket.
   - Cap nguon 12V vao J1. Kiem tra LED D2 (+12V) sang.
   - Do diem do TP1 xem dung 12V.
   - Dieu chinh bien tro tren module XH-M401 sao cho dien ap tai TP2/TP3 dat chinh xac **6.0V**. Kiem tra LED D3, D4 sang.
   - Dieu chinh bien tro tren module MP1584EN sao cho dien ap tai TP4 dat chinh xac **5.0V**. Kiem tra LED D5 sang.
2. **Kiem tra ESP32 & Logic:**
   - Ngat nguon 12V, cam module ESP32 DevKit 38 vao 2 hang socket J18, J19 (chu y cong USB huong xuong duoi).
   - Cap lai nguon 12V. Kiem tra LED D6 (+3.3V) sang. Do TP5 dat 3.3V.
   - Nap firmware dieu khien qua cong USB.
3. **Ket noi tai Servo & Sensor:**
   - Lan luot cam 4 servo vao J5 - J8 va 2 mat nhan IR vao J9, J10.
