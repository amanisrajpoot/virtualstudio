"""Schemas for Render Orchestration."""

from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Any, List

class RenderStatus(str, Enum):
    CREATED = "Created"
    COMPILING = "Compiling"
    PLANNING = "Planning"
    GENERATING_DIALOGUE = "GeneratingDialogue"
    GENERATING_AUDIO = "GeneratingAudio"
    BUILDING_MANIFEST = "BuildingManifest"
    STREAMING_ASSETS = "StreamingAssets"
    READY = "Ready"
    RENDERING = "Rendering"
    EXPORTING = "Exporting"
    COMPLETED = "Completed"
    FAILED = "Failed"

class ReadinessTracker(BaseModel):
    assets_ready: bool = False
    audio_ready: bool = False
    camera_ready: bool = False
    timeline_ready: bool = False

    @property
    def all_ready(self) -> bool:
        return self.assets_ready and self.audio_ready and self.camera_ready and self.timeline_ready

class RenderJob(BaseModel):
    job_id: str
    story_id: str
    status: RenderStatus = RenderStatus.CREATED
    readiness: ReadinessTracker = Field(default_factory=ReadinessTracker)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RenderManifest(BaseModel):
    """The exact package sent to the Godot Renderer."""
    story_id: str
    timeline_id: str
    audio_assets: List[str] = []
    visual_assets: List[str] = []
    camera_track: Dict[str, Any] = {}
