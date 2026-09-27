#pragma once
#include <Wire.h>
#include "MAX30105.h"
#include "heartRate.h"

class HeartRateSensor {
public:
    HeartRateSensor();
    bool begin(int sdaPin, int sclPin);
    void update();
    float getBPM() const;
    bool isFingerDetected() const;

private:
    MAX30105 particleSensor;
    TwoWire sensorWire;
    float currentBPM;
    bool fingerPresent;
    long lastBeat;
    static constexpr byte RATE_SIZE = 4;
    byte rates[RATE_SIZE];
    byte rateSpot;
};