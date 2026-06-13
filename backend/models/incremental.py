"""Incremental Compilation Schemas."""

from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class DirtyReason(str, Enum):
    CONTENT_CHANGED = "content_changed"
    UPSTREAM_CHANGED = "upstream_changed"
    OVERRIDE_CHANGED = "override_changed"
    WORLD_CHANGED = "world_changed"
    CHARACTER_CHANGED = "character_changed"

class CompilationUnit(BaseModel):
    node_id: str
    node_hash: str
    dependency_hash: str
    fingerprint: str
    dirty: bool
    dirty_reason: Optional[DirtyReason] = None
    last_compiled_at: str

class CacheMetadata(BaseModel):
    created_at: str
    last_accessed: str
    hit_count: int

class SemanticCacheEntry(BaseModel):
    fingerprint: str
    graph_node_data: dict
    metadata: CacheMetadata

class CompilationSnapshot(BaseModel):
    story_id: str
    graph_version: int
    compiled_nodes: List[str]
    health_score: int
    timestamp: str
