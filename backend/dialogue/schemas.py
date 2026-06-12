"""Schemas for the Dialogue Engine."""

from enum import Enum
from pydantic import BaseModel
from backend.director.staging_schemas import StagedBeat

class DialogueImportance(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class DialogueTags(BaseModel):
    speech_goal: str
    emotion: str
    importance: DialogueImportance
    response_expected: bool

class DialogueLine(BaseModel):
    speaker_id: str
    text: str
    language: str = "hinglish"
    tags: DialogueTags
    audio_path: str | None = None
    duration: float = 0.0

class DialogueBeat(StagedBeat):
    dialogue_line: DialogueLine | None = None
