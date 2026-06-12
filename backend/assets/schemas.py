"""Schemas for Asset Dependency and Streaming."""

from enum import Enum
from pydantic import BaseModel
from typing import Dict, List, Optional

class StreamingLayer(int, Enum):
    CRITICAL = 1      # Scenes, Characters
    INTERACTION = 2   # Props, Targeted Animations, Voice Audio
    SECONDARY = 3     # Ambient Audio, Crowd Variations, Background Props

class AssetState(str, Enum):
    UNREQUESTED = "Unrequested"
    REQUESTED = "Requested"
    LOADING = "Loading"
    READY = "Ready"
    CACHED = "Cached"
    FAILED = "Failed"

class DependencyEdge(BaseModel):
    parent_id: str
    child_id: str

class AssetManifest(BaseModel):
    """Immutable record of what assets a story requires."""
    story_id: str
    required_assets: List[str]
    dependency_graph: List[DependencyEdge]
    warm_starts: List[str]

class AssetLoadSession(BaseModel):
    """Mutable session tracking the streaming state of a manifest."""
    session_id: str
    manifest: AssetManifest
    asset_states: Dict[str, AssetState]
