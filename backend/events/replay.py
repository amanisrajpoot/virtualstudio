"""Event Replay functionality."""

from typing import List, Optional
from .schemas import EventEnvelope, EventType, EventCategory, EventMetadata
from .bus import EventBus
from .store import EventStore

class EventReplayer:
    def __init__(self, bus: EventBus, store: EventStore | None = None):
        self.bus = bus
        self.store = store or EventStore()

    def _publish_replay_event(self, event_type: EventType, correlation_id: str, payload: dict):
        self.bus.publish(
            event_type=event_type,
            event_category=EventCategory.SYSTEM,
            correlation_id=correlation_id,
            payload=payload,
            metadata=EventMetadata(producer="EventReplayer", tags=["system", "replay"])
        )

    def replay(self, correlation_id: str) -> int:
        """Replays all events for a correlation ID."""
        events = self.store.load_events(correlation_id)
        if not events:
            return 0
            
        self._publish_replay_event(EventType.REPLAY_STARTED, correlation_id, {"mode": "full", "count": len(events)})
        
        count = 0
        for event in events:
            # Bypass generating a new sequence number/persisting by directly calling subscribers?
            # Or publish it again? If we publish, it generates new events.
            # For pure replay, we should just invoke subscribers directly using the historical envelope.
            self._dispatch_historical_event(event)
            count += 1
            
        self._publish_replay_event(EventType.REPLAY_COMPLETED, correlation_id, {"mode": "full", "replayed_count": count})
        return count

    def replay_until(self, correlation_id: str, target_event_type: EventType) -> int:
        """Replays events until a specific event type is encountered (inclusive)."""
        events = self.store.load_events(correlation_id)
        if not events:
            return 0
            
        self._publish_replay_event(EventType.REPLAY_STARTED, correlation_id, {"mode": "until", "target": target_event_type.value})
        
        count = 0
        for event in events:
            self._dispatch_historical_event(event)
            count += 1
            if event.event_type == target_event_type:
                break
                
        self._publish_replay_event(EventType.REPLAY_COMPLETED, correlation_id, {"mode": "until", "replayed_count": count})
        return count

    def replay_range(self, correlation_id: str, start_seq: int, end_seq: int) -> int:
        """Replays events within a specific sequence range [start_seq, end_seq] inclusive."""
        events = self.store.load_events(correlation_id)
        if not events:
            return 0
            
        self._publish_replay_event(EventType.REPLAY_STARTED, correlation_id, {"mode": "range", "start": start_seq, "end": end_seq})
        
        count = 0
        for event in events:
            if start_seq <= event.sequence_number <= end_seq:
                self._dispatch_historical_event(event)
                count += 1
                
        self._publish_replay_event(EventType.REPLAY_COMPLETED, correlation_id, {"mode": "range", "replayed_count": count})
        return count

    def _dispatch_historical_event(self, envelope: EventEnvelope):
        """Dispatches an already-persisted event to current subscribers without re-persisting."""
        # Using the bus's subscriber list directly
        # In a real app, the EventBus might expose a `dispatch_raw` method.
        handlers = getattr(self.bus, "subscribers", {}).get(envelope.event_type, [])
        for handler in handlers:
            try:
                handler(envelope)
            except Exception as e:
                print(f"[Replay ERROR] Handler {handler.__name__} failed on {envelope.event_type}: {e}")
