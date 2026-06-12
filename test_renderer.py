"""Tests for Godot Renderer Adapter."""

import time
import pytest
from backend.events.bus import InProcessEventBus
from backend.events.store import EventStore
from backend.events.schemas import EventType, EventCategory, EventMetadata
from backend.renderer.schemas import RenderPackage, ExportSettings
from backend.renderer.godot_adapter import GodotRendererAdapter
from backend.orchestrator.engine import OrchestratorEngine

def test_godot_adapter_missing_asset():
    store = EventStore(base_dir="data/test_renderer/events_missing")
    bus = InProcessEventBus(store=store)
    adapter = GodotRendererAdapter(bus)
    
    package = RenderPackage(
        render_job_id="test_missing_123",
        asset_manifest={"assets": ["char_halku", "missing_asset"]},
        timeline={},
        camera_track={},
        audio_assets={},
        export_settings=ExportSettings()
    )
    
    # Should immediately fail due to validation
    success = adapter.execute_render(package)
    assert not success
    
    events = store.load_events("test_missing_123")
    assert EventType.ASSET_FAILED in [e.event_type for e in events]
    print("Test 7 (Missing Asset) passed.")

def test_godot_adapter_success_lifecycle():
    store = EventStore(base_dir="data/test_renderer/events_success")
    bus = InProcessEventBus(store=store)
    adapter = GodotRendererAdapter(bus)
    correlation_id = "test_godot_lifecycle"
    
    package = RenderPackage(
        render_job_id=correlation_id,
        asset_manifest={"assets": ["char_halku"]},
        timeline={"data": "mock_timeline"},
        camera_track={"data": "mock_camera"},
        audio_assets={"data": "mock_audio"},
        export_settings=ExportSettings()
    )
    
    success = adapter.execute_render(package)
    assert success
    
    # Wait for the mocked async godot lifecycle to finish
    time.sleep(0.3)
    
    events = store.load_events(correlation_id)
    types = [e.event_type for e in events]
    
    assert EventType.RENDER_PACKAGE_RECEIVED in types
    assert EventType.SCENE_CONSTRUCTED in types
    assert EventType.RECORDING_STARTED in types
    assert EventType.RECORDING_COMPLETED in types
    assert EventType.GODOT_EXPORT_COMPLETED in types
    print("Tests 1-6 (Godot Lifecycle) passed.")

def test_orchestrator_e2e_integration():
    store = EventStore(base_dir="data/test_renderer/events_e2e")
    bus = InProcessEventBus(store=store)
    adapter = GodotRendererAdapter(bus)
    
    # Inject adapter into orchestrator
    engine = OrchestratorEngine(bus, renderer_adapter=adapter)
    correlation_id = "test_e2e_full"
    
    # Trigger full backend flow
    bus.publish(EventType.STORY_SUBMITTED, EventCategory.DOMAIN, correlation_id, {}, EventMetadata(producer="Test"))
    bus.publish(EventType.STORY_COMPILED, EventCategory.DOMAIN, correlation_id, {}, EventMetadata(producer="Test"))
    bus.publish(EventType.BEAT_PLANNED, EventCategory.DOMAIN, correlation_id, {}, EventMetadata(producer="Test"))
    
    # Satisfy Readiness Gates
    bus.publish(EventType.ASSET_READY, EventCategory.DOMAIN, correlation_id, {}, EventMetadata(producer="Test"))
    bus.publish(EventType.AUDIO_GENERATED, EventCategory.DOMAIN, correlation_id, {}, EventMetadata(producer="Test"))
    bus.publish(EventType.CAMERA_TRACK_GENERATED, EventCategory.DOMAIN, correlation_id, {}, EventMetadata(producer="Test"))
    bus.publish(EventType.TIMELINE_BUILT, EventCategory.DOMAIN, correlation_id, {}, EventMetadata(producer="Test"))
    
    # Timeline Built unlocks RENDERING state and calls adapter.execute_render
    time.sleep(0.3) # Wait for Godot adapter to complete its async lifecycle
    
    events = store.load_events(correlation_id)
    types = [e.event_type for e in events]
    
    # Prove the Orchestrator successfully triggered the Adapter and processed the callback
    assert EventType.RENDER_STARTED in types
    assert EventType.RENDER_PACKAGE_RECEIVED in types
    assert EventType.GODOT_EXPORT_COMPLETED in types
    assert EventType.EXPORT_COMPLETED in types # Final Orchestrator wrap-up
    print("Test 8 (E2E Integration) passed.")

if __name__ == "__main__":
    test_godot_adapter_missing_asset()
    test_godot_adapter_success_lifecycle()
    test_orchestrator_e2e_integration()
    print("All Renderer Adapter tests passed!")
