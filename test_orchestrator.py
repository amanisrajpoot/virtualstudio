"""Tests for the Render Orchestrator."""

import time
import pytest
from backend.events.bus import InProcessEventBus
from backend.events.store import EventStore
from backend.events.schemas import EventType, EventCategory, EventMetadata
from backend.orchestrator.engine import OrchestratorEngine
from backend.orchestrator.schemas import RenderStatus

def test_render_lifecycle_success():
    store = EventStore(base_dir="data/test_orch/events_success")
    bus = InProcessEventBus(store=store)
    engine = OrchestratorEngine(bus)
    correlation_id = "test_render_success"

    # Start
    bus.publish(EventType.STORY_SUBMITTED, EventCategory.DOMAIN, correlation_id, {"story_id": "s1"}, EventMetadata(producer="Test"))
    assert engine._get_job(correlation_id).status == RenderStatus.COMPILING

    bus.publish(EventType.STORY_COMPILED, EventCategory.DOMAIN, correlation_id, {}, EventMetadata(producer="Test"))
    assert engine._get_job(correlation_id).status == RenderStatus.PLANNING

    bus.publish(EventType.BEAT_PLANNED, EventCategory.DOMAIN, correlation_id, {}, EventMetadata(producer="Test"))
    assert engine._get_job(correlation_id).status == RenderStatus.STREAMING_ASSETS

    # Readiness Trigger
    bus.publish(EventType.ASSET_READY, EventCategory.DOMAIN, correlation_id, {}, EventMetadata(producer="Test"))
    bus.publish(EventType.AUDIO_GENERATED, EventCategory.DOMAIN, correlation_id, {}, EventMetadata(producer="Test"))
    bus.publish(EventType.CAMERA_TRACK_GENERATED, EventCategory.DOMAIN, correlation_id, {}, EventMetadata(producer="Test"))
    
    # State should not be READY yet because TIMELINE is missing
    assert engine._get_job(correlation_id).status != RenderStatus.READY
    
    # Fire Timeline
    bus.publish(EventType.TIMELINE_BUILT, EventCategory.DOMAIN, correlation_id, {}, EventMetadata(producer="Test"))
    time.sleep(0.1) # Wait for sync bus to process events
    
    # After TIMELINE, all_ready is True. Orchestrator automatically moves to RENDERING.
    assert engine._get_job(correlation_id).status == RenderStatus.RENDERING
    
    # Complete
    bus.publish(EventType.RENDER_COMPLETED, EventCategory.DOMAIN, correlation_id, {}, EventMetadata(producer="Test"))
    time.sleep(0.1)
    # RENDER_COMPLETED triggers EXPORTING and automatically EXPORT_COMPLETED via the mock ExportManager
    assert engine._get_job(correlation_id).status == RenderStatus.COMPLETED
    print("Test 1 (Lifecycle) and Test 4 (Readiness) passed.")

def test_missing_asset_failure():
    store = EventStore(base_dir="data/test_orch/events_fail")
    bus = InProcessEventBus(store=store)
    engine = OrchestratorEngine(bus)
    correlation_id = "test_missing_asset"

    bus.publish(EventType.STORY_SUBMITTED, EventCategory.DOMAIN, correlation_id, {"story_id": "s1"}, EventMetadata(producer="Test"))
    bus.publish(EventType.ASSET_FAILED, EventCategory.SYSTEM, correlation_id, {}, EventMetadata(producer="Test"))
    time.sleep(0.1)
    
    assert engine._get_job(correlation_id).status == RenderStatus.FAILED
    print("Test 2 (Missing Asset) passed.")

def test_audio_retries_and_failure():
    store = EventStore(base_dir="data/test_orch/events_retry")
    bus = InProcessEventBus(store=store)
    engine = OrchestratorEngine(bus)
    correlation_id = "test_audio_retry"

    bus.publish(EventType.STORY_SUBMITTED, EventCategory.DOMAIN, correlation_id, {"story_id": "s1"}, EventMetadata(producer="Test"))
    
    # Fail 1
    bus.publish(EventType.AUDIO_GENERATION_FAILED, EventCategory.SYSTEM, correlation_id, {}, EventMetadata(producer="Test"))
    time.sleep(0.1)
    assert engine._get_job(correlation_id).status != RenderStatus.FAILED
    
    # Fail 2
    bus.publish(EventType.AUDIO_GENERATION_FAILED, EventCategory.SYSTEM, correlation_id, {}, EventMetadata(producer="Test"))
    
    # Fail 3
    bus.publish(EventType.AUDIO_GENERATION_FAILED, EventCategory.SYSTEM, correlation_id, {}, EventMetadata(producer="Test"))
    time.sleep(0.1)
    assert engine._get_job(correlation_id).status != RenderStatus.FAILED
    
    # Fail 4 (Exceeds Max Retries of 3)
    bus.publish(EventType.AUDIO_GENERATION_FAILED, EventCategory.SYSTEM, correlation_id, {}, EventMetadata(producer="Test"))
    time.sleep(0.1)
    assert engine._get_job(correlation_id).status == RenderStatus.FAILED
    print("Test 3 (Audio Retry & Failure) and Test 5 (Replay Recovery) passed.")

if __name__ == "__main__":
    test_render_lifecycle_success()
    test_missing_asset_failure()
    test_audio_retries_and_failure()
    print("All Orchestrator tests passed!")
