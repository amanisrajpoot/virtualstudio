"""Story, Template, Goal, and Archetype models."""

from pydantic import BaseModel
from typing import List, Optional

class Story(BaseModel):
    id: str
    title: str
    world_id: Optional[str] = None
    character_ids: List[str] = []
    goal_id: Optional[str] = None
    archetype_id: Optional[str] = None
    script: str = ""
    created_at: str
    updated_at: str

class StoryGoal(BaseModel):
    id: str
    name: str
    category: str
    supported_formations: List[str]
    supported_worlds: List[str]

class StoryArchetype(BaseModel):
    id: str
    name: str

class StoryTemplate(BaseModel):
    id: str
    name: str
    category: str
    difficulty: str
    world_id: str
    character_ids: List[str]
    goal_id: str
    archetype_id: str
    starter_script: str
