import json
import os
import time
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

# Import core business logic modules from backend/core/
from backend.core.choice_engine import evaluate_choice_computing
from backend.core.reverse_hypothesis import generate_reverse_hypothesis

# Load environment variables from .env file located at project root
load_dotenv()

# MQTT Configuration from environment variables
MQTT_BROKER = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))
TOPIC_TELEMETRY = "synapse/sensors/telemetry"
TOPIC_ACTUATION = "synapse/actuator/prompt"

# Local LLM Configuration from environment variables
MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "llama3.2:1b")

# Operational Parameters
COOLDOWN_SECONDS = float(os.getenv("COOLDOWN_SECONDS", 30.0))
BLOCK_THRESHOLD = float(os.getenv("BLOCK_SCORE_THRESHOLD", 0.75))
CURRENT_TASK = os.getenv("CURRENT_TASK_CONTEXT", "Default engineering design task.")

# State tracking for idempotency and rate limiting
last_trigger_time = 0.0


def on_mqtt_message(client: mqtt.Client, userdata, msg: mqtt.MQTTMessage) -> None:
    """Callback handler for incoming MQTT telemetry messages from edge devices."""
    global last_trigger_time
    try:
        payload_data = json.loads(msg.payload.decode())
        bpm = float(payload_data.get("heart_rate_bpm", 75.0))
        idle = float(payload_data.get("keystroke_idle_sec", 0.0))
        override = payload_data.get("manual_override", False)

        block_score = evaluate_choice_computing(idle, bpm)
        current_time = time.time()

        print(
            f"[TELEMETRY] BPM: {bpm} | Idle: {idle}s | Block Score: {block_score}"
        )

        # Idempotency check: Trigger only if threshold is met and cooldown period has elapsed
        if (
            block_score >= BLOCK_THRESHOLD or override
        ) and current_time - last_trigger_time > COOLDOWN_SECONDS:
            last_trigger_time = current_time
            print(
                "\n>>> [COGNITIVE BLOCK DETECTED] Invoking Local LLM for Reverse Hypothesis..."
            )

            reversal_question = generate_reverse_hypothesis(CURRENT_TASK)
            print(f">>> [AI PROMPT GENERATED]: {reversal_question}\n")

            # Publish generated prompt back to edge device display topic
            actuation_payload = {
                "reversal_question": reversal_question,
                "timestamp": current_time,
            }
            client.publish(TOPIC_ACTUATION, json.dumps(actuation_payload))

    except Exception as error:
        print(f"[ERROR] Processing telemetry packet failed: {error}")


def main() -> None:
    """Initialize MQTT client loop and subscribe to sensor telemetry channels."""
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.subscribe(TOPIC_TELEMETRY)
    client.on_message = on_mqtt_message

    print(
        f"[BACKEND READY] Listening on broker {MQTT_BROKER}:{MQTT_PORT} using model '{MODEL_NAME}'... (Press Ctrl+C to exit)"
    )
    client.loop_forever()


if __name__ == "__main__":
    main()