/**
 * @file FV-CTRL_RevS3-pins.h
 * @brief FreshVend Controller Rev-S3 Board Pin Definitions & Hardware Configuration
 * @author FreshVend Hardware Engineering Team
 * @date 2026-10-28
 *
 * Microcontroller: ESP32-S3-WROOM-1U (Dual-core Xtensa LX7 @ 240MHz, 8MB Flash, IPEX Ant)
 * Hardware Revision: Rev-S3
 * Target Application: Automated Fresh Fruit Bowl Vending Machine Controller
 */

#ifndef FV_CTRL_REVS3_PINS_H_
#define FV_CTRL_REVS3_PINS_H_

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ========================================================================== */
/*                               BOARD METADATA                               */
/* ========================================================================== */
#define FV_BOARD_REVISION           "Rev-S3"
#define FV_BOARD_MCU                "ESP32-S3-WROOM-1U"
#define FV_BOARD_FLASH_SIZE_MB      8
#define FV_BOARD_NATIVE_USB         1

/* ========================================================================== */
/*                           SERVO ACTUATOR PWM PINS                          */
/* ========================================================================== */
/**
 * @brief 4x Servo PWM control channels (Standard 50Hz RC PWM, 1.0ms - 2.0ms pulse)
 * Connected via 330 ohm series damping resistors with 10k pulldown resistors.
 * Powered by dedicated +6V Buck converters (+6V_A for Gate 1, +6V_B for Gate 2).
 */
#define PIN_SERVO1_TOP_PWM          16   /* IO16 (Pin 9)  - S1 Top Gate Door Actuator */
#define PIN_SERVO1_BOT_PWM          17   /* IO17 (Pin 10) - S1 Bottom Dispense Actuator */
#define PIN_SERVO2_TOP_PWM          18   /* IO18 (Pin 11) - S2 Top Gate Door Actuator */
#define PIN_SERVO2_BOT_PWM          14   /* IO14 (Pin 22) - S2 Bottom Dispense Actuator */

#define SERVO_PWM_FREQUENCY_HZ      50
#define SERVO_PWM_RESOLUTION_BITS   16

/* ========================================================================== */
/*                      UNIVERSAL DROP DETECTION SENSORS                      */
/* ========================================================================== */
/**
 * @brief Dual Universal 4-Pin Drop Detection Sensor Headers (J11 & J12).
 * JST-XH 4-Pin Layout: [Pin 1: +5V, Pin 2: TRIG, Pin 3: SENS_OUT, Pin 4: GND]
 *
 * Compatible Sensors:
 * 1. SW-420 Vibration Sensor: Digital pulse on SENS_OUT when fruit bowl hits chute.
 * 2. HC-SR04 Ultrasonic Sensor: TRIG sent on PIN_DROP_TRIG, Echo received on PIN_DROP_SENSx.
 * 3. IR Optical Beam Barrier: Active-LOW beam break on PIN_DROP_SENSx.
 *
 * Note: Echo / Sense signals are level-shifted via 1k / 2k divider (5V -> 3.3V safe).
 */
#define PIN_DROP_SENS1              4    /* IO4  (Pin 4)  - Chute 1 Sensor Input (Echo/Digital) */
#define PIN_DROP_SENS2              5    /* IO5  (Pin 5)  - Chute 2 Sensor Input (Echo/Digital) */
#define PIN_DROP_TRIG               21   /* IO21 (Pin 23) - Shared Ultrasonic Trigger Pulse */

/* ========================================================================== */
/*                            LIMIT SWITCH INPUTS                             */
/* ========================================================================== */
/**
 * @brief 4x Endstop Limit Switches for mechanical travel verification (J10 header).
 * Normally-Closed (NC) or Normally-Open (NO) configuration with internal pull-up enabled.
 */
#define PIN_LIMIT_1_TOP             6    /* IO6  (Pin 6)  - Gate 1 Upper Limit Switch */
#define PIN_LIMIT_1_BOT             7    /* IO7  (Pin 7)  - Gate 1 Lower Limit Switch */
#define PIN_LIMIT_2_TOP             8    /* IO8  (Pin 12) - Gate 2 Upper Limit Switch */
#define PIN_LIMIT_2_BOT             9    /* IO9  (Pin 17) - Gate 2 Lower Limit Switch */

/* ========================================================================== */
/*                            I2C EXPANSION BUS                               */
/* ========================================================================== */
/**
 * @brief Spare I2C bus header (J9) with on-board 4.7k pull-up resistors to +3.3V.
 * JST-XH 4-Pin: [Pin 1: +3.3V, Pin 2: SDA, Pin 3: SCL, Pin 4: GND]
 * Ideal for OLED display, temperature/humidity sensor (SHT40), or NFC/RFID reader.
 */
#define PIN_I2C_SDA                 1    /* IO1  (Pin 39) - I2C Data */
#define PIN_I2C_SCL                 2    /* IO2  (Pin 38) - I2C Clock */
#define I2C_BUS_DEFAULT_FREQ_HZ     400000

/* ========================================================================== */
/*                       NATIVE USB & DEBUG UART INTERFACES                   */
/* ========================================================================== */
/**
 * @brief ESP32-S3 Built-in USB-Serial-JTAG on USB Type-C Receptacle (J21).
 * Completely eliminates external USB-UART bridge chips (CP2102N/CH340).
 * Provides direct high-speed flashing, USB CDC console, and hardware JTAG debugging.
 */
#define PIN_USB_DM                  19   /* IO19 (Pin 13) - USB Full-Speed D- */
#define PIN_USB_DP                  20   /* IO20 (Pin 14) - USB Full-Speed D+ */

/**
 * @brief Hardware UART0 Test Points (TP7: TXD, TP8: RXD) for low-level boot logs.
 */
#define PIN_UART0_TX                43   /* IO43 (Pin 37) - Boot Log TX (TP7) */
#define PIN_UART0_RX                44   /* IO44 (Pin 36) - Boot Log RX (TP8) */
#define UART0_DEFAULT_BAUD          115200

/* ========================================================================== */
/*                           SYSTEM CONTROL PUSHBUTTONS                       */
/* ========================================================================== */
#define PIN_ESP_EN                  -1   /* Hardware Reset (EN pin 3, SW1 tact switch) */
#define PIN_ESP_BOOT                0    /* IO0 (Pin 27, SW2 tact switch) - Download mode */

/* ========================================================================== */
/*                           DIAGNOSTIC TEST POINTS                           */
/* ========================================================================== */
#define TP_12V_MAIN                 1    /* TP1 - Main DC +12V post-Schottky */
#define TP_6V_BUCK_A                2    /* TP2 - Servo Gate 1 Power (+6.0V 3A) */
#define TP_6V_BUCK_B                3    /* TP3 - Servo Gate 2 Power (+6.0V 3A) */
#define TP_5V_RECOM                 4    /* TP4 - Logic/Sensor +5.0V (RECOM R-78E5.0) */
#define TP_3V3_MCU                  5    /* TP5 - MCU Power Rail (+3.3V 800mA LD1117) */
#define TP_GND_MAIN                 6    /* TP6 - System Star Ground reference */
#define TP_UART_TX                  7    /* TP7 - Hardware UART0 TX */
#define TP_UART_RX                  8    /* TP8 - Hardware UART0 RX */

/* ========================================================================== */
/*                              HELPER MACROS                                 */
/* ========================================================================== */
#define FV_INIT_INPUTS() do { \
    pinMode(PIN_DROP_SENS1, INPUT); \
    pinMode(PIN_DROP_SENS2, INPUT); \
    pinMode(PIN_LIMIT_1_TOP, INPUT_PULLUP); \
    pinMode(PIN_LIMIT_1_BOT, INPUT_PULLUP); \
    pinMode(PIN_LIMIT_2_TOP, INPUT_PULLUP); \
    pinMode(PIN_LIMIT_2_BOT, INPUT_PULLUP); \
} while(0)

#define FV_INIT_OUTPUTS() do { \
    pinMode(PIN_DROP_TRIG, OUTPUT); \
    digitalWrite(PIN_DROP_TRIG, LOW); \
} while(0)

#ifdef __cplusplus
}
#endif

#endif /* FV_CTRL_REVS3_PINS_H_ */
