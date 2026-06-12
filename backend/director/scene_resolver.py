"""Scene Resolver maps semantic AnchorIntents to exact Asset Registry nodes."""

import json
from typing import Dict, Any
from .staging_schemas import StagedBeat, ResolvedBlockingDirective, AnchorIntent

# Fallback strategies for when a specific zone isn't available
FALLBACK_STRATEGIES = {
    AnchorIntent.NEAREST_SELLING_ZONE: ["selling_zone", "neutral_zone", "entry_zone"],
    AnchorIntent.NEAREST_REST_ZONE: ["rest_zone", "neutral_zone"],
    AnchorIntent.NEAREST_CONVERSATION_ZONE: ["conversation_zone", "neutral_zone", "rest_zone"],
    AnchorIntent.NEAREST_INTERROGATION_ZONE: ["interrogation_zone", "neutral_zone", "scene_center"],
    AnchorIntent.NEAREST_GROUP_ZONE: ["group_zone", "neutral_zone"],
    AnchorIntent.SCENE_CENTER: ["neutral_zone", "entry_zone"],
    AnchorIntent.SCENE_ENTRY: ["entry_zone", "neutral_zone"],
    AnchorIntent.SCENE_EXIT: ["exit_zone", "entry_zone", "neutral_zone"],
}

class SceneResolutionCache:
    """Caches scene metadata to avoid repeated DB calls during resolution."""
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        
    def load_scene_metadata(self, scene_id: str) -> Dict[str, Any]:
        """Loads scene metadata. In real app, fetches from AssetRegistry database."""
        if scene_id in self._cache:
            return self._cache[scene_id]
            
        # Mocking the DB fetch for village_market_v1 based on 001_asset_registry_v1.sql
        if scene_id == "scene_village_market_v1":
            metadata_str = '{"vertical_safe_area":true,"interaction_zones":[{"id":"market_stall","type":"selling_zone","priority":100,"capacity":1,"adjacent":["stall_front"]},{"id":"stall_front","type":"customer_zone","priority":80,"capacity":2,"adjacent":["scene_center"]},{"id":"scene_center","type":"neutral_zone","priority":50,"capacity":10,"adjacent":["entrance","tree_area"]},{"id":"tree_area","type":"rest_zone","priority":20,"capacity":3,"adjacent":["scene_center"]},{"id":"entrance","type":"entry_zone","priority":10,"capacity":5,"adjacent":["scene_center"]}]}'
            self._cache[scene_id] = json.loads(metadata_str)
        elif scene_id == "scene_empty_v1":
            self._cache[scene_id] = {"interaction_zones": []}
        else:
            raise ValueError(f"Scene {scene_id} not found in registry.")
            
        return self._cache[scene_id]

class SceneResolver:
    def __init__(self):
        self.cache = SceneResolutionCache()
        
    def resolve_beat(self, beat: StagedBeat, scene_id: str) -> StagedBeat:
        """Resolves abstract AnchorIntents into actual resolved_anchors."""
        metadata = self.cache.load_scene_metadata(scene_id)
        interaction_zones = metadata.get("interaction_zones", [])
        
        # Sort zones by priority descending
        interaction_zones.sort(key=lambda x: x.get("priority", 0), reverse=True)
        
        for blocking in beat.blocking:
            resolved_anchor = None
            
            # If the intent is to anchor to another actor, just pass it through
            if blocking.anchor_intent in [AnchorIntent.TARGET_FRONT, AnchorIntent.TARGET_FLANK]:
                resolved_anchor = f"offset_{blocking.anchor_intent.value}"
            elif blocking.anchor_intent:
                # Find the required zone types via fallback strategy
                allowed_zone_types = FALLBACK_STRATEGIES.get(blocking.anchor_intent, [])
                
                # Search for the highest priority zone that matches an allowed type
                for allowed_type in allowed_zone_types:
                    match = next((z for z in interaction_zones if z["type"] == allowed_type), None)
                    if match:
                        resolved_anchor = match["id"]
                        beat.planner_reasoning.append(f"Resolver: Mapped {blocking.anchor_intent} to '{resolved_anchor}' (type: {allowed_type}).")
                        break
                        
                if not resolved_anchor:
                    beat.planner_reasoning.append(f"Resolver WARNING: Could not resolve {blocking.anchor_intent}. No fallback zones found.")
                    resolved_anchor = "fallback_origin"
                    
            resolved_directive = ResolvedBlockingDirective(
                **blocking.model_dump(),
                resolved_anchor=resolved_anchor
            )
            beat.resolved_blocking.append(resolved_directive)
            
        return beat
