"""Asset Cache Engine."""

from typing import Set

class AssetCache:
    def __init__(self):
        # In a real app, this tracks memory references or cached files.
        # For our architecture test, it simply tracks IDs that have been cached.
        self.cached_assets: Set[str] = set()

    def is_cached(self, asset_id: str) -> bool:
        return asset_id in self.cached_assets

    def mark_cached(self, asset_id: str):
        self.cached_assets.add(asset_id)
    
    def clear(self):
        self.cached_assets.clear()
