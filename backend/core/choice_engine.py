"""Choice Engine Module for evaluating cognitive block scores based on telemetry."""


def evaluate_choice_computing(keystroke_idle: float, bpm: float) -> float:
    """Evaluate cognitive block score fusing behavioral metrics and biometric telemetry.

    Args:
        keystroke_idle (float): Idle time in seconds since the last keystroke.
        bpm (float): Current heart rate in beats per minute.

    Returns:
        float: Normalized cognitive block score between 0.0 and 1.0.
    """
    # Normalize idle time (assuming 10+ seconds of inactivity indicates cognitive friction)
    idle_score = min(keystroke_idle / 10.0, 1.0)

    # Normalize stress score based on a baseline resting heart rate of 75.0 BPM
    stress_score = max(0.0, min((bpm - 75.0) / 25.0, 1.0))

    # Weighted fusion: 60% behavioral inertia, 40% biometric stress response
    total_score = (0.6 * idle_score) + (0.4 * stress_score)
    return round(total_score, 2)