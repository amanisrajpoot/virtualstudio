"""Story Trace Viewer for printing chronological event flows with performance timings."""

from datetime import datetime
from typing import List
from .schemas import EventEnvelope
from .store import EventStore

class StoryTraceViewer:
    def __init__(self, store: EventStore | None = None):
        self.store = store or EventStore()

    def view_trace(self, correlation_id: str) -> None:
        events = self.store.load_events(correlation_id)
        if not events:
            print(f"No events found for correlation_id: {correlation_id}")
            return
            
        print(f"\n{'='*50}")
        print(f" STORY TRACE: {correlation_id}")
        print(f"{'='*50}\n")
        
        last_timestamp: datetime | None = None
        total_duration_ms = 0.0
        
        for event in events:
            # Calculate duration from previous event
            duration_str = ""
            if last_timestamp is not None:
                delta = event.timestamp - last_timestamp
                duration_ms = delta.total_seconds() * 1000
                total_duration_ms += duration_ms
                duration_str = f" (+{duration_ms:.2f}ms)"
                
            last_timestamp = event.timestamp
            
            # Formatting
            seq = f"[{event.sequence_number}]"
            priority = f"({event.priority.value.upper()})"
            category = f"[{event.event_category.value.upper()}]"
            
            # Print row
            print(f"{seq:>5} {event.event_type.value:<25} {category:<10} {priority:<10} {duration_str}")
            
            # Print failure metadata if any
            if event.event_type == "SubscriberFailed":
                handler = event.payload.get("handler", "Unknown")
                err = event.payload.get("error", "Unknown error")
                print(f"      -> Failed Handler: {handler}")
                print(f"      -> Error: {err}")
                
        print(f"\n{'-'*50}")
        print(f" Total Trace Time: {total_duration_ms:.2f}ms")
        print(f"{'-'*50}\n")
