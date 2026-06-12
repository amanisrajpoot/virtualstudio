"""Schemas for the Event Bus Subsystem."""

from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field

class EventCategory(str, Enum):
    DOMAIN = "domain"
    SYSTEM = "system"

class EventPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

class EventType(str, Enum):
    # Domain Events
    STORY_SUBMITTED = "StorySubmitted"
    STORY_COMPILED = "StoryCompiled"
    INTENT_MAPPED = "IntentMapped"
    SCENE_RESOLVED = "SceneResolved"
    BEAT_PLANNED = "BeatPlanned"
    BEAT_STAGED = "BeatStaged"
    DIALOGUE_PLANNED = "DialoguePlanned"
    DIALOGUE_GENERATED = "DialogueGenerated"
    AUDIO_REQUESTED = "AudioRequested"
    AUDIO_GENERATED = "AudioGenerated"
    AUDIO_CACHED = "AudioCached"
    CAMERA_TRACK_GENERATED = "CameraTrackGenerated"
    SHOT_SELECTED = "ShotSelected"
    TIMELINE_BUILT = "TimelineBuilt"

    SNAPSHOT_CREATED = "SnapshotCreated"
    WORLD_STATE_UPDATED = "WorldStateUpdated"
    ROLLBACK_PERFORMED = "RollbackPerformed"
    ASSET_LOADED = "AssetLoaded"
    ASSET_MISSING = "AssetMissing"
    ASSET_RESOLVED = "AssetResolved"
    ASSET_REQUESTED = "AssetRequested"
    ASSET_LOADING = "AssetLoading"
    ASSET_READY = "AssetReady"
    ASSET_CACHED = "AssetCached"
    ASSET_FAILED = "AssetFailed"
    MANIFEST_BUILT = "ManifestBuilt"
    
    # Orchestrator & Lifecycle Events
    RENDER_JOB_CREATED = "RenderJobCreated"
    RENDER_JOB_READY = "RenderJobReady"
    RENDER_STARTED = "RenderStarted"
    RENDER_COMPLETED = "RenderCompleted"
    RENDER_FAILED = "RenderFailed"
    EXPORT_STARTED = "ExportStarted"
    EXPORT_COMPLETED = "ExportCompleted"
    
    # Godot Renderer Adapter Events
    RENDER_PACKAGE_RECEIVED = "RenderPackageReceived"
    SCENE_CONSTRUCTED = "SceneConstructed"
    RECORDING_STARTED = "RecordingStarted"
    RECORDING_COMPLETED = "RecordingCompleted"
    GODOT_EXPORT_COMPLETED = "GodotExportCompleted"
    
    # System & Failure Events
    STORY_VALIDATION_FAILED = "StoryValidationFailed"
    SCENE_VALIDATION_FAILED = "SceneValidationFailed"
    INTENT_VALIDATION_FAILED = "IntentValidationFailed"
    SOLVER_FAILED = "SolverFailed"
    DIALOGUE_GENERATION_FAILED = "DialogueGenerationFailed"
    AUDIO_GENERATION_FAILED = "AudioGenerationFailed"
    SUBSCRIBER_FAILED = "SubscriberFailed"
    REPLAY_STARTED = "ReplayStarted"
    REPLAY_COMPLETED = "ReplayCompleted"

class EventMetadata(BaseModel):
    producer: str
    tags: list[str] = Field(default_factory=list)
    headers: dict = Field(default_factory=dict)

class EventEnvelope(BaseModel):
    event_id: str
    event_type: EventType
    event_category: EventCategory
    event_version: str = "1.0"
    timestamp: datetime
    correlation_id: str
    sequence_number: int
    priority: EventPriority = EventPriority.NORMAL
    metadata: EventMetadata
    payload: dict
