"""Pydantic schemas for the Director Engine."""

from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel, Field, model_validator

class StoryBeat(BaseModel):
    intent: str
    actor: str
    target: str | None = None
    dialogue: str | None = None

class ActorEvent(BaseModel):
    time: float
    actor_id: str
    action: str
    target: Any = None
    context: dict[str, Any] = Field(default_factory=dict)

class CameraEvent(BaseModel):
    time: float
    preset: str
    target: str | None = None

class AudioEvent(BaseModel):
    time: float
    asset_id: str
    type: Literal["sfx", "music", "ambient"]
    volume_db: float = 0.0

class EffectEvent(BaseModel):
    time: float
    asset_id: str
    anchor: str | None = None
    duration: float = 0.0

class TrackSet(BaseModel):
    actor: list[ActorEvent] = Field(default_factory=list)
    camera: list[CameraEvent] = Field(default_factory=list)
    audio: list[AudioEvent] = Field(default_factory=list)
    effects: list[EffectEvent] = Field(default_factory=list)

class DirectedSequence(BaseModel):
    schema_version: str = "1.0"
    scene: str = ""
    duration: float = 0.0
    tracks: TrackSet = Field(default_factory=TrackSet)

    @model_validator(mode='after')
    def validate_monotonic_time(self) -> DirectedSequence:
        for track_name in ["actor", "camera", "audio", "effects"]:
            events = getattr(self.tracks, track_name)
            for i in range(1, len(events)):
                if events[i].time < events[i-1].time:
                    raise ValueError(f"Events in track '{track_name}' must be sorted by time (monotonic). Found {events[i].time} after {events[i-1].time}.")
        return self
