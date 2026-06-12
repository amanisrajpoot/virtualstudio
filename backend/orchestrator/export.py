"""Export Manager for post-render packaging."""

from backend.events.bus import EventBus
from backend.events.schemas import EventType, EventCategory, EventMetadata

class ExportManager:
    def __init__(self, bus: EventBus):
        self.bus = bus

    def run_export(self, correlation_id: str, job_id: str):
        """Mock export process. Collects video/audio and encodes MP4."""
        self.bus.publish(
            event_type=EventType.EXPORT_STARTED,
            event_category=EventCategory.SYSTEM,
            correlation_id=correlation_id,
            payload={"job_id": job_id},
            metadata=EventMetadata(producer="ExportManager")
        )
        
        # In real system, wait for ffmpeg. Here we mock instant success.
        
        self.bus.publish(
            event_type=EventType.EXPORT_COMPLETED,
            event_category=EventCategory.SYSTEM,
            correlation_id=correlation_id,
            payload={"job_id": job_id, "output_path": "exports/video.mp4"},
            metadata=EventMetadata(producer="ExportManager")
        )
