"""Tests for Asset Dependency & Streaming System."""

import pytest
import time
from backend.events.bus import InProcessEventBus
from backend.events.store import EventStore
from backend.events.schemas import EventType, EventCategory, EventMetadata
from backend.assets.builder import DependencyBuilder
from backend.assets.manager import StreamingManager

def test_dependency_builder():
    builder = DependencyBuilder()
    
    # 1. Test Bundle Unpacking & Recursive Expansion
    manifest = builder.build_manifest("story_test_1", ["market_core", "char_halku_v1"])
    
    required = manifest.required_assets
    assert "market_scene" in required
    assert "market_stall" in required
    assert "market_ambient_audio" in required
    assert "char_halku_v1" in required
    assert "rig_human" in required
    assert "anim_idle" in required
    
    # 2. Test Dependency Graph Integrity
    # char_halku_v1 -> rig_human
    # char_halku_v1 -> anim_idle
    edges = [(e.parent_id, e.child_id) for e in manifest.dependency_graph]
    assert ("char_halku_v1", "rig_human") in edges
    assert ("char_halku_v1", "anim_idle") in edges
    assert ("market_core", "market_scene") in edges
    
    # 3. Test Warm Starts
    # "market_scene" should now be in the builder's known cache. Let's build a new manifest asking for it.
    manifest2 = builder.build_manifest("story_test_2", ["market_scene"])
    assert "market_scene" in manifest2.warm_starts

def test_streaming_manager():
    store = EventStore(base_dir="data/test_assets/events")
    bus = InProcessEventBus(store=store)
    manager = StreamingManager(bus=bus)
    builder = DependencyBuilder()
    
    correlation_id = "story_test_streaming"
    
    # Generate Manifest
    manifest = builder.build_manifest(correlation_id, ["market_core", "char_policeman_v1", "missing_prop_123"])
    
    # Publish MANIFEST_BUILT to trigger the StreamingManager
    bus.publish(
        event_type=EventType.MANIFEST_BUILT,
        event_category=EventCategory.DOMAIN,
        correlation_id=correlation_id,
        payload={"manifest": manifest.model_dump()},
        metadata=EventMetadata(producer="Test")
    )
    
    time.sleep(0.1) # Sync
    events = store.load_events(correlation_id)
    event_types = [e.event_type for e in events]
    
    assert EventType.MANIFEST_BUILT in event_types
    assert EventType.ASSET_REQUESTED in event_types
    assert EventType.ASSET_READY in event_types
    assert EventType.ASSET_FAILED in event_types # Because missing_prop_123
    
    # Test Caching via second request
    correlation_id_2 = "story_test_streaming_2"
    manifest2 = builder.build_manifest(correlation_id_2, ["market_scene"]) # Already cached from test 1
    
    bus.publish(
        event_type=EventType.MANIFEST_BUILT,
        event_category=EventCategory.DOMAIN,
        correlation_id=correlation_id_2,
        payload={"manifest": manifest2.model_dump()},
        metadata=EventMetadata(producer="Test")
    )
    
    time.sleep(0.1)
    events2 = store.load_events(correlation_id_2)
    event_types2 = [e.event_type for e in events2]
    
    # Since market_scene is cached and a warm start, it should emit ASSET_CACHED
    assert EventType.ASSET_CACHED in event_types2
    assert EventType.ASSET_READY not in event_types2 # Bypassed loading completely

if __name__ == "__main__":
    test_dependency_builder()
    test_streaming_manager()
    print("All Asset System tests passed!")
