"""Tests for Event Bus Subsystem."""

import uuid
import time
from backend.events.schemas import EventType, EventCategory, EventPriority, EventMetadata
from backend.events.bus import InProcessEventBus
from backend.events.store import EventStore
from backend.events.replay import EventReplayer
from backend.events.trace import StoryTraceViewer

def run_tests():
    # Setup
    store = EventStore(base_dir="data/test_events")
    bus = InProcessEventBus(store=store)
    replayer = EventReplayer(bus=bus, store=store)
    viewer = StoryTraceViewer(store=store)
    
    correlation_id = f"story_{uuid.uuid4().hex[:8]}"
    print(f"Using Correlation ID: {correlation_id}")
    
    # State tracking for subscribers
    state = {"received": [], "multi": 0}
    
    # Handlers
    def handler_1(event):
        state["received"].append(event.event_type)
        
    def handler_multi_a(event): state["multi"] += 1
    def handler_multi_b(event): state["multi"] += 1
    
    def handler_fail(event):
        raise ValueError("Simulated subscriber failure!")
        
    def handler_survivor(event):
        state["received"].append("survived")

    print("\n--- TEST 1: PUBLISH SINGLE EVENT ---")
    bus.subscribe(EventType.STORY_SUBMITTED, handler_1)
    
    bus.publish(
        event_type=EventType.STORY_SUBMITTED,
        event_category=EventCategory.DOMAIN,
        correlation_id=correlation_id,
        payload={"story": "test"},
        metadata=EventMetadata(producer="Test")
    )
    print(f"Received: {state['received']}")
    assert EventType.STORY_SUBMITTED in state["received"]

    print("\n--- TEST 2: MULTIPLE SUBSCRIBERS ---")
    bus.subscribe(EventType.STORY_COMPILED, handler_multi_a)
    bus.subscribe(EventType.STORY_COMPILED, handler_multi_b)
    
    time.sleep(0.01) # Small sleep to show duration in trace
    bus.publish(
        event_type=EventType.STORY_COMPILED,
        event_category=EventCategory.DOMAIN,
        correlation_id=correlation_id,
        payload={},
        metadata=EventMetadata(producer="Compiler")
    )
    print(f"Multi Count: {state['multi']} (Expected: 2)")
    assert state["multi"] == 2

    print("\n--- TEST 3: FAILURE ISOLATION ---")
    # Subscribing fail handler first, survivor second
    bus.subscribe(EventType.INTENT_MAPPED, handler_fail)
    bus.subscribe(EventType.INTENT_MAPPED, handler_survivor)
    
    time.sleep(0.01)
    bus.publish(
        event_type=EventType.INTENT_MAPPED,
        event_category=EventCategory.DOMAIN,
        correlation_id=correlation_id,
        payload={},
        metadata=EventMetadata(producer="Mapper")
    )
    # The fail handler should have crashed, but survivor should have received it
    print(f"Survived status: {'survived' in state['received']}")
    assert "survived" in state["received"]

    print("\n--- TEST 4: EVENT REPLAY ---")
    # Clear state
    state["received"].clear()
    state["multi"] = 0
    
    # We unsubscribe fail handler so it doesn't pollute replay output, 
    # but we'll leave it to show replay runs through existing bus subscribers
    bus.unsubscribe(EventType.INTENT_MAPPED, handler_fail)
    
    replayed_count = replayer.replay(correlation_id)
    # Note: Publish triggered: STORY_SUBMITTED, STORY_COMPILED, INTENT_MAPPED
    # BUT! INTENT_MAPPED also caused SUBSCRIBER_FAILED to be published internally.
    # So total persisted events should be 4!
    print(f"Replayed Count: {replayed_count}")
    assert replayed_count == 4
    
    print("\n--- TEST 5 & 6: TRACE VIEWER & FAILURE EVENT ---")
    viewer.view_trace(correlation_id)

if __name__ == "__main__":
    run_tests()
