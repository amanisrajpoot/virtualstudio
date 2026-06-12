"""Pydantic schemas for the Story Compiler outputs."""

from typing import Literal
from pydantic import BaseModel, Field

class StoryBeatDraft(BaseModel):
    intent: str
    intent_confidence: float = Field(..., ge=0.0, le=1.0)
    actor: str
    target: str | None = None
    object: str | None = None

class StoryDSLDraft(BaseModel):
    status: Literal["success", "needs_clarification"]
    unknown_concepts: list[str] = Field(default_factory=list)
    
    scene: str | None = None
    scene_confidence: float = Field(0.0, ge=0.0, le=1.0)
    
    characters: list[str] = Field(default_factory=list)
    beats: list[StoryBeatDraft] = Field(default_factory=list)
