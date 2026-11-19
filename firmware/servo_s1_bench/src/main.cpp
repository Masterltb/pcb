#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <Preferences.h>
#include <esp_system.h>
#include <time.h>
#include "../secrets.h"

// Rev-S3 S1_TOP bench test. GPIO16, 50 Hz, neutral pulse on boot.
constexpr uint8_t SERVO_PIN = 16;
constexpr uint32_t SERVO_HZ = 50;
constexpr uint8_t PWM_BITS = 14;
constexpr uint8_t PWM_CHANNEL = 0;
constexpr uint32_t PWM_MAX = (1u << PWM_BITS) - 1u;
constexpr uint16_t MIN_US = 1000;
constexpr uint16_t MAX_US = 2000;
constexpr uint16_t CENTER_US = 1500;
constexpr uint32_t PERIOD_US = 1000000u / SERVO_HZ;
constexpr char DEVICE_ID[] = "rev-s3-s1-bench-01";
constexpr uint32_t MQTT_RETRY_MS = 5000;
constexpr uint32_t RESTART_DELAY_MS = 350;

WiFiClientSecure tlsClient;
PubSubClient mqtt(tlsClient);
Preferences preferences;
char commandTopic[96], ackTopic[96], availabilityTopic[96], statusTopic[96];
uint32_t lastMqttAttempt = 0;
bool restartRequested = false;
bool remoteRestart = false;
char pendingCommandId[49] = {};

bool outputEnabled = true;
uint16_t pulseUs = CENTER_US;

void setPulse(uint16_t us) {
  pulseUs = us;
  const uint32_t duty = (uint32_t(us) * PWM_MAX + PERIOD_US / 2) / PERIOD_US;
  ledcWrite(PWM_CHANNEL, duty);
  Serial.printf("PWM GPIO%d = %u us\n", SERVO_PIN, pulseUs);
}

void printHelp() {
  Serial.println("Commands: p <1000..2000> | center | off | on | status | reset");
}

void publishAck(const char* commandId, const char* state, const char* detail) {
  if (!mqtt.connected()) return;
  JsonDocument doc;
  doc["device_id"] = DEVICE_ID;
  doc["command_id"] = commandId;
  doc["state"] = state;
  doc["detail"] = detail;
  doc["pulse_us"] = pulseUs;
  doc["output_enabled"] = outputEnabled;
  char payload[192];
  const size_t size = serializeJson(doc, payload, sizeof(payload));
  mqtt.publish(ackTopic, reinterpret_cast<const uint8_t*>(payload), size, false);
}

void onMqttMessage(char* topic, byte* payload, unsigned int length) {
  if (strcmp(topic, commandTopic) != 0 || restartRequested || length == 0 || length > 256) return;
  JsonDocument doc;
  if (deserializeJson(doc, payload, length)) return;
  const char* action = doc["action"] | "";
  const char* target = doc["device_id"] | "";
  const char* commandId = doc["command_id"] | "";
  const int pulse = doc["pulse_us"] | 0;
  const int64_t issuedAt = doc["issued_at"] | int64_t(0);
  const int64_t now = time(nullptr);
  const bool knownAction = strcmp(action, "restart") == 0 || strcmp(action, "status") == 0 ||
      strcmp(action, "servo.center") == 0 || strcmp(action, "servo.off") == 0 ||
      strcmp(action, "servo.on") == 0 || strcmp(action, "servo.set") == 0;
  if (!knownAction || strcmp(target, DEVICE_ID) != 0 ||
      commandId[0] == '\0' || strlen(commandId) > 48 || now < 1700000000 ||
      issuedAt > now + 10 || now - issuedAt > 60 ||
      (strcmp(action, "servo.set") == 0 && (pulse < MIN_US || pulse > MAX_US))) {
    Serial.println("MQTT command rejected: invalid action/target/id");
    return;
  }
  if (!preferences.begin("fv-admin", false)) return;
  const String previousId = preferences.getString("last-command", "");
  if (previousId == commandId) {
    preferences.end();
    publishAck(commandId, "duplicate", "Command ID was already processed");
    Serial.println("MQTT duplicate command ignored");
    return;
  }
  if (preferences.putString("last-command", commandId) == 0) {
    preferences.end();
    publishAck(commandId, "rejected", "Could not persist command ID");
    Serial.println("MQTT command rejected: journal write failed");
    return;
  }
  preferences.end();
  if (strcmp(action, "restart") == 0) {
    strlcpy(pendingCommandId, commandId, sizeof(pendingCommandId));
    restartRequested = true;
    remoteRestart = true;
    publishAck(pendingCommandId, "accepted", "CPU restart scheduled; PWM will be disabled");
    Serial.printf("MQTT restart accepted command_id=%s\n", pendingCommandId);
    return;
  }
  if (strcmp(action, "servo.center") == 0) {
    outputEnabled = true;
    setPulse(CENTER_US);
  } else if (strcmp(action, "servo.set") == 0) {
    outputEnabled = true;
    setPulse(uint16_t(pulse));
  } else if (strcmp(action, "servo.off") == 0) {
    ledcWrite(PWM_CHANNEL, 0);
    outputEnabled = false;
  } else if (strcmp(action, "servo.on") == 0) {
    outputEnabled = true;
    setPulse(pulseUs);
  }
  publishAck(commandId, "done", "Command applied");
  if (strcmp(action, "status") != 0) {
    JsonDocument status;
    status["device_id"] = DEVICE_ID;
    status["firmware"] = "servo_s1_bench-mqtt-1";
    status["pulse_us"] = pulseUs;
    status["output_enabled"] = outputEnabled;
    status["reset_reason"] = unsigned(esp_reset_reason());
    char statusPayload[160];
    const size_t statusSize = serializeJson(status, statusPayload, sizeof(statusPayload));
    mqtt.publish(statusTopic, reinterpret_cast<const uint8_t*>(statusPayload), statusSize, true);
  }
}

void setupMqtt() {
  snprintf(commandTopic, sizeof(commandTopic), "freshvend/%s/admin/command", DEVICE_ID);
  snprintf(ackTopic, sizeof(ackTopic), "freshvend/%s/admin/ack", DEVICE_ID);
  snprintf(availabilityTopic, sizeof(availabilityTopic), "freshvend/%s/availability", DEVICE_ID);
  snprintf(statusTopic, sizeof(statusTopic), "freshvend/%s/status", DEVICE_ID);
  tlsClient.setCACert(MQTT_CA_CERT);
  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setCallback(onMqttMessage);
  mqtt.setBufferSize(384);
  mqtt.setSocketTimeout(2);
  mqtt.setKeepAlive(20);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  configTime(0, 0, "pool.ntp.org", "time.nist.gov");
  preferences.begin("fv-admin", false);
  preferences.end();
  Serial.println("Wi-Fi/MQTT connection scheduled");
}

void mqttTick() {
  if (WiFi.status() != WL_CONNECTED) return;
  if (!mqtt.connected()) {
    const uint32_t now = millis();
    if (uint32_t(now - lastMqttAttempt) < MQTT_RETRY_MS) return;
    lastMqttAttempt = now;
    if (time(nullptr) < 1700000000) return; // TLS certificate validation needs a valid clock.
    const bool connected = mqtt.connect(DEVICE_ID, MQTT_USERNAME, MQTT_PASSWORD,
                                        availabilityTopic, 0, true, "offline");
    if (!connected) {
      char tlsError[128] = {};
      tlsClient.lastError(tlsError, sizeof(tlsError));
      Serial.printf("MQTT connect failed state=%d tls=%s epoch=%lu\n", mqtt.state(),
                    tlsError, static_cast<unsigned long>(time(nullptr)));
      return;
    }
    mqtt.publish(availabilityTopic, "online", true);
    mqtt.subscribe(commandTopic, 1);
    JsonDocument status;
    status["device_id"] = DEVICE_ID;
    status["firmware"] = "servo_s1_bench-mqtt-1";
    status["ip"] = WiFi.localIP().toString();
    status["reset_reason"] = unsigned(esp_reset_reason());
    status["pulse_us"] = pulseUs;
    status["output_enabled"] = outputEnabled;
    char payload[160];
    const size_t size = serializeJson(status, payload, sizeof(payload));
    mqtt.publish(statusTopic, reinterpret_cast<const uint8_t*>(payload), size, true);
    Serial.printf("MQTT connected; subscribed %s\n", commandTopic);
  }
  mqtt.loop();
}

void executeRemoteRestart() {
  if (!restartRequested) return;
  Serial.printf("Remote CPU restart command_id=%s\n", pendingCommandId);
  ledcWrite(PWM_CHANNEL, 0);
  outputEnabled = false;
  if (remoteRestart)
    publishAck(pendingCommandId, "restarting", "PWM disabled; rebooting CPU");
  mqtt.loop();
  delay(RESTART_DELAY_MS);
  ESP.restart();
}

void setup() {
  Serial.begin(115200);
  delay(250);
  ledcSetup(PWM_CHANNEL, SERVO_HZ, PWM_BITS);
  ledcAttachPin(SERVO_PIN, PWM_CHANNEL);
  setPulse(CENTER_US);
  setupMqtt();
  Serial.println("Rev-S3 S1_TOP bench firmware ready; GPIO17/S1_BOT untouched.");
  printHelp();
}

void loop() {
  static String line;
  while (Serial.available()) {
    const char c = char(Serial.read());
    if (c == '\r') continue;
    if (c != '\n') {
      if (line.length() < 48) line += c;
      else line = "!";
      continue;
    }

    line.trim();
    if (line == "center") {
      outputEnabled = true;
      setPulse(CENTER_US);
    } else if (line == "off") {
      ledcWrite(PWM_CHANNEL, 0);
      outputEnabled = false;
      Serial.println("PWM off");
    } else if (line == "on") {
      outputEnabled = true;
      setPulse(pulseUs);
    } else if (line == "status") {
      Serial.printf("GPIO%d pulse=%u us output=%s\n", SERVO_PIN, pulseUs,
                    outputEnabled ? "on" : "off");
    } else if (line == "reset") {
      Serial.println("Local CPU restart requested");
      restartRequested = true;
      remoteRestart = false;
      strlcpy(pendingCommandId, "serial-local", sizeof(pendingCommandId));
    } else if (line.startsWith("p ")) {
      const long requested = line.substring(2).toInt();
      if (requested < MIN_US || requested > MAX_US) {
        Serial.println("Rejected: use 1000..2000 us");
      } else {
        outputEnabled = true;
        setPulse(uint16_t(requested));
      }
    } else {
      printHelp();
    }
    line = "";
  }
  mqttTick();
  executeRemoteRestart();
  delay(2);
}
