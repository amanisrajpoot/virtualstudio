"""Schemas for Voice and Audio processing."""

from pydantic import BaseModel, Field
from typing import Dict, Optional

class VoiceProfile(BaseModel):
    profile_id: str
    language: str
    speaking_rate: str
    energy: str
    humor: str = "normal"
    age_group: str = "adult"
    provider_voice: Dict[str, str] = Field(default_factory=dict)

class AudioAsset(BaseModel):
    asset_id: str
    path: str
    duration_ms: int
    voice_profile: str
    checksum: str
