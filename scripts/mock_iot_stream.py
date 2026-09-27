"""Mock IoT Stream Script for simulating edge sensor telemetry

and listening to AI actuation feedback via MQTT.
"""

import json
import os
import random
import time
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

# Load environment variables from .env file located at project root
load_dotenv()

# MQTT Configuration from environment variables
MQTT_BROKER = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))
TOPIC_TELEMETRY = "synapse/sensors/telemetry"
TOPIC_ACTUATION = "synapse/actuator/prompt"


def on_connect(client: mqtt.Client, userdata, flags, rc, properties=None) -> None:
    """Callback triggered when the client connects to the MQTT broker."""
    if rc == 0:
        print(f"[MOCK IOT] Connected successfully to MQTT Broker at {MQTT_BROKER}:{MQTT_PORT}")
        # Subscribe to actuation topic to receive AI responses back
        client.subscribe(TOPIC_ACTUATION)
        print(f"[MOCK IOT] Subscribed to actuation topic: {TOPIC_ACTUATION}")
    else:
        print(f"[MOCK IOT] Failed to connect, return code {rc}")


def on_message(client: mqtt.Client, userdata, msg: mqtt.MQTTMessage) -> None:
    """Callback triggered when an actuation message is received from the backend."""
    try:
        payload = json.loads(msg.payload.decode())
        question = payload.get("reversal_question", "")
        timestamp = payload.get("timestamp", 0)
        
        print("\n" + "="*60)
        print("📥 [EDGE DISPLAY RECEIVED AI PROMPT]")
        print(f"   Timestamp : {timestamp}")
        print(f"   Provocation: {question}")
        print("="*60 + "\n")
    except Exception as error:
        print(f"[ERROR] Failed to parse actuation message: {error}")


def main() -> None:
    """Initialize MQTT client and start publishing simulated sensor telemetry loop."""
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
    except Exception as error:
        print(f"[ERROR] Could not connect to MQTT broker: {error}")
        print("Hint: Make sure Docker containers are running (docker compose up -d)")
        return

    # Start non-blocking network loop for receiving messages
    client.loop_start()

    print("[MOCK IOT STARTED] Pumping sensor telemetry data... (Press Ctrl+C to stop)\n")

    try:
        counter = 0
        while True:
            counter += 1
            
            # Simulate normal work vs cognitive block scenarios
            # Every 5 iterations, simulate a stressed/stuck state to trigger the AI block detector
            if counter % 5 == 0:
                bpm = random.uniform(95.0, 110.0)  # Elevated heart rate
                idle_sec = random.uniform(12.0, 20.0)  # Long idle time
                manual_override = False
                print(f"[SIMULATION] Simulating COGNITIVE BLOCK condition (Iteration {counter})...")
            else:
                bpm = random.uniform(70.0, 80.0)  # Normal heart rate
                idle_sec = random.uniform(1.0, 4.0)   # Normal active typing
                manual_override = False

            telemetry_payload = {
                "heart_rate_bpm": round(bpm, 1),
                "keystroke_idle_sec": round(idle_sec, 1),
                "manual_override": manual_override,
                "client_timestamp": time.time()
            }

            client.publish(TOPIC_TELEMETRY, json.dumps(telemetry_payload))
            print(f"-> Sent Telemetry | BPM: {telemetry_payload['heart_rate_bpm']} | Idle: {telemetry_payload['keystroke_idle_sec']}s")

            # Wait 6 seconds between packets
            time.sleep(6.0)

    except KeyboardInterrupt:
        print("\n[MOCK IOT] Stopping simulation...")
        client.loop_stop()
        client.disconnect()
        print("[MOCK IOT] Disconnected gracefully.")


if __name__ == "__main__":
    main()