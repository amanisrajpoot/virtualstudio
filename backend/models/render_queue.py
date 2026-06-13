"""Render Control Plane Schemas."""

from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class RenderStatus(str, Enum):
    QUEUED = "queued"
    ASSIGNED = "assigned"
    DOWNLOADING_ASSETS = "downloading_assets"
    RENDERING = "rendering"
    UPLOADING = "uploading"
    COMPLETED = "completed"
    FAILED = "failed"

class RenderJob(BaseModel):
    job_id: str
    project_id: str
    snapshot_version: int
    approval_status: str
    status: RenderStatus
    submitted_by: str
    organization_id: Optional[str] = None
    submitted_at: str
    priority: int = 1
    retry_count: int = 0
    max_retries: int = 3
    worker_id: Optional[str] = None

class RenderJobSnapshot(BaseModel):
    job_id: str
    status: str
    worker_id: Optional[str] = None
    timestamp: str

class RenderArtifact(BaseModel):
    artifact_id: str
    job_id: str
    file_path: str
    file_size_bytes: int
    duration_ms: int
    resolution: str
    created_at: str

class WorkerInfo(BaseModel):
    worker_id: str
    status: str
    active_jobs: int
    capabilities: List[str]

class WorkerHeartbeat(BaseModel):
    worker_id: str
    timestamp: str
    cpu_usage: float
    memory_usage: float

class QueueMetrics(BaseModel):
    queued_jobs: int
    active_jobs: int
    completed_jobs: int
    failed_jobs: int
    average_render_ms: float
