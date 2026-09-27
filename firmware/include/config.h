#pragma once

// Wi-Fi Configuration (Replace with your actual credentials)
constexpr const char* WIFI_SSID     = "YOUR_WIFI_SSID";
constexpr const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// MQTT Broker Configuration (Running on local network or laptop)
constexpr const char* MQTT_BROKER_IP = "192.168.1.100";
constexpr int         MQTT_PORT      = 1883;

// MQTT Topics
constexpr const char* TOPIC_TELEMETRY = "synapse/sensors/telemetry";
constexpr const char* TOPIC_ACTUATION = "synapse/actuator/prompt";

// I2C Communication Pins for MAX30102 on M5StickC Plus 2 top header
constexpr int I2C_SDA_PIN = 0;   // Pin G0
constexpr int I2C_SCL_PIN = 26;  // Pin G26

// Device Identity
constexpr const char* DEVICE_ID = "M5STICK_PLUS2_NODE";