"""Reverse Hypothesis Module for interacting with Local LLM (Ollama)

applying lateral thinking principles.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file located at project root
load_dotenv()

# Configuration loaded securely from environment variables
OLLAMA_URL = os.getenv(
    "OLLAMA_API_URL", "http://localhost:11434/api/generate"
)
MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "llama3.2:1b")


def generate_reverse_hypothesis(task_context: str) -> str:
    """Call local Ollama instance applying Edward De Bono's lateral thinking

    and Margaret Boden's transformational creativity to invert problem premises.

    Args:
        task_context (str): The current engineering task or problem description.

    Returns:
        str: A provocative, paradoxical question to break mental block.
    """
    prompt = (
        f"You are a Creative Thinking AI assistant. The user is stuck working on: '{task_context}'. "
        "Apply Edward De Bono's Lateral Thinking and Reverse Hypothesis: "
        "Invert the premise of the problem and propose ONE single provocative, paradoxical question "
        "to break their mental block. Maximum 20 words. No intro, output ONLY the question."
    )

    payload = {"model": MODEL_NAME, "prompt": prompt, "stream": False}

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=10)
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.exceptions.RequestException as error:
        print(f"[ERROR] Failed to connect to Ollama API: {error}")
        return "Reverse idea: What if the problem solved itself?"