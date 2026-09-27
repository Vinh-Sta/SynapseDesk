#include "max30102_handler.h"

HeartRateSensor::HeartRateSensor() 
    : sensorWire(0), currentBPM(0.0f), fingerPresent(false), lastBeat(0), rateSpot(0) {
    for (byte i = 0; i < RATE_SIZE; i++) rates[i] = 0;
}

bool HeartRateSensor::begin(int sdaPin, int sclPin) {
    sensorWire.begin(sdaPin, sclPin, 400000); // 400kHz I2C
    if (!particleSensor.begin(sensorWire, I2C_SPEED_FAST)) {
        return false;
    }
    
    // Configure sensor LED parameters optimized for finger skin measurements
    particleSensor.setup(0x1F, 4, 2, 400, 411, 4096);
    particleSensor.setPulseAmplitudeRed(0x0A);
    particleSensor.setPulseAmplitudeGreen(0);
    return true;
}

void HeartRateSensor::update() {
    long irValue = particleSensor.getIR();

    if (irValue < 50000) {
        fingerPresent = false;
        currentBPM = 0.0f;
        return;
    }

    fingerPresent = true;
    if (checkForBeat(irValue)) {
        long delta = millis() - lastBeat;
        lastBeat = millis();

        float beatsPerMinute = 60.0f / (delta / 1000.0f);

        if (beatsPerMinute < 255.0f && beatsPerMinute > 30.0f) {
            rates[rateSpot++] = (byte)beatsPerMinute;
            rateSpot %= RATE_SIZE;

            // Calculate 4-beat sliding average
            int beatAvg = 0;
            for (byte x = 0; x < RATE_SIZE; x++) beatAvg += rates[x];
            beatAvg /= RATE_SIZE;
            currentBPM = static_cast<float>(beatAvg);
        }
    }
}

float HeartRateSensor::getBPM() const {
    return currentBPM;
}

bool HeartRateSensor::isFingerDetected() const {
    return fingerPresent;
}