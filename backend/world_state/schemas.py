"""Pydantic schemas for the World State Manager."""

from typing import Any
from pydantic import BaseModel, Field

class SnapshotMetadata(BaseModel):
    story_id: str
    episode_id: str
    title: str
    created_at: str

class EntityState(BaseModel):
    id: str
    type: str  # e.g., "character", "prop", "location"
    properties: dict[str, Any] = Field(default_factory=dict)

class WorldConditions(BaseModel):
    weather: str | None = None
    time_of_day: str | None = None
    market_status: str | None = None

class StoryEvent(BaseModel):
    event_id: str
    actor: str
    action: str
    target: str | None = None

class StoryWorldState(BaseModel):
    version: int
    metadata: SnapshotMetadata
    entities: dict[str, EntityState] = Field(default_factory=dict)
    conditions: WorldConditions = Field(default_factory=WorldConditions)
    events: list[StoryEvent] = Field(default_factory=list)

class RuntimeEntityState(BaseModel):
    position: dict[str, float]
    current_animation: str | None = None

class RuntimeWorldState(BaseModel):
    entities: dict[str, RuntimeEntityState] = Field(default_factory=dict)
