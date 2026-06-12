"""Godot Renderer Adapter implementation."""

import threading
import time
from backend.events.bus import EventBus
from backend.events.schemas import EventType, EventCategory, EventMetadata
from .base import RendererAdapterInterface
from .schemas import RenderPackage

class GodotRendererAdapter(RendererAdapterInterface):
    def __init__(self, bus: EventBus):
        self.bus = bus

    def execute_render(self, package: RenderPackage) -> bool:
        # Step 1: Validate payload
        if "missing_asset" in package.asset_manifest.get("assets", []):
            self.bus.publish(
                EventType.ASSET_FAILED, EventCategory.SYSTEM,
                package.render_job_id, {"error": "Missing Asset"}, EventMetadata(producer="GodotAdapter")
            )
            return False

        # Step 2: Simulate sending JSON to Godot over IPC/Sockets
        self.bus.publish(
            EventType.RENDER_PACKAGE_RECEIVED, EventCategory.SYSTEM,
            package.render_job_id, {}, EventMetadata(producer="GodotAdapter")
        )

        # Step 3: Run the Godot simulation asynchronously
        threading.Thread(target=self._mock_godot_lifecycle, args=(package.render_job_id,)).start()
        return True

    def _mock_godot_lifecycle(self, job_id: str):
        """Mocks the telemetry that the real godot process would send back via IPC."""
        time.sleep(0.05)
        self.bus.publish(EventType.SCENE_CONSTRUCTED, EventCategory.SYSTEM, job_id, {}, EventMetadata(producer="GodotAdapter"))
        
        time.sleep(0.05)
        self.bus.publish(EventType.RECORDING_STARTED, EventCategory.SYSTEM, job_id, {}, EventMetadata(producer="GodotAdapter"))
        
        time.sleep(0.05)
        self.bus.publish(EventType.RECORDING_COMPLETED, EventCategory.SYSTEM, job_id, {}, EventMetadata(producer="GodotAdapter"))
        
        time.sleep(0.05)
        # Notify the Orchestrator that the file is entirely ready
        self.bus.publish(EventType.GODOT_EXPORT_COMPLETED, EventCategory.SYSTEM, job_id, {"path": "mp4"}, EventMetadata(producer="GodotAdapter"))
