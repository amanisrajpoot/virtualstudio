"""Project Packaging and Runtime Schemas."""

from pydantic import BaseModel
from typing import List, Optional

class ProjectRevision(BaseModel):
    revision_id: str
    graph_version: int
    summary: str
    timestamp: str

class ProjectManifest(BaseModel):
    project_id: str
    name: str
    description: str
    story_ids: List[str] = []
    character_ids: List[str] = []
    world_ids: List[str] = []
    active_story_id: Optional[str] = None
    active_snapshot_version: Optional[int] = None
    graph_version: int = 1
    revisions: List[ProjectRevision] = []
    members: List[dict] = [] # List[ProjectMember] dump
    approvals: List[dict] = [] # List[RevisionApproval] dump
    created_at: str
    updated_at: str

class ProjectSnapshot(BaseModel):
    project_id: str
    graph_version: int
    semantic_graph: dict # Dump of StoryGraph
    overrides: List[dict] # Dumps of GraphOverride
    preview_state: dict # Dump of PreviewPackage
