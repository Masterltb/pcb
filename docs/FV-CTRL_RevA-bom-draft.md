# BOM Nháp FV-CTRL Rev A (Engineering Draft)

| Ref | Giá trị / Mô tả | Thư viện | Footprint | DNP | MPN / Ghi chú |
|---|---|---|---|---|---|
| J1 | 12V_IN | `Connector_Generic:Conn_01x02` | TBD | No | Pluggable 2-pin 5.0mm |
| F1 | 5A 250V | `Device:Fuse` | TBD | No | 5x20mm 5A cartridge |
| Q1 | IRF9540N | `Device:Q_PMOS` | TBD | No | IRF9540NPBF |
| R9 | 10k | `Device:R` | TBD | No | 10k 1/4W 5% |
| D1 | 1.5KE15CA | `Device:D_TVS` | TBD | No | 1.5KE15CA |
| J2 | XL4015_A (6.0V >=5A) | `Connector_Generic:Conn_01x04` | TBD | No | Breakout Module 4-pin |
| J3 | XL4015_B (6.0V >=5A) | `Connector_Generic:Conn_01x04` | TBD | No | Breakout Module 4-pin |
| J4 | BUCK_5V (Logic) | `Connector_Generic:Conn_01x04` | TBD | No | Breakout Module 4-pin |
| F2 | PTC 3A | `Device:Polyfuse` | TBD | No | Bourns MF-R300 |
| C1 | 1000-2200uF 16V | `Device:C_Polarized` | TBD | No | 1000uF 16V Radial |
| C3 | 100nF | `Device:C` | TBD | No | 100nF 50V Ceramic |
| J5 | S1_TOP | `Connector_Generic:Conn_01x03` | TBD | No | 3-pin Header |
| J6 | S1_BOT | `Connector_Generic:Conn_01x03` | TBD | No | 3-pin Header |
| F3 | PTC 3A | `Device:Polyfuse` | TBD | No | Bourns MF-R300 |
| C2 | 1000-2200uF 16V | `Device:C_Polarized` | TBD | No | 1000uF 16V Radial |
| C4 | 100nF | `Device:C` | TBD | No | 100nF 50V Ceramic |
| J7 | S2_TOP | `Connector_Generic:Conn_01x03` | TBD | No | 3-pin Header |
| J8 | S2_BOT | `Connector_Generic:Conn_01x03` | TBD | No | 3-pin Header |
| J18 | ESP32_Left (Pins 1-19) | `Connector_Generic:Conn_01x19` | TBD | No | 19-pin Female Header 2.54mm |
| J19 | ESP32_Right (Pins 20-38) | `Connector_Generic:Conn_01x19` | TBD | No | 19-pin Female Header 2.54mm |
| R1 | 330R | `Device:R` | TBD | No | 330R 1/4W 5% |
| R5 | 10k | `Device:R` | TBD | No | 10k 1/4W 5% |
| R2 | 330R | `Device:R` | TBD | No | 330R 1/4W 5% |
| R6 | 10k | `Device:R` | TBD | No | 10k 1/4W 5% |
| R3 | 330R | `Device:R` | TBD | No | 330R 1/4W 5% |
| R7 | 10k | `Device:R` | TBD | No | 10k 1/4W 5% |
| R4 | 330R | `Device:R` | TBD | No | 330R 1/4W 5% |
| R8 | 10k | `Device:R` | TBD | No | 10k 1/4W 5% |
| R13 | 1k | `Device:R` | TBD | No | 1k 1/4W 5% |
| Q2 | S8050 | `Device:Q_NPN` | TBD | No | S8050 |
| R14 | 120R | `Device:R` | TBD | No | 120R 1/2W 5% |
| J11 | IR_TX1 (Col 1) | `Connector_Generic:Conn_01x02` | TBD | No | JST-XH 2-pin |
| R15 | 120R | `Device:R` | TBD | No | 120R 1/2W 5% |
| J12 | IR_TX2 (Col 2) | `Connector_Generic:Conn_01x02` | TBD | No | JST-XH 2-pin |
| J9 | IR_RX1 | `Connector_Generic:Conn_01x03` | TBD | No | JST-XH 3-pin |
| J10 | IR_RX2 | `Connector_Generic:Conn_01x03` | TBD | No | JST-XH 3-pin |
| J13 | LS1 (DNP) | `Connector_Generic:Conn_01x02` | TBD | DNP | JST-XH 2-pin |
| R16 | 10k (DNP) | `Device:R` | TBD | DNP | 10k 1/4W 5% |
| C7 | 100nF (DNP) | `Device:C` | TBD | DNP | 100nF 50V Ceramic |
| J14 | LS2 (DNP) | `Connector_Generic:Conn_01x02` | TBD | DNP | JST-XH 2-pin |
| R17 | 10k (DNP) | `Device:R` | TBD | DNP | 10k 1/4W 5% |
| C8 | 100nF (DNP) | `Device:C` | TBD | DNP | 100nF 50V Ceramic |
| J15 | LS3 (DNP) | `Connector_Generic:Conn_01x02` | TBD | DNP | JST-XH 2-pin |
| R18 | 10k (DNP) | `Device:R` | TBD | DNP | 10k 1/4W 5% |
| C9 | 100nF (DNP) | `Device:C` | TBD | DNP | 100nF 50V Ceramic |
| J16 | LS4 (DNP) | `Connector_Generic:Conn_01x02` | TBD | DNP | JST-XH 2-pin |
| R19 | 10k (DNP) | `Device:R` | TBD | DNP | 10k 1/4W 5% |
| C10 | 100nF (DNP) | `Device:C` | TBD | DNP | 100nF 50V Ceramic |
| C5 | 10uF 16V | `Device:C_Polarized` | TBD | No | 10uF 16V Radial |
| C6 | 100nF | `Device:C` | TBD | No | 100nF 50V Ceramic |
| R20 | 5.6k | `Device:R` | TBD | No | 5.6k 1/4W 5% |
| D2 | LED_+12V | `Device:LED` | TBD | No | 3mm Green LED |
| R21 | 2.2k | `Device:R` | TBD | No | 2.2k 1/4W 5% |
| D3 | LED_+6V_A | `Device:LED` | TBD | No | 3mm Green LED |
| R22 | 2.2k | `Device:R` | TBD | No | 2.2k 1/4W 5% |
| D4 | LED_+6V_B | `Device:LED` | TBD | No | 3mm Green LED |
| R23 | 1.5k | `Device:R` | TBD | No | 1.5k 1/4W 5% |
| D5 | LED_+5V | `Device:LED` | TBD | No | 3mm Green LED |
| R24 | 1.0k | `Device:R` | TBD | No | 1.0k 1/4W 5% |
| D6 | LED_+3V3 | `Device:LED` | TBD | No | 3mm Green LED |
| TP1 | TP_+12V | `Connector:TestPoint` | TBD | No | Test Point Loop THT |
| TP2 | TP_+6V_A | `Connector:TestPoint` | TBD | No | Test Point Loop THT |
| TP3 | TP_+6V_B | `Connector:TestPoint` | TBD | No | Test Point Loop THT |
| TP4 | TP_+5V | `Connector:TestPoint` | TBD | No | Test Point Loop THT |
| TP5 | TP_+3V3 | `Connector:TestPoint` | TBD | No | Test Point Loop THT |
| TP6 | TP_GND | `Connector:TestPoint` | TBD | No | Test Point Loop THT |
| TP7 | TP_GND | `Connector:TestPoint` | TBD | No | Test Point Loop THT |
| TP8 | TP_SPARE_GPIO33 | `Connector:TestPoint` | TBD | No | Test Point Loop THT |
| J17 | I2C_RESERVED | `Connector_Generic:Conn_01x04` | TBD | No | 4-pin Header 2.54mm |
