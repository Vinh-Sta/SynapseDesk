#include <M5StickCPlus2.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include "config.h"
#include "max30102_handler.h"

WiFiClient espClient;
PubSubClient mqttClient(espClient);
HeartRateSensor hrSensor;

unsigned long lastTelemetryPublish = 0;
constexpr unsigned long PUBLISH_INTERVAL_MS = 2000;

void setupWiFi() {
    StickCP2.Lcd.fillScreen(BLACK);
    StickCP2.Lcd.setCursor(10, 20);
    StickCP2.Lcd.printf("Connecting WiFi...");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
    }
    StickCP2.Lcd.fillScreen(GREEN);
    delay(500);
    StickCP2.Lcd.fillScreen(BLACK);
}

void onMqttMessage(char* topic, byte* payload, unsigned int length) {
    JsonDocument doc;
    DeserializationError error = deserializeJson(doc, payload, length);
    if (error) return;

    const char* reversalQ = doc["reversal_question"] | "Break the rule!";
    
    // Display cognitive prompt feedback on LCD screen
    StickCP2.Lcd.fillScreen(ORANGE);
    StickCP2.Lcd.setTextColor(BLACK);
    StickCP2.Lcd.setTextSize(2);
    StickCP2.Lcd.setCursor(10, 10);
    StickCP2.Lcd.printf("REVERSE AI:\n");
    StickCP2.Lcd.setTextSize(1);
    StickCP2.Lcd.setCursor(10, 45);
    StickCP2.Lcd.printf("%s", reversalQ);
}

void reconnectMqtt() {
    while (!mqttClient.connected()) {
        if (mqttClient.connect(DEVICE_ID)) {
            mqttClient.subscribe(TOPIC_ACTUATION);
        } else {
            delay(2000);
        }
    }
}

void setup() {
    StickCP2.begin();
    StickCP2.Lcd.setRotation(1);
    StickCP2.Lcd.setTextColor(WHITE, BLACK);
    StickCP2.Lcd.setTextSize(2);

    setupWiFi();
    mqttClient.setServer(MQTT_BROKER_IP, MQTT_PORT);
    mqttClient.setCallback(onMqttMessage);

    if (!hrSensor.begin(I2C_SDA_PIN, I2C_SCL_PIN)) {
        StickCP2.Lcd.fillScreen(RED);
        StickCP2.Lcd.setCursor(10, 30);
        StickCP2.Lcd.printf("Sensor Error!");
        while (1) delay(100);
    }
}

void loop() {
    StickCP2.update();
    if (!mqttClient.connected()) reconnectMqtt();
    mqttClient.loop();

    hrSensor.update();

    // Button A (Front face): Manual override emergency trigger for demo purposes
    bool manualStressTrigger = StickCP2.BtnA.wasPressed();

    unsigned long now = millis();
    if (now - lastTelemetryPublish >= PUBLISH_INTERVAL_MS) {
        lastTelemetryPublish = now;

        float bpm = hrSensor.getBPM();
        if (manualStressTrigger) bpm = 115.0f; // Force high heart rate to immediately trigger AI block detector

        // Pack telemetry data into JSON format
        JsonDocument doc;
        doc["device_id"] = DEVICE_ID;
        doc["heart_rate_bpm"] = bpm;
        doc["finger_detected"] = hrSensor.isFingerDetected();
        doc["manual_override"] = manualStressTrigger;
        doc["timestamp"] = now;

        char buffer[256];
        serializeJson(doc, buffer);
        mqttClient.publish(TOPIC_TELEMETRY, buffer);

        // Render normal operating state UI on LCD
        StickCP2.Lcd.fillScreen(BLACK);
        StickCP2.Lcd.setTextColor(WHITE);
        StickCP2.Lcd.setCursor(10, 10);
        StickCP2.Lcd.printf("SynapseDesk Node");
        StickCP2.Lcd.setCursor(10, 40);
        if (hrSensor.isFingerDetected()) {
            StickCP2.Lcd.setTextColor(GREEN);
            StickCP2.Lcd.printf("BPM: %.1f", bpm);
        } else {
            StickCP2.Lcd.setTextColor(YELLOW);
            StickCP2.Lcd.printf("Place Finger...");
        }
    }
}