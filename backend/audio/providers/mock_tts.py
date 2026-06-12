"""Mock TTS Provider. Generates proportional silent .wav files."""

import wave
import struct
import math
from .base import TTSProvider
from backend.audio.schemas import VoiceProfile

class MockTTSProvider(TTSProvider):
    def generate_audio(self, text: str, profile: VoiceProfile, output_path: str) -> bool:
        # Calculate duration based on text length + speaking rate
        # Let's say normal rate is 100ms per character
        base_ms_per_char = 100
        if profile.speaking_rate == "fast":
            base_ms_per_char = 75
        elif profile.speaking_rate == "slow":
            base_ms_per_char = 125
            
        duration_ms = len(text) * base_ms_per_char
        duration_seconds = duration_ms / 1000.0
        
        # Audio specs
        sample_rate = 44100
        num_samples = int(sample_rate * duration_seconds)
        
        # Generate silent .wav
        try:
            with wave.open(output_path, 'w') as wav_file:
                wav_file.setnchannels(1) # Mono
                wav_file.setsampwidth(2) # 16-bit
                wav_file.setframerate(sample_rate)
                
                # Fill with silence (0s)
                data = struct.pack('<h', 0) * num_samples
                wav_file.writeframes(data)
            return True
        except Exception as e:
            print(f"[MockTTS] Failed to generate wav: {e}")
            return False
