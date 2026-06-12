"""Abstract and In-Process Event Bus implementations."""

import uuid
import traceback
from datetime import datetime, timezone
from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Any
from .schemas import EventType, EventCategory, EventPriority, EventMetadata, EventEnvelope
from .store import EventStore

class EventBus(ABC):
    @abstractmethod
    def subscribe(self, event_type: EventType, handler: Callable):
        pass

    @abstractmethod
    def unsubscribe(self, event_type: EventType, handler: Callable):
        pass

    @abstractmethod
    def publish(
        self,
        event_type: EventType,
        event_category: EventCategory,
        correlation_id: str,
        payload: dict,
        metadata: EventMetadata,
        priority: EventPriority = EventPriority.NORMAL
    ) -> EventEnvelope:
        pass


class InProcessEventBus(EventBus):
    def __init__(self, store: EventStore | None = None):
        self.subscribers: Dict[EventType, List[Callable]] = {}
        self.store = store or EventStore()

    def subscribe(self, event_type: EventType, handler: Callable):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        if handler not in self.subscribers[event_type]:
            self.subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: EventType, handler: Callable):
        if event_type in self.subscribers and handler in self.subscribers[event_type]:
            self.subscribers[event_type].remove(handler)

    def publish(
        self,
        event_type: EventType,
        event_category: EventCategory,
        correlation_id: str,
        payload: dict,
        metadata: EventMetadata,
        priority: EventPriority = EventPriority.NORMAL
    ) -> EventEnvelope:
        
        # 1. Generate Sequence Number and Timestamp
        seq_num = self.store.get_next_sequence_number(correlation_id)
        
        envelope = EventEnvelope(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            event_category=event_category,
            timestamp=datetime.now(timezone.utc),
            correlation_id=correlation_id,
            sequence_number=seq_num,
            priority=priority,
            metadata=metadata,
            payload=payload
        )
        
        # 2. Persist to Store
        self.store.save_event(envelope)
        
        # 3. Dispatch to Subscribers
        handlers = self.subscribers.get(event_type, [])
        for handler in handlers:
            try:
                handler(envelope)
            except Exception as e:
                # 4. Subscriber Failure Isolation
                error_msg = f"Subscriber '{handler.__name__}' failed: {str(e)}"
                error_trace = traceback.format_exc()
                print(f"[EventBus ERROR] {error_msg}")
                
                # Publish failure event recursively
                # Avoid infinite loop if SubscriberFailed handlers crash
                if event_type != EventType.SUBSCRIBER_FAILED:
                    self._publish_system_error(
                        correlation_id=correlation_id,
                        failed_event_type=event_type,
                        handler_name=handler.__name__,
                        error=error_msg,
                        trace=error_trace
                    )
                    
        return envelope

    def _publish_system_error(self, correlation_id: str, failed_event_type: EventType, handler_name: str, error: str, trace: str):
        self.publish(
            event_type=EventType.SUBSCRIBER_FAILED,
            event_category=EventCategory.SYSTEM,
            correlation_id=correlation_id,
            payload={
                "failed_event": failed_event_type.value,
                "handler": handler_name,
                "error": error,
                "traceback": trace
            },
            metadata=EventMetadata(producer="EventBus", tags=["error", "system"]),
            priority=EventPriority.CRITICAL
        )
