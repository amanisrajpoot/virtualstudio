"""Asset Registry Hooks for dependency lookup."""

from typing import List
from .schemas import StreamingLayer

# Mock registry exposing dependencies and layers for assets
ASSET_DB = {
    "char_halku_v1": {
        "dependencies": ["rig_human", "anim_idle"],
        "layer": StreamingLayer.CRITICAL
    },
    "char_policeman_v1": {
        "dependencies": ["rig_human", "anim_idle_police"],
        "layer": StreamingLayer.CRITICAL
    },
    "market_scene": {
        "dependencies": [],
        "layer": StreamingLayer.CRITICAL
    },
    "market_stall": {
        "dependencies": [],
        "layer": StreamingLayer.INTERACTION
    },
    "market_ambient_audio": {
        "dependencies": [],
        "layer": StreamingLayer.SECONDARY
    },
    "rig_human": {
        "dependencies": [],
        "layer": StreamingLayer.CRITICAL
    },
    "anim_idle": {
        "dependencies": [],
        "layer": StreamingLayer.INTERACTION
    },
    "anim_idle_police": {
        "dependencies": [],
        "layer": StreamingLayer.INTERACTION
    },
    "prop_baton": {
        "dependencies": [],
        "layer": StreamingLayer.INTERACTION
    }
}

def get_asset_dependencies(asset_id: str) -> List[str]:
    """Returns the list of immediate dependencies for a given asset."""
    if asset_id in ASSET_DB:
        return ASSET_DB[asset_id].get("dependencies", [])
    return []

def get_asset_layer(asset_id: str) -> StreamingLayer:
    """Returns the streaming layer of the asset."""
    if asset_id in ASSET_DB:
        return ASSET_DB[asset_id].get("layer", StreamingLayer.INTERACTION)
    return StreamingLayer.INTERACTION # Default
