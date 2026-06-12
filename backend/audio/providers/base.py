"""Abstract base for TTS Providers."""

from abc import ABC, abstractmethod
from backend.audio.schemas import VoiceProfile

class TTSProvider(ABC):
    @abstractmethod
    def generate_audio(self, text: str, profile: VoiceProfile, output_path: str) -> bool:
        """
        Generates audio for the given text using the specified profile.
        Saves the audio to output_path.
        Returns True if successful, False otherwise.
        """
        pass
