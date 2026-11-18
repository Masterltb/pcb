#pragma once

// Copy to secrets.h and fill with the test Wi-Fi and MQTT broker settings.
// Use a broker account restricted by ACL to this device's command/ack/status topics.
#define WIFI_SSID "your-test-wifi"
#define WIFI_PASSWORD "replace-me"
#define MQTT_HOST "mqtt.example.net"
#define MQTT_PORT 8883
#define MQTT_USERNAME "rev-s3-s1-bench-01"
#define MQTT_PASSWORD "replace-me"

// PEM root CA for the broker certificate chain. Do not use setInsecure().
static const char MQTT_CA_CERT[] PROGMEM = R"CERT(
-----BEGIN CERTIFICATE-----
REPLACE_WITH_BROKER_CA_CERTIFICATE
-----END CERTIFICATE-----
)CERT";
