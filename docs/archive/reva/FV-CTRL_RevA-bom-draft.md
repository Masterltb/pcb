# BOM Nháp FV-CTRL Rev A (Engineering Draft)

| Ref | Giá trị / Mô tả | Thư viện | Footprint | DNP | MPN / Ghi chú |
|---|---|---|---|---|---|
| J1 | 12V_IN | `Connector_Generic:Conn_01x02` | TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal | No | Pluggable 2-pin 5.0mm |
| F1 | 5A 250V | `Device:Fuse` | Fuse:Fuseholder_Clip-5x20mm_Littelfuse_111_Inline_P20.00x5.00mm_D1.05mm_Horizontal | No | 5x20mm 5A cartridge |
| Q1 | IRF9540N | `Device:Q_PMOS` | Package_TO_SOT_THT:TO-220-3_Vertical | No | IRF9540NPBF |
| R9 | 10k | `Device:R` | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal | No | 10k 1/4W 5% |
| D1 | 1.5KE15CA | `Device:D_TVS` | Diode_THT:D_DO-201_P12.70mm_Horizontal | No | 1.5KE15CA |
| J2 | XH-M401 (6.0V 8A) | `Connector_Generic:Conn_01x04` | fv_modules:Converter_DCDC_XH-M401_8A | No | XH-M401 (XL4016E1 8A 200W) |
| J3 | AUX_BUCK (DNP) | `Connector_Generic:Conn_01x04` | Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical | DNP | Auxiliary 4-pin Header |
| J4 | MP1584EN (5V Logic) | `Connector_Generic:Conn_01x04` | fv_modules:Converter_DCDC_MP1584EN | No | MP1584EN Mini 3A Buck |
| F2 | PTC 3A | `Device:Polyfuse` | Fuse:Fuse_Bourns_MF-RG300 | No | Bourns MF-R300 |
| C1 | 1000-2200uF 16V | `Device:C_Polarized` | Capacitor_THT:CP_Radial_D12.5mm_P5.00mm | No | 1000uF 16V Radial |
| C3 | 100nF | `Device:C` | Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm | No | 100nF 50V Ceramic |
| J5 | S1_TOP | `Connector_Generic:Conn_01x03` | Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical | No | 3-pin Header |
| J6 | S1_BOT | `Connector_Generic:Conn_01x03` | Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical | No | 3-pin Header |
| F3 | PTC 3A | `Device:Polyfuse` | Fuse:Fuse_Bourns_MF-RG300 | No | Bourns MF-R300 |
| C2 | 1000-2200uF 16V | `Device:C_Polarized` | Capacitor_THT:CP_Radial_D12.5mm_P5.00mm | No | 1000uF 16V Radial |
| C4 | 100nF | `Device:C` | Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm | No | 100nF 50V Ceramic |
| J7 | S2_TOP | `Connector_Generic:Conn_01x03` | Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical | No | 3-pin Header |
| J8 | S2_BOT | `Connector_Generic:Conn_01x03` | Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical | No | 3-pin Header |
| U3 | AMS1117-3.3 | `Regulator_Linear:AP1117-15` | Package_TO_SOT_SMD:SOT-223-3_TabPin2 | No | AMS1117-3.3 |
| C11 | 10uF 16V | `Device:C_Polarized` | Capacitor_THT:CP_Radial_D5.0mm_P2.00mm | No | 10uF 16V Radial |
| C12 | 22uF 16V | `Device:C_Polarized` | Capacitor_THT:CP_Radial_D5.0mm_P2.00mm | No | 22uF 16V Radial |
| C13 | 100nF | `Device:C` | Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm | No | 100nF 50V Ceramic |
| U2 | ESP32-WROOM-32 | `RF_Module:ESP32-WROOM-32` | RF_Module:ESP32-WROOM-32 | No | ESP32-WROOM-32E |
| R10 | 10k | `Device:R` | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal | No | 10k 1/4W 5% |
| C14 | 100nF | `Device:C` | Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm | No | 100nF 50V Ceramic |
| SW1 | SW_EN | `Switch:SW_Push` | Button_Switch_THT:SW_PUSH_6mm_H5mm | No | SW-PB-6mm |
| R11 | 10k | `Device:R` | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal | No | 10k 1/4W 5% |
| SW2 | SW_BOOT | `Switch:SW_Push` | Button_Switch_THT:SW_PUSH_6mm_H5mm | No | SW-PB-6mm |
| J20 | PROG_UART0 | `Connector_Generic:Conn_01x06` | Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical | No | Header 1x06 2.54mm |
| J21 | SENSOR_ADC | `Connector_Generic:Conn_01x04` | Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical | No | Header 1x04 2.54mm |
| J22 | SENSOR_DIGITAL | `Connector_Generic:Conn_01x08` | Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical | No | Header 1x08 2.54mm |
| R1 | 330R | `Device:R` | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal | No | 330R 1/4W 5% |
| R5 | 10k | `Device:R` | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal | No | 10k 1/4W 5% |
| R2 | 330R | `Device:R` | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal | No | 330R 1/4W 5% |
| R6 | 10k | `Device:R` | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal | No | 10k 1/4W 5% |
| R3 | 330R | `Device:R` | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal | No | 330R 1/4W 5% |
| R7 | 10k | `Device:R` | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal | No | 10k 1/4W 5% |
| R4 | 330R | `Device:R` | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal | No | 330R 1/4W 5% |
| R8 | 10k | `Device:R` | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal | No | 10k 1/4W 5% |
| R13 | 1k | `Device:R` | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal | No | 1k 1/4W 5% |
| Q2 | S8050 | `Device:Q_NPN` | Package_TO_SOT_THT:TO-92_Inline | No | S8050 |
| R14 | 120R | `Device:R` | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal | No | 120R 1/2W 5% |
| J11 | IR_TX1 (Col 1) | `Connector_Generic:Conn_01x02` | Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical | No | JST-XH 2-pin |
| R15 | 120R | `Device:R` | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal | No | 120R 1/2W 5% |
| J12 | IR_TX2 (Col 2) | `Connector_Generic:Conn_01x02` | Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical | No | JST-XH 2-pin |
| J9 | IR_RX1 | `Connector_Generic:Conn_01x03` | Connector_JST:JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical | No | JST-XH 3-pin |
| J10 | IR_RX2 | `Connector_Generic:Conn_01x03` | Connector_JST:JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical | No | JST-XH 3-pin |
| J13 | LS1 (DNP) | `Connector_Generic:Conn_01x02` | Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical | DNP | JST-XH 2-pin |
| R16 | 10k (DNP) | `Device:R` | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal | DNP | 10k 1/4W 5% |
| C7 | 100nF (DNP) | `Device:C` | Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm | DNP | 100nF 50V Ceramic |
| J14 | LS2 (DNP) | `Connector_Generic:Conn_01x02` | Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical | DNP | JST-XH 2-pin |
| R17 | 10k (DNP) | `Device:R` | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal | DNP | 10k 1/4W 5% |
| C8 | 100nF (DNP) | `Device:C` | Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm | DNP | 100nF 50V Ceramic |
| J15 | LS3 (DNP) | `Connector_Generic:Conn_01x02` | Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical | DNP | JST-XH 2-pin |
| R18 | 10k (DNP) | `Device:R` | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal | DNP | 10k 1/4W 5% |
| C9 | 100nF (DNP) | `Device:C` | Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm | DNP | 100nF 50V Ceramic |
| J16 | LS4 (DNP) | `Connector_Generic:Conn_01x02` | Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical | DNP | JST-XH 2-pin |
| R19 | 10k (DNP) | `Device:R` | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal | DNP | 10k 1/4W 5% |
| C10 | 100nF (DNP) | `Device:C` | Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm | DNP | 100nF 50V Ceramic |
| C5 | 10uF 16V | `Device:C_Polarized` | Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm | No | 10uF 16V Radial |
| C6 | 100nF | `Device:C` | Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm | No | 100nF 50V Ceramic |
| R20 | 5.6k | `Device:R` | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal | No | 5.6k 1/4W 5% |
| D2 | LED_+12V | `Device:LED` | LED_THT:LED_D3.0mm | No | 3mm Green LED |
| R21 | 2.2k | `Device:R` | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal | No | 2.2k 1/4W 5% |
| D3 | LED_+6V_A | `Device:LED` | LED_THT:LED_D3.0mm | No | 3mm Green LED |
| R22 | 2.2k | `Device:R` | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal | No | 2.2k 1/4W 5% |
| D4 | LED_+6V_B | `Device:LED` | LED_THT:LED_D3.0mm | No | 3mm Green LED |
| R23 | 1.5k | `Device:R` | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal | No | 1.5k 1/4W 5% |
| D5 | LED_+5V | `Device:LED` | LED_THT:LED_D3.0mm | No | 3mm Green LED |
| R24 | 1.0k | `Device:R` | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal | No | 1.0k 1/4W 5% |
| D6 | LED_+3V3 | `Device:LED` | LED_THT:LED_D3.0mm | No | 3mm Green LED |
| TP1 | TP_+12V | `Connector:TestPoint` | TestPoint:TestPoint_Pad_D2.0mm | No | Test Point Loop THT |
| TP2 | TP_+6V_A | `Connector:TestPoint` | TestPoint:TestPoint_Pad_D2.0mm | No | Test Point Loop THT |
| TP3 | TP_+6V_B | `Connector:TestPoint` | TestPoint:TestPoint_Pad_D2.0mm | No | Test Point Loop THT |
| TP4 | TP_+5V | `Connector:TestPoint` | TestPoint:TestPoint_Pad_D2.0mm | No | Test Point Loop THT |
| TP5 | TP_+3V3 | `Connector:TestPoint` | TestPoint:TestPoint_Pad_D2.0mm | No | Test Point Loop THT |
| TP6 | TP_GND | `Connector:TestPoint` | TestPoint:TestPoint_Pad_D2.0mm | No | Test Point Loop THT |
| TP7 | TP_GND | `Connector:TestPoint` | TestPoint:TestPoint_Pad_D2.0mm | No | Test Point Loop THT |
| TP8 | TP_SPARE_GPIO33 | `Connector:TestPoint` | TestPoint:TestPoint_Pad_D2.0mm | No | Test Point Loop THT |
| J17 | I2C_RESERVED | `Connector_Generic:Conn_01x04` | Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical | No | 4-pin Header 2.54mm |
