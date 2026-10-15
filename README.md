# FV-CTRL Rev A — Mạch điều khiển máy bán tô trái cây tự động

> **Nguồn sự thật duy nhất:** [`PROJECT.md`](PROJECT.md) (kiến trúc, bảng chân, ràng buộc).  
> **Quy tắc cho agent:** [`CLAUDE.md`](CLAUDE.md) (bắt buộc đọc trước khi thay đổi bất cứ thứ gì).

---

## Mục tiêu

PCB 2 lớp, **100% THT, tự hàn**, kích thước **≤ 100 × 100 mm**, điều khiển 2 cột xuất tô FIFO cho máy bán tô trái cây tự động. Thiết kế ưu tiên dễ thay thế linh kiện, dễ bảo trì, dễ chẩn đoán lỗi. Kế hoạch: **Rev A ≈ 5 tấm** → chạy thử trên máy thật → ghi lỗi → Rev B.

---

## Kiến trúc hệ thống

```
12V (nguồn tổ ong 40A)
  └─ [F1: cầu chì 5A, đế thay được]
  └─ [Q1: P-MOSFET chống ngược cực]
  └─ [D1: TVS 12V]
       ├─ Buck A (XL4015 >=5A -> 6.0V) -[PTC F2]- Servo cột 1 (TOP + BOT)
       ├─ Buck B (XL4015 >=5A -> 6.0V) -[PTC F3]- Servo cột 2 (TOP + BOT)
       └─ Buck C (5V logic)
             ├─ ESP32 DevKit 38-pin (cắm header, KHÔNG hàn)
             └─ IR TX (transistor + 2x LED IR 940nm)

ESP32 GPIOs
  ├─ GPIO 16/17 -> PWM Servo cột 1 (TOP/BOT), 330Ohm + 10k pull-down
  ├─ GPIO 18/19 -> PWM Servo cột 2 (TOP/BOT), 330Ohm + 10k pull-down
  ├─ GPIO 23    -> IR TX 38kHz (burst mode)
  ├─ GPIO 34/35 -> IR RX cột 1/2 (input only, từ board satellite)
  ├─ GPIO 25/26/27/32 -> Limit switch (tùy chọn, DNP)
  └─ GPIO 21/22 -> I2C dự phòng

Board IR satellite (x2, riêng biệt):
  TSOP38238/VS1838B + 100Ohm + 4.7uF -> JST-XH 3-pin -> mainboard
```

---

## Cấu trúc thư mục

```
pcb/
├── README.md                        <- File này
├── PROJECT.md                       <- Đặc tả kỹ thuật đầy đủ (nguồn sự thật)
├── CLAUDE.md                        <- Quy tắc bắt buộc cho agent AI
├── .gitignore
│
├── hardware/
│   ├── FV-CTRL_RevA.kicad_sch       <- [OK] Schematic KiCad 10 (ERC: 0 lỗi)
│   ├── FV-CTRL_RevA.manifest.json   <- 50 linh kiện + 27 nets (machine-readable)
│   ├── FV-CTRL_RevA.net.json        <- Netlist tương thích ngược (27 nets)
│   └── FV-CTRL_RevA.sch             <- Legacy conceptual (chỉ tham khảo)
│
├── tools/
│   ├── generate_fv_schematic.py     <- Generator tạo .kicad_sch (deterministic)
│   ├── fv_pipeline.py               <- Orchestrator: audit -> schematic -> erc
│   ├── audit_fv_project.py          <- Kiểm tra gate KiCad env / symbol / ERC
│   └── validate_fv_design.py        <- Validate cấu trúc manifest/netlist
│
├── tests/
│   └── test_code_generation.py      <- 4 tests: pipeline, schematic, manifest, ERC
│
├── docs/
│   ├── requirements-and-blockers.md <- Ma trận yêu cầu điện + 5 blocker mở
│   ├── FV-CTRL_RevA-bom-draft.md    <- BOM nháp (50 dòng)
│   ├── audit-revA.md                <- Trạng thái gate hiện tại
│   ├── FV-CTRL_RevA-schematic.pdf   <- Sơ đồ PDF (kicad-cli export)
│   └── FV-CTRL_RevA-schematic.svg/  <- Sơ đồ SVG
│
└── reports/
    ├── erc.rpt                      <- KiCad ERC report (0 errors, 0 warnings)
    └── erc.json                     <- ERC report dạng JSON
```

---

## Trạng thái hiện tại (Gate Status)

| Giai đoạn | Trạng thái | Ghi chú |
|---|---|---|
| Schematic KiCad 10 | **DRAFT READY** | 50 linh kiện, 27 nets, ERC: 0 lỗi |
| Automated tests | **PASSING** | 4/4 tests pass kể cả kicad-cli ERC |
| Symbol/Footprint | **BLOCKED** | Chờ đo kích thước module XL4015 và ESP32 |
| PCB Layout | **BLOCKED** | Chờ footprint và kích thước enclosure |
| DRC / Gerber | **BLOCKED** | Chờ PCB layout |

---

## 5 Blocker cần giải quyết trước khi layout PCB

Chi tiết: [`docs/requirements-and-blockers.md`](docs/requirements-and-blockers.md)

1. **[B1]** Khoảng cách 2 hàng header ESP32 DevKit 38-pin — đo bằng thước kẹp (0.9" hay 1.0"?)
2. **[B2]** Kích thước module XL4015 >=5A — chiều dài, rộng, vị trí lỗ vít, pitch pad IN/OUT
3. **[B3]** Kích thước module buck 5V logic (MP1584EN hoặc tương đương)
4. **[B4]** Kích thước enclosure — vị trí lỗ M3, hướng cổng USB ESP32
5. **[B5]** MPN cụ thể: cầu chì, PTC, P-MOSFET, TVS, tụ điện phân

---

## Linh kiện chính

| Linh kiện | SL | Ghi chú |
|---|---|---|
| ESP32 DevKit 38-pin | 1 | Cắm header cái, KHÔNG hàn trực tiếp |
| XL4015 module >=5A | 2 | Buck A (6V cột 1), Buck B (6V cột 2) |
| Buck 5V (MP1584EN / mini-360) | 1 | Logic, tách khỏi nhánh servo |
| MG996R 360° continuous rotation | 4 | 2 mỗi cột (TOP + BOT) |
| TSOP38238 / VS1838B | 2 | Trên board satellite IR RX |
| LED IR 940nm (TSAL6200 / IR333-A) | 2 | Mỗi LED có điện trở hạn dòng |
| S8050 / 2N2222 | 1 | Driver IR TX |
| Nguồn tổ ong 12V 40A | 1 | Ngoài board |

---

## Bảng chân ESP32 — KHÔNG thay đổi khi chưa hỏi

| Chức năng | GPIO |
|---|---|
| Servo cột 1 TOP / BOT | 16 / 17 |
| Servo cột 2 TOP / BOT | 18 / 19 |
| IR TX 38kHz | 23 |
| IR RX cột 1 / cột 2 | 34 / 35 |
| Limit switch 1–4 (DNP) | 25, 26, 27, 32 |
| I2C dự phòng SDA/SCL | 21 / 22 |
| Dự phòng | 33 |

> Tránh strapping pin: GPIO 0, 2, 12, 15.

---

## Môi trường & Công cụ

```
OS:          Windows
KiCad:       10.0.7  (kicad-cli)
Python:      3.11    (C:/Program Files/KiCad/10.0/bin/python.exe)
Freerouting: 2.5.0   (F:\programs\freerouting, cần Java 25)
```

### Lệnh hay dùng (PowerShell)

```powershell
# Tạo lại schematic từ script
python tools/generate_fv_schematic.py

# Chạy toàn bộ pipeline (audit -> schematic -> erc)
python tools/fv_pipeline.py

# Chạy ERC thủ công
kicad-cli sch erc --severity-all --output reports/erc.rpt hardware/FV-CTRL_RevA.kicad_sch

# Chạy DRC (sau khi có PCB)
kicad-cli pcb drc --output reports/drc.rpt hardware/FV-CTRL_RevA.kicad_pcb

# Xuất Gerber + drill (sau khi layout xong)
kicad-cli pcb export gerbers --output gerbers/ hardware/FV-CTRL_RevA.kicad_pcb
kicad-cli pcb export drill   --output gerbers/ hardware/FV-CTRL_RevA.kicad_pcb

# Chạy test suite
python -m pytest tests/ -v
```

---

## Quy trình thiết kế tiếp theo

```
[Hiện tại: DRAFT READY]
  1. Người dùng đo XL4015 + ESP32 + buck 5V      -> Giải quyết Blocker B1-B3
  2. Tạo footprint .kicad_mod cho 3 module        -> tools/ hoặc libs/
  3. Gán footprint vào .kicad_sch                 -> hardware/*.kicad_sch
  4. Init .kicad_pcb, board outline 100x100mm     -> hardware/*.kicad_pcb
  5. Đặt linh kiện (nguồn/servo cạnh board, MCU giữa)
  6. Đi dây tay: trace 12V/6V >=2mm, GND copper pour
  7. DRC sạch -> người dùng duyệt -> xuất Gerber/BOM/drill -> docs/
  8. Đặt in 5 tấm Rev A, bring-up theo checklist
```

---

## Lưu ý quan trọng cho agent

- **Đọc `PROJECT.md` và `CLAUDE.md` trước** mỗi phiên làm việc.
- **Không thay đổi bảng chân ESP32** hoặc kiến trúc nguồn khi chưa hỏi người dùng.
- **Không tạo footprint giả** cho XL4015/ESP32 khi chưa có số đo thực tế.
- Sau mỗi lần sửa schematic → chạy ERC và báo cáo kết quả trước khi tiếp tục.
- IR TX phải dùng **burst mode** (~1ms on/off), KHÔNG phát 38kHz liên tục.
- Phần lưới AC của nguồn tổ ong: **ngoài phạm vi** dự án này.
- Nếu `PROJECT.md` còn `TODO(user)` chặn bước hiện tại → dừng và hỏi người dùng.

---

## Liên kết nhanh

| Tài liệu | Mô tả |
|---|---|
| [PROJECT.md](PROJECT.md) | Đặc tả kỹ thuật đầy đủ |
| [CLAUDE.md](CLAUDE.md) | Quy tắc bắt buộc cho agent |
| [docs/requirements-and-blockers.md](docs/requirements-and-blockers.md) | Ma trận yêu cầu + 5 blocker |
| [docs/FV-CTRL_RevA-bom-draft.md](docs/FV-CTRL_RevA-bom-draft.md) | BOM nháp 50 linh kiện |
| [docs/audit-revA.md](docs/audit-revA.md) | Gate status |
| [hardware/FV-CTRL_RevA.kicad_sch](hardware/FV-CTRL_RevA.kicad_sch) | Schematic KiCad 10 |
| [hardware/FV-CTRL_RevA.manifest.json](hardware/FV-CTRL_RevA.manifest.json) | Manifest linh kiện + nets |
| [reports/erc.rpt](reports/erc.rpt) | ERC report mới nhất |
