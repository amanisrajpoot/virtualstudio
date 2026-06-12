"""Utilities for estimating sequence timings."""

def estimate_speech_duration(text: str | None) -> float:
    """
    Estimates the time it takes for TTS to speak the given text.
    Assumes an average speaking rate of 150 words per minute (2.5 words per second).
    We use character length to be slightly more precise (average 5 chars/word).
    Therefore, approx 12.5 characters per second.
    """
    if not text:
        return 0.0
        
    chars_per_second = 12.5
    duration = len(text) / chars_per_second
    
    # Add a minimum duration and a small padding for natural pauses
    return max(1.0, duration + 0.5)
