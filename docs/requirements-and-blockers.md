# FV-CTRL Rev A: Electrical Requirements & Design Blockers

**Document Version:** 1.0 (Native Schematic Stage)  
**Project:** FV-CTRL (Fruit-Bowl Vending Machine Controller) Rev A  
**Target Platform:** KiCad 10.0.7  
**Scope:** Engineering draft requirements and design blockers for native schematic and pre-layout verification.

---

## 1. Electrical Architecture Overview

The FV-CTRL Rev A board is a 2-layer, 100% through-hole (THT) controller board designed to manage a dual-column FIFO (First-In, First-Out) fruit bowl dispensing mechanism.

```
                    +-------------------------------------------------------+
                    |                 12V DC Supply Input                   |
                    +-------------------------------------------------------+
                                                |
                                    [F1: 5A Replaceable Fuse]
                                                |
                                  [Q1: P-MOSFET Reverse Polarity]
                                                |
                                      [D1: 12V TVS Clamp]
                                                |
                               +----------------+----------------+
                               |                |                |
                       +-------v-------+ +------v-------+ +------v-------+
                       |    Buck A     | |    Buck B     | |    Buck C     |
                       |    XL4015     | |    XL4015     | |  5V Logic     |
                       |   (12V->6V)   | |   (12V->6V)   | |  (12V->5V)    |
                       +-------+-------+ +------+-------+ +------+-------+
                               |                |                |
                            [PTC F2]         [PTC F3]            |
                           Bulk C1          Bulk C2              |
                               |                |                |
                          +----+----+      +----+----+           |
                          |  Col 1  |      |  Col 2  |           |
                          | Servos  |      | Servos  |           |
                          | (2x)    |      | (2x)    |           |
                          +---------+      +---------+           |
                                                                 |
                                 +-------------------------------+
                                 |
                 +---------------+---------------+
                 |                               |
        +--------v--------+             +--------v--------+
        | ESP32 DevKit 38 |             |   IR Emitter    |
        |  (5V Input)     |             |   (2x LED IR)   |
        |  (3V3 Output)   |             +-----------------+
        +--------+--------+
                 |
      +----------+----------+
      |          |          |
+-----v----+ +---v----+ +---v----+
| 4x PWM   | | 2x IR  | | 4x LS  |
| 330R+10k | | RX     | | (DNP)  |
+----------+ +--------+ +--------+
```

---

## 2. Requirements Matrix: Confirmed vs. Assumptions

| Item | Specification / Requirement | Status | Rationale / Reference |
|---|---|---|---|
| **Board Technology** | 2-layer, <= 100 x 100 mm, 100% THT hand-soldered | **Confirmed** | `PROJECT.md` Section 1, 8 |
| **Power Input** | 12V DC from external power supply via pluggable screw terminal | **Confirmed** | `PROJECT.md` Section 3, 6 |
| **Input Protection** | 5A cartridge fuse (F1) + P-MOSFET reverse polarity (Q1) + TVS diode (D1) | **Confirmed** | `PROJECT.md` Section 7 |
| **Servo Power Architecture** | 2 independent buck channels (Buck A, Buck B) set to 6.0V nominal | **Confirmed** | `PROJECT.md` Section 3 |
| **Servo Channel Protection** | PTC fuse per rail (F2, F3) + 1000-2200uF electrolytic + 100nF ceramic | **Confirmed** | `PROJECT.md` Section 7 |
| **Servo Motors** | 4x MG996R continuous rotation (360 deg), 2 per column (TOP/BOT) | **Confirmed** | `PROJECT.md` Section 4 |
| **Servo Connectors** | 4x 3-pin 2.54mm pin headers (GND, V+, SIG) | **Confirmed** | `PROJECT.md` Section 6 |
| **Servo PWM Signal Conditioning** | 330 ohm series resistor + 10k ohm pull-down to GND per servo channel | **Confirmed** | `PROJECT.md` Section 7 |
| **Logic Power Architecture** | Separate 5V buck converter (Buck C) supplying ESP32 5V pin and IR TX | **Confirmed** | Isolates ESP32 from servo transients |
| **MCU Socket** | ESP32 DevKit 38-pin mounted via female socket headers (no direct soldering) | **Confirmed** | `PROJECT.md` Section 4 |
| **MCU Pin Allocation** | PWM: 16, 17, 18, 19; IR TX: 23; IR RX: 34, 35; LS: 25, 26, 27, 32; I2C: 21, 22 | **Confirmed** | `PROJECT.md` Section 5 (No strapping pins used) |
| **IR TX Circuit** | NPN transistor driver (Q2) + 2x IR LEDs with individual series resistors (5V) | **Confirmed** | `PROJECT.md` Section 7 |
| **IR RX Interface** | 2x JST-XH 3-pin headers (3V3, SIG, GND) to satellite RX boards | **Confirmed** | `PROJECT.md` Section 6, 7 |
| **Limit Switches** | 4x JST-XH 2-pin headers with 10k pull-up and 100nF filter (marked DNP) | **Confirmed** | `PROJECT.md` Section 6, 7 |
| **Diagnostics** | Power LEDs + test points on all rails (+12V, +6V_A, +6V_B, +5V, +3V3, GND) | **Confirmed** | `PROJECT.md` Section 7 |
| **ESP32 Header Row Pitch** | Assumed 22.86 mm (0.9 in) or 25.4 mm (1.0 in) dual 19-pin header spacing | *Assumption* | Unverified physical board clone |
| **XL4015 Module Footprint** | Assumed 4-pin header interface (IN+, IN-, OUT+, OUT-) | *Assumption* | Physical module dimensions TBD |
| **5V Buck Module Footprint** | Assumed 4-pin header interface (IN+, IN-, OUT+, OUT-) | *Assumption* | Module dimensions TBD |
| **Component MPNs** | Generic standard THT symbols used for engineering draft | *Assumption* | Specific manufacturer part numbers TBD |

---

## 3. Unresolved Design Blockers

Before advancing to PCB layout and Gerber release, the following design blockers **must** be resolved and verified with physical hardware:

### Blocker 1: ESP32 DevKit 38-Pin Module Verification
- **Issue:** ESP32 38-pin boards vary widely between manufacturers (ESP32-DevKitC, NodeMCU-32S, clones). Differences include row-to-row spacing (0.9" vs 1.0"), antenna overhang, and micro-USB connector position.
- **Required User Action:** Measure the pin row spacing with calipers, confirm pin labeling on the physical board, and check USB connector protrusion.
- **Schematic Action:** Implemented via two 19-pin female connector blocks (`J_ESP32_L`, `J_ESP32_R`) mapped to confirmed GPIO signals with explicit `no_connect` on unused pins.

### Blocker 2: XL4015 Step-Down Converter Module Specification
- **Issue:** The XL4015 >=5A step-down module is purchased as a pre-assembled PCB module. Pad positions, terminal hole spacing, mounting hole locations, and heatsink clearances vary across suppliers.
- **Required User Action:** Measure physical module dimensions (length, width, mounting hole positions, pin header pitch) and verify thermal adequacy for dual continuous MG996R servos.
- **Schematic Action:** Modeled as standard 4-pin interface headers (`J_BUCK_A`, `J_BUCK_B`) with explicit notes to preset output voltage to 6.0V prior to connecting servos.

### Blocker 3: 5V Logic Buck Converter Module Specification
- **Issue:** Physical dimensions and pinout of the 5V buck module (e.g., MP1584EN, mini-360) are unconfirmed.
- **Required User Action:** Provide part number and pin spacing of the chosen module.
- **Schematic Action:** Modeled as standard 4-pin interface header (`J_BUCK_C`).

### Blocker 4: Enclosure and Mechanical Interface
- **Issue:** Board mounting hole coordinates (M3), board outline clearances, connector orientation, and USB access cutout depend on the machine's mechanical chassis.
- **Required User Action:** Provide mounting hole pitch and enclosure interior dimensions.
- **Schematic Action:** Documented in electrical constraints; schematic remains unaffected by physical enclosure outline.

### Blocker 5: THT Protection Component MPN Selection
- **Issue:** Specific manufacturer part numbers for the 5A fuse holder, P-MOSFET (TO-220), 12V TVS (axial), and PTC resettable fuses must be finalized for BOM ordering and footprint pad sizing.
- **Required User Action:** Confirm preferred local vendor part numbers (e.g., Littelfuse, Bourns, Vishay).
- **Schematic Action:** Standard KiCad symbols (`Fuse`, `Polyfuse`, `Q_PMOS_GDS`, `D_TVS`) assigned with functional values.
