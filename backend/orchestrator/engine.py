"""Render Orchestrator Engine."""

import uuid
from typing import Dict
from backend.events.bus import EventBus
from backend.events.schemas import EventEnvelope, EventType, EventCategory, EventMetadata
from .schemas import RenderJob, RenderStatus, RenderManifest
from .retries import RetryManager
from .export import ExportManager
from backend.renderer.base import RendererAdapterInterface
from backend.renderer.schemas import RenderPackage, ExportSettings

class OrchestratorEngine:
    def __init__(self, bus: EventBus, renderer_adapter: RendererAdapterInterface = None):
        self.bus = bus
        self.adapter = renderer_adapter
        self.active_jobs: Dict[str, RenderJob] = {}
        self.retries = RetryManager(max_retries=3)
        self.exporter = ExportManager(bus)

        # Lifecycle Subscriptions
        self.bus.subscribe(EventType.STORY_SUBMITTED, self._on_story_submitted)
        self.bus.subscribe(EventType.STORY_COMPILED, self._on_story_compiled)
        self.bus.subscribe(EventType.BEAT_PLANNED, self._on_planned)
        self.bus.subscribe(EventType.BEAT_STAGED, self._on_staged)
        self.bus.subscribe(EventType.DIALOGUE_GENERATED, self._on_dialogue)
        
        # Readiness Subscriptions
        self.bus.subscribe(EventType.AUDIO_GENERATED, self._on_audio_ready)
        self.bus.subscribe(EventType.AUDIO_CACHED, self._on_audio_ready)
        self.bus.subscribe(EventType.ASSET_READY, self._on_asset_ready)
        self.bus.subscribe(EventType.ASSET_CACHED, self._on_asset_ready)
        self.bus.subscribe(EventType.CAMERA_TRACK_GENERATED, self._on_camera_ready)
        self.bus.subscribe(EventType.TIMELINE_BUILT, self._on_timeline_ready)
        
        # Failure Subscriptions
        self.bus.subscribe(EventType.AUDIO_GENERATION_FAILED, self._on_audio_failed)
        self.bus.subscribe(EventType.ASSET_FAILED, self._on_asset_failed)
        
        # Godot Mock Subscriptions
        self.bus.subscribe(EventType.GODOT_EXPORT_COMPLETED, self._on_godot_export_completed)
        self.bus.subscribe(EventType.EXPORT_COMPLETED, self._on_export_completed)

    def _get_job(self, correlation_id: str) -> RenderJob:
        return self.active_jobs.get(correlation_id)

    def _update_status(self, correlation_id: str, status: RenderStatus):
        job = self._get_job(correlation_id)
        if job and job.status != RenderStatus.FAILED:  # Don't overwrite FAILED state
            job.status = status

    def _fail_job(self, correlation_id: str, reason: str):
        job = self._get_job(correlation_id)
        if job and job.status != RenderStatus.FAILED:
            job.status = RenderStatus.FAILED
            self.bus.publish(
                event_type=EventType.RENDER_FAILED,
                event_category=EventCategory.SYSTEM,
                correlation_id=correlation_id,
                payload={"job_id": job.job_id, "reason": reason},
                metadata=EventMetadata(producer="Orchestrator")
            )

    def _check_readiness(self, correlation_id: str):
        job = self._get_job(correlation_id)
        if not job or job.status == RenderStatus.FAILED:
            return
            
        if job.readiness.all_ready and job.status != RenderStatus.READY:
            self._update_status(correlation_id, RenderStatus.READY)
            self.bus.publish(
                event_type=EventType.RENDER_JOB_READY,
                event_category=EventCategory.DOMAIN,
                correlation_id=correlation_id,
                payload={"job_id": job.job_id},
                metadata=EventMetadata(producer="Orchestrator")
            )
            
            # Auto-start rendering
            self._update_status(correlation_id, RenderStatus.RENDERING)
            self.bus.publish(
                event_type=EventType.RENDER_STARTED,
                event_category=EventCategory.DOMAIN,
                correlation_id=correlation_id,
                payload={"job_id": job.job_id},
                metadata=EventMetadata(producer="Orchestrator")
            )
            
            # Delegate to Adapter
            if self.adapter:
                package = RenderPackage(
                    render_job_id=correlation_id,
                    asset_manifest={"assets": []}, # Mock empty
                    timeline={},
                    camera_track={},
                    audio_assets={},
                    export_settings=ExportSettings()
                )
                self.adapter.execute_render(package)

    # --- Handlers ---
    
    def _on_story_submitted(self, envelope: EventEnvelope):
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        job = RenderJob(job_id=job_id, story_id=envelope.payload.get("story_id", "unknown"))
        self.active_jobs[envelope.correlation_id] = job
        
        self.bus.publish(
            event_type=EventType.RENDER_JOB_CREATED,
            event_category=EventCategory.DOMAIN,
            correlation_id=envelope.correlation_id,
            payload={"job_id": job_id},
            metadata=EventMetadata(producer="Orchestrator")
        )
        self._update_status(envelope.correlation_id, RenderStatus.COMPILING)

    def _on_story_compiled(self, envelope: EventEnvelope):
        self._update_status(envelope.correlation_id, RenderStatus.PLANNING)

    def _on_planned(self, envelope: EventEnvelope):
        self._update_status(envelope.correlation_id, RenderStatus.STREAMING_ASSETS)

    def _on_staged(self, envelope: EventEnvelope):
        self._update_status(envelope.correlation_id, RenderStatus.GENERATING_DIALOGUE)

    def _on_dialogue(self, envelope: EventEnvelope):
        self._update_status(envelope.correlation_id, RenderStatus.GENERATING_AUDIO)

    # --- Readiness Hook Updates ---

    def _on_audio_ready(self, envelope: EventEnvelope):
        job = self._get_job(envelope.correlation_id)
        if job:
            job.readiness.audio_ready = True
            self.retries.reset(envelope.correlation_id) # Reset retries on success
            self._check_readiness(envelope.correlation_id)

    def _on_asset_ready(self, envelope: EventEnvelope):
        job = self._get_job(envelope.correlation_id)
        if job:
            job.readiness.assets_ready = True
            self._check_readiness(envelope.correlation_id)

    def _on_camera_ready(self, envelope: EventEnvelope):
        job = self._get_job(envelope.correlation_id)
        if job:
            job.readiness.camera_ready = True
            self._check_readiness(envelope.correlation_id)

    def _on_timeline_ready(self, envelope: EventEnvelope):
        job = self._get_job(envelope.correlation_id)
        if job:
            job.readiness.timeline_ready = True
            self._check_readiness(envelope.correlation_id)

    # --- Failures & Retries ---
    
    def _on_asset_failed(self, envelope: EventEnvelope):
        # Assets shouldn't fail. If they do, immediate render fail.
        self._fail_job(envelope.correlation_id, "Missing visual asset.")

    def _on_audio_failed(self, envelope: EventEnvelope):
        correlation_id = envelope.correlation_id
        if self.retries.should_retry(correlation_id):
            # Replay the audio request specifically
            # In a real system, the payload would store exactly what to replay. 
            # We mock sending the event again:
            self.bus.publish(
                event_type=EventType.AUDIO_REQUESTED,
                event_category=EventCategory.DOMAIN,
                correlation_id=correlation_id,
                payload={}, # Simplified
                metadata=EventMetadata(producer="Orchestrator_Retry")
            )
        else:
            self._fail_job(correlation_id, "Audio generation failed after 3 retries.")

    # --- Culmination ---
    
    def _on_render_completed(self, envelope: EventEnvelope):
        pass # Replaced by GODOT_EXPORT_COMPLETED

    def _on_export_completed(self, envelope: EventEnvelope):
        self._update_status(envelope.correlation_id, RenderStatus.COMPLETED)
        
    def _on_godot_export_completed(self, envelope: EventEnvelope):
        job = self._get_job(envelope.correlation_id)
        if job:
            # Trigger final post-Godot export (e.g. cloud upload, watermarking) if needed
            self._update_status(envelope.correlation_id, RenderStatus.EXPORTING)
            self.exporter.run_export(envelope.correlation_id, job.job_id)
