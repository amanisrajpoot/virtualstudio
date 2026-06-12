"""Semantic Simulation Preview Models."""

from pydantic import BaseModel
from typing import List, Optional

class PreviewState(BaseModel):
    current_beat_id: str
    active_zone: str
    active_path: List[str]
    visible_characters: List[str]
    active_dialogue: Optional[str]

class PreviewBeat(BaseModel):
    id: str
    time: float
    formation_id: str
    formation_visual: str
    intent: str
    dialogue: Optional[str]
    explanation: List[str]
    state_snapshot: PreviewState

class PreviewPackage(BaseModel):
    story_id: str
    world_id: Optional[str]
    characters: List[str]
    beats: List[PreviewBeat]
