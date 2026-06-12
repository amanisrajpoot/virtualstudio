"""Mock Audio Engine for TTS Duration Measurement."""

import random

class AudioEngine:
    def generate_tts_and_measure(self, text: str, voice_id: str) -> tuple[str, float]:
        """
        Mocks passing the generated string to a TTS service (like ElevenLabs/Google),
        saving the .mp3, and measuring the exact duration.
        """
        # In a real app, we save an mp3 and run something like mutagen to get exact float duration
        audio_path = f"res://assets/audio/generated/{hash(text)}.mp3"
        
        # Mock calculation: roughly 0.15s per word for Hindi/Hinglish
        word_count = len(text.split())
        duration = word_count * 0.15
        
        # Add a little natural variance
        duration += random.uniform(0.1, 0.4)
        
        return audio_path, round(duration, 3)
