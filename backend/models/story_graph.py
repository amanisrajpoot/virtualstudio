"""Story Graph and Semantic Node models."""

from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class NodeStatus(str, Enum):
    GENERATED = "generated"
    OVERRIDDEN = "overridden"
    LOCKED = "locked"
    DIRTY = "dirty"

class BeatNode(BaseModel):
    id: str
    intent: str
    beat_type: str = "action" # dialogue, action, reaction, transition
    dialogue: Optional[str] = None
    formation: Optional[str] = None
    zone: Optional[str] = None
    confidence: float = 100.0 # 0.0 to 100.0
    status: NodeStatus = NodeStatus.GENERATED
    next_nodes: List[str] = [] # Supports branching

class StoryGraph(BaseModel):
    story_id: str
    version: int = 1
    graph_health: int = 100
    nodes: List[BeatNode] = []

class GraphOverride(BaseModel):
    node_id: str
    story_id: str
    original_intent: str
    overridden_intent: str
    timestamp: str
