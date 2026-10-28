# FreshVend Vending Controller — Rev-S3 Design & Fabrication Manual

**Board Revision:** FV-CTRL Rev-S3  
**Target MCU:** ESP32-S3-WROOM-1U-N8 (Dual-Core 240MHz Xtensa, 8MB Flash, 512KB SRAM, IPEX MHF1 Antenna)  
**Native Interface:** USB Type-C 16-Pin (Native USB-Serial-JTAG CDC on GPIO19/20)  
**Drop Sensing:** Dual Universal 4-Pin Headers (J11 & J12: SW-420 Vibration / HC-SR04 Ultrasonic / IR Beam)  
**Form Factor:** 100 mm × 100 mm 2-Layer PCB (JLCPCB Standard DFM, 0 ERC / 0 DRC / 0 Unconnected)  
**Author:** AI Pair Engineer & FreshVend Hardware Team  
**Date:** October 28, 2026  

---

## 1. Executive Summary & Cost Comparison

Revision S3 (**Rev-S3**) represents a major architectural upgrade over Rev-B. By moving to the **ESP32-S3-WROOM-1U** module, the board achieves:

1. **Massive Component Elimination:**
   - Eliminated CP2102N USB-UART bridge IC, its QFN-24 footprint, and 0402 passives.
   - Eliminated external 40MHz crystal ($Y_1$) and load capacitors ($C_{24}, C_{25}$).
   - Eliminated external SPI flash IC ($U_4$, W25Q32) and its 6 high-speed tracks.
   - Eliminated discrete auto-download BJT circuitry ($Q_3, Q_4$).
   - Eliminated discrete RF $\pi$-matching inductors and ceramic capacitors ($L_1, L_2, C_{30}, C_{31}$).
   - Replaced old Micro-USB connector with modern, durable **USB Type-C 16-Pin**.

2. **Cost Optimization Matrix:**
   | Component / Cost Factor | Rev-B (Discrete ESP32-D0WD) | Rev-S3 (ESP32-S3-WROOM-1U) | Savings / Benefits |
   |---|---|---|---|
   | MCU Core | ESP32-D0WD-V3 ($1.20) | ESP32-S3-WROOM-1U-N8 ($1.85) | Pre-certified FCC/CE module, IPEX connector, 8MB Flash integrated |
   | USB Bridge | CP2102N-A02-GQFN24 ($1.30) | **$0.00 (Native USB)** | **Saved $1.30** |
   | SPI Flash | W25Q32JVSSIQ ($0.38) | **$0.00 (Integrated 8MB)** | **Saved $0.38** (Double capacity: 4MB -> 8MB) |
   | 40MHz Crystal | ABM8-40.000MHz ($0.25) | **$0.00 (Integrated)** | **Saved $0.25** |
   | Auto-reset BJTs & Diodes | 2x MMBT3904 + passives ($0.15) | **$0.00 (Native USB)** | **Saved $0.15** |
   | Passives & RF Match | 12x 0402/0201 passives ($0.18) | **$0.00 (Integrated)** | **Saved $0.18** |
   | JLCPCB SMT Placement Fee | 63 SMT parts (~$5.50 setup/feed) | **39 SMT parts (~$3.10)** | **Saved ~$2.40 per board** |
   | **Total Estimated Savings** | Baseline | **~-$3.00 to -$4.00 / board** | **Greater reliability, lower part count, faster assembly** |

---

## 2. Universal 4-Pin Drop Sensor Interface (J11 & J12)

The board provides two dedicated 4-pin JST-XH headers (`J11` for Column 1, `J12` for Column 2). Each header supplies **Pin 1: +5V, Pin 2: TRIGGER / GPIO21, Pin 3: SENSE / ECHO (with 1k/2k voltage divider to 3.3V), Pin 4: GND**.

### Compatible Sensor Types & Wiring

```
   JST-XH Header (J11 / J12)
  ┌───────────────┐
  │ [1] +5V       │ ───> VCC (Sensor Power)
  │ [2] TRIG      │ ───> Trigger Input (HC-SR04 TRIG / Optional LED / Sync)
  │ [3] SENSE/ECHO│ <─── Digital Output / ECHO (Protected by onboard 1k/2k divider: 5V -> 3.3V)
  │ [4] GND       │ ───> GND (Ground Return)
  └───────────────┘
```

#### Sensor Option A: SW-420 Vibration Sensor (Cảm Biến Rung Chấn Tô Rơi)
- **Concept:** Installed directly on the bowl collection tray / chute. When a bowl drops from the carousel, the impact vibration triggers the SW-420 digital comparator output.
- **Connection:**
  - `Pin 1 (+5V)` -> VCC
  - `Pin 2 (TRIG)` -> NC (Unused)
  - `Pin 3 (SENSE)` -> DO (Digital Output, Active HIGH on vibration)
  - `Pin 4 (GND)` -> GND
- **Software Config:** Attach interrupt to `PIN_DROP1_SENSE` (`GPIO4`) or `PIN_DROP2_SENSE` (`GPIO5`) with `RISING` edge trigger.

#### Sensor Option B: HC-SR04 / US-015 Ultrasonic Sensor (Cảm Biến Siêu Âm)
- **Concept:** Installed at the top of the drop chute aiming downward. Measures distance to the bottom plate; sudden decrease in distance indicates bowl detected.
- **Connection:**
  - `Pin 1 (+5V)` -> VCC
  - `Pin 2 (TRIG)` -> TRIG (Driven by `GPIO21`)
  - `Pin 3 (SENSE)` -> ECHO (5V pulse safely divided down to 3.3V by onboard $R_{16}/R_{17}$ and $R_{18}/R_{19}$)
  - `Pin 4 (GND)` -> GND

#### Sensor Option C: Traditional IR Beam-Break Sensor
- **Connection:**
  - `Pin 1 (+5V)` -> VCC
  - `Pin 2 (TRIG)` -> NC
  - `Pin 3 (SENSE)` -> OUT (Phototransistor output, Active LOW on beam interruption)
  - `Pin 4 (GND)` -> GND

---

## 3. Native USB Type-C & Flashing Guide

The board features a top-mount 16-pin USB Type-C connector (`J21`):
- **Pins A6/B6 (D+)** -> $22\,\Omega$ ($R_{12}$) -> ESP32-S3 `GPIO20` (USB D+)
- **Pins A7/B7 (D-)** -> $22\,\Omega$ ($R_{11}$) -> ESP32-S3 `GPIO19` (USB D-)
- **Pin A5 (CC1)** -> $5.1\,\text{k}\Omega$ ($R_{14}$) -> GND
- **Pin B5 (CC2)** -> $5.1\,\text{k}\Omega$ ($R_{15}$) -> GND

### Flashing Procedure
1. **Power:** The FreshVend controller board is **DC-powered from 12V** via `J1` (`MSTBA 2-pin`). The USB port is **DATA ONLY**; VBUS is intentionally isolated for safety and noise immunity. Always connect 12V DC power to `J1` during firmware flashing.
2. **PC Connection:** Plug standard USB Type-C to Type-A/C cable into PC.
3. **Automatic ROM Boot:** ESP32-S3 native USB automatically enumerates as **`USB JTAG/serial debug unit`** (COM port).
4. **Manual Recovery (if needed):**
   - Hold `BOOT` button (`SW2`).
   - Press and release `RESET` button (`SW1`).
   - Release `BOOT` button (`SW2`).
   - The device immediately enters USB ROM Download Mode.
5. **Firmware Upload (PlatformIO / Arduino / ESP-IDF):**
   ```ini
   ; platformio.ini configuration
   [env:esp32-s3-freshvend]
   platform = espressif32
   board = esp32-s3-devkitc-1
   framework = arduino
   board_build.mcu = esp32s3
   board_build.f_cpu = 240000000L
   board_build.flash_mode = qio
   board_build.flash_size = 8MB
   build_flags = 
       -D ARDUINO_USB_MODE=1
       -D ARDUINO_USB_CDC_ON_BOOT=1
   ```

---

## 4. Firmware GPIO Pinout Mapping

All pin definitions are codified in [`FV-CTRL_RevS3-pins.h`](file:///f:/project/repo-github/pcb/pcb/docs/rev_s3/FV-CTRL_RevS3-pins.h):

```c
// Servo Motor PWM (Channel A & B)
#define PIN_SERVO_S1_TOP       16   // Column 1 Top Gate Servo
#define PIN_SERVO_S1_BOT       17   // Column 1 Bottom Release Servo
#define PIN_SERVO_S2_TOP       18   // Column 2 Top Gate Servo
#define PIN_SERVO_S2_BOT       14   // Column 2 Bottom Release Servo

// Universal Drop Sensors (J11 & J12)
#define PIN_DROP1_SENSE         4   // Col 1 Sensor Sense / Echo
#define PIN_DROP2_SENSE         5   // Col 2 Sensor Sense / Echo
#define PIN_DROP_TRIG          21   // Shared Ultrasonic Trigger (HC-SR04)

// Limit Switches (J10)
#define PIN_LIMIT_SW1           6   // Column 1 Top Limit
#define PIN_LIMIT_SW2           7   // Column 1 Bottom Limit
#define PIN_LIMIT_SW3           8   // Column 2 Top Limit
#define PIN_LIMIT_SW4           9   // Column 2 Bottom Limit

// I2C Expansion Bus (J9)
#define PIN_I2C_SDA             1   // I2C SDA (4.7k pull-up to 3.3V)
#define PIN_I2C_SCL             2   // I2C SCL (4.7k pull-up to 3.3V)

// Native USB Interface (J21)
#define PIN_USB_DM             19   // USB D-
#define PIN_USB_DP             20   // USB D+

// Dedicated Boot/Debug UART0 (Test Points TP7/TP8)
#define PIN_UART0_TXD          43   // Debug TXD
#define PIN_UART0_RXD          44   // Debug RXD
```

---

## 5. JLCPCB Production Ordering Guide

To order the manufactured and SMT-assembled PCB from JLCPCB:

1. **Upload Gerber:**
   - Go to [JLCPCB Quote Page](https://cart.jlcpcb.com/quote).
   - Drag & drop [`FV-CTRL_RevS3-Gerber.zip`](file:///f:/project/repo-github/pcb/pcb/releases/rev_s3/FV-CTRL_RevS3-Gerber.zip).
   - Verify dimensions detected: **100 mm × 100 mm**, 2 Layers.
   - Recommended PCB Color: Green, Blue, or Matte Black.
   - Surface Finish: **HASL with lead** (or ENIG for premium oxidation resistance).
   - Copper Weight: **1 oz**.

2. **Enable PCB Assembly (SMT):**
   - Toggle **PCB Assembly** switch to **ON**.
   - PCBA Type: **Standard** (required for ESP32-S3 module and Type-C assembly).
   - Assembly Side: **Top Side**.
   - Click **Next**.

3. **Upload BOM & CPL Files:**
   - **BOM File:** Upload [`FV-CTRL_RevS3-BOM.csv`](file:///f:/project/repo-github/pcb/pcb/releases/rev_s3/FV-CTRL_RevS3-BOM.csv).
   - **CPL File:** Upload [`FV-CTRL_RevS3-CPL.csv`](file:///f:/project/repo-github/pcb/pcb/releases/rev_s3/FV-CTRL_RevS3-CPL.csv).
   - Click **Next**.

4. **Component Match & Placement Review:**
   - Check that all 24 line items (39 SMT parts) match their verified LCSC part numbers.
   - Review 3D placement preview. Component orientations have been normalized to JLCPCB SMT library footprints.
   - Save to Cart and checkout!

---

## 6. Deliverable File Manifest & Checksums

| File | Description | Location |
|---|---|---|
| **Gerber Package** | 11 fabrication layers (zip) | [`FV-CTRL_RevS3-Gerber.zip`](file:///f:/project/repo-github/pcb/pcb/releases/rev_s3/FV-CTRL_RevS3-Gerber.zip) |
| **JLCPCB SMT BOM** | Bill of Materials for SMT | [`FV-CTRL_RevS3-BOM.csv`](file:///f:/project/repo-github/pcb/pcb/releases/rev_s3/FV-CTRL_RevS3-BOM.csv) |
| **JLCPCB SMT CPL** | Pick & Place Centroid file | [`FV-CTRL_RevS3-CPL.csv`](file:///f:/project/repo-github/pcb/pcb/releases/rev_s3/FV-CTRL_RevS3-CPL.csv) |
| **Full Eng BOM** | Complete procurement table | [`FV-CTRL_RevS3-BOM-full.csv`](file:///f:/project/repo-github/pcb/pcb/docs/rev_s3/FV-CTRL_RevS3-BOM-full.csv) |
| **Schematic PDF** | 5-sheet hierarchical schematic | [`FV-CTRL_RevS3-Schematic.pdf`](file:///f:/project/repo-github/pcb/pcb/docs/rev_s3/FV-CTRL_RevS3-Schematic.pdf) |
| **3D STEP CAD** | Mechanical integration model | [`FV-CTRL_RevS3-3D.step`](file:///f:/project/repo-github/pcb/pcb/docs/rev_s3/FV-CTRL_RevS3-3D.step) |
| **Firmware Pinout** | C/C++ pin configuration header | [`FV-CTRL_RevS3-pins.h`](file:///f:/project/repo-github/pcb/pcb/docs/rev_s3/FV-CTRL_RevS3-pins.h) |
| **Release Manifest**| Verification & SHA256 hashes | [`FV-CTRL_RevS3-manifest.json`](file:///f:/project/repo-github/pcb/pcb/releases/rev_s3/FV-CTRL_RevS3-manifest.json) |
