"""Streaming Manager."""

import uuid
from typing import Dict, List
from backend.events.bus import EventBus
from backend.events.schemas import EventEnvelope, EventType, EventCategory, EventMetadata
from .schemas import AssetManifest, AssetLoadSession, AssetState, StreamingLayer
from .cache import AssetCache
from .registry_hooks import get_asset_layer, ASSET_DB

class StreamingManager:
    def __init__(self, bus: EventBus):
        self.bus = bus
        self.cache = AssetCache()
        self.active_sessions: Dict[str, AssetLoadSession] = {}
        
        # We would normally subscribe to MANIFEST_BUILT here, but for explicit testing control 
        # we'll expose a direct start_session method that handles the logic.
        self.bus.subscribe(EventType.MANIFEST_BUILT, self.handle_manifest_built)

    def handle_manifest_built(self, envelope: EventEnvelope):
        """Auto-starts streaming when a manifest is built."""
        manifest_data = envelope.payload.get("manifest")
        if not manifest_data:
            return
            
        manifest = AssetManifest(**manifest_data)
        self.start_session(envelope.correlation_id, manifest)

    def start_session(self, correlation_id: str, manifest: AssetManifest):
        session_id = f"sess_{uuid.uuid4().hex[:8]}"
        states = {asset: AssetState.UNREQUESTED for asset in manifest.required_assets}
        
        session = AssetLoadSession(
            session_id=session_id,
            manifest=manifest,
            asset_states=states
        )
        self.active_sessions[correlation_id] = session
        
        self._process_layers(correlation_id, session)

    def _process_layers(self, correlation_id: str, session: AssetLoadSession):
        """
        Processes assets by layer order. 
        In V1, we simulate synchronous layer execution for testing.
        Layer 1 -> Layer 2 -> Layer 3
        """
        # Group by layer
        layer_groups: Dict[StreamingLayer, List[str]] = {
            StreamingLayer.CRITICAL: [],
            StreamingLayer.INTERACTION: [],
            StreamingLayer.SECONDARY: []
        }
        
        for asset_id in session.manifest.required_assets:
            layer = get_asset_layer(asset_id)
            layer_groups[layer].append(asset_id)
            
        # Process sequentially
        for layer in [StreamingLayer.CRITICAL, StreamingLayer.INTERACTION, StreamingLayer.SECONDARY]:
            assets_in_layer = layer_groups[layer]
            if not assets_in_layer:
                continue
                
            for asset_id in assets_in_layer:
                self._request_asset(correlation_id, session, asset_id)

    def _request_asset(self, correlation_id: str, session: AssetLoadSession, asset_id: str):
        if session.asset_states[asset_id] != AssetState.UNREQUESTED:
            return
            
        session.asset_states[asset_id] = AssetState.REQUESTED
        self.bus.publish(
            event_type=EventType.ASSET_REQUESTED,
            event_category=EventCategory.DOMAIN,
            correlation_id=correlation_id,
            payload={"asset_id": asset_id, "session_id": session.session_id},
            metadata=EventMetadata(producer="StreamingManager")
        )
        
        # Mock load physics
        if asset_id not in ASSET_DB:
            session.asset_states[asset_id] = AssetState.FAILED
            self.bus.publish(
                event_type=EventType.ASSET_FAILED,
                event_category=EventCategory.SYSTEM,
                correlation_id=correlation_id,
                payload={"asset_id": asset_id, "error": "Unknown asset in registry"},
                metadata=EventMetadata(producer="StreamingManager")
            )
            return

        if self.cache.is_cached(asset_id) or asset_id in session.manifest.warm_starts:
            session.asset_states[asset_id] = AssetState.CACHED
            self.bus.publish(
                event_type=EventType.ASSET_CACHED,
                event_category=EventCategory.DOMAIN,
                correlation_id=correlation_id,
                payload={"asset_id": asset_id},
                metadata=EventMetadata(producer="StreamingManager")
            )
        else:
            session.asset_states[asset_id] = AssetState.LOADING
            # In real system, wait for async callback from Godot. Here we mock instant load.
            session.asset_states[asset_id] = AssetState.READY
            self.cache.mark_cached(asset_id)
            self.bus.publish(
                event_type=EventType.ASSET_READY,
                event_category=EventCategory.DOMAIN,
                correlation_id=correlation_id,
                payload={"asset_id": asset_id},
                metadata=EventMetadata(producer="StreamingManager")
            )
