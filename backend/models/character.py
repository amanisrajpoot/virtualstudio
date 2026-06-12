"""Semantic Character Identity Schemas."""

from pydantic import BaseModel, Field
from typing import List, Optional

class VoiceProfileRef(BaseModel):
    provider: str
    profile_id: str
    language: str

class AppearanceProfile(BaseModel):
    description: str
    concept_images: List[str] = Field(default_factory=list)
    selected_concept: Optional[str] = None
    asset_id: Optional[str] = None

class BehaviorProfile(BaseModel):
    talkative: float = 0.5
    aggressive: float = 0.5
    energetic: float = 0.5
    greedy: float = 0.5
    curious: float = 0.5

class Relationship(BaseModel):
    target_id: str
    type: str # friend, enemy, mentor, customer, etc.
    strength: float = 0.5

class CharacterProfile(BaseModel):
    id: str
    name: str
    archetype: str
    tags: List[str] = Field(default_factory=list)
    voice_profile: VoiceProfileRef
    behavior: BehaviorProfile
    speech_style: str
    appearance: AppearanceProfile
    relationships: List[Relationship] = Field(default_factory=list)
