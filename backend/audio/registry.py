"""Voice Registry."""

from typing import Dict, Optional
from .schemas import VoiceProfile

VOICE_PROFILES = {
    "halku_default": VoiceProfile(
        profile_id="halku_default",
        language="hinglish",
        speaking_rate="fast",
        energy="high",
        humor="high",
        provider_voice={"elevenlabs": "abc123_halku", "openai": "alloy"}
    ),
    "police_default": VoiceProfile(
        profile_id="police_default",
        language="hinglish",
        speaking_rate="normal",
        energy="medium",
        humor="low",
        provider_voice={"elevenlabs": "xyz456_police", "openai": "echo"}
    )
}

ACTOR_VOICE_MAP = {
    "char_halku_v1": "halku_default",
    "char_policeman_v1": "police_default"
}

def get_voice_profile(actor_id: str) -> Optional[VoiceProfile]:
    # Fallback to halku_default for testing if actor is unknown
    profile_id = ACTOR_VOICE_MAP.get(actor_id)
    if not profile_id:
        return None
    return VOICE_PROFILES.get(profile_id)
