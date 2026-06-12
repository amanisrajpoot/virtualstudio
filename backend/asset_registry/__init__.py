"""Asset Registry subsystem.

The registry is the canonical source for supported StoryForge assets. It does
not compile stories, direct cameras, render video, or expose UI behavior.
"""

from .constants import ASSET_TYPES, ASSET_TYPE_PREFIXES, RESOURCE_BACKED_TYPES
from .schemas import AssetCreate, AssetRead, AssetType, AssetUpdate

__all__ = [
    "ASSET_TYPES",
    "ASSET_TYPE_PREFIXES",
    "RESOURCE_BACKED_TYPES",
    "AssetCreate",
    "AssetRead",
    "AssetType",
    "AssetUpdate",
]
