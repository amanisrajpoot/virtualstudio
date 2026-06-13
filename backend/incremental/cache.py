"""Semantic Two-Level Cache with Eviction."""

import json
import os
import datetime
from typing import Dict, Optional, List
from backend.models.incremental import SemanticCacheEntry, CacheMetadata, CompilationSnapshot
from backend.models.story_graph import BeatNode

class SemanticCache:
    def __init__(self, data_dir: str = "data/cache", max_entries: int = 5000):
        self.l1_dir = os.path.join(data_dir, "semantic", "l1") # fingerprint -> node
        self.l2_dir = os.path.join(data_dir, "semantic", "l2") # node_id -> preview state
        self.checkpoints_dir = os.path.join(data_dir, "checkpoints")
        self.max_entries = max_entries
        
        for d in [self.l1_dir, self.l2_dir, self.checkpoints_dir]:
            os.makedirs(d, exist_ok=True)

    def _get_l1_path(self, fingerprint: str) -> str:
        return os.path.join(self.l1_dir, f"{fingerprint}.json")

    def _get_l2_path(self, node_id: str) -> str:
        return os.path.join(self.l2_dir, f"{node_id}.json")

    def get_l1_entry(self, fingerprint: str) -> Optional[SemanticCacheEntry]:
        path = self._get_l1_path(fingerprint)
        if not os.path.exists(path):
            return None
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                entry = SemanticCacheEntry(**data)
                
                # Update hit count & last accessed
                entry.metadata.hit_count += 1
                entry.metadata.last_accessed = datetime.datetime.now().isoformat()
                self.save_l1_entry(entry, evict=False)
                
                return entry
        except Exception:
            return None

    def save_l1_entry(self, entry: SemanticCacheEntry, evict: bool = True):
        path = self._get_l1_path(entry.fingerprint)
        with open(path, 'w') as f:
            json.dump(entry.model_dump(), f, indent=2)
            
        if evict:
            self._evict_if_needed()

    def get_l2_preview(self, node_id: str) -> Optional[dict]:
        path = self._get_l2_path(node_id)
        if not os.path.exists(path):
            return None
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception:
            return None

    def save_l2_preview(self, node_id: str, preview_state: dict):
        path = self._get_l2_path(node_id)
        with open(path, 'w') as f:
            json.dump(preview_state, f, indent=2)

    def save_checkpoint(self, snapshot: CompilationSnapshot):
        path = os.path.join(self.checkpoints_dir, f"{snapshot.story_id}_v{snapshot.graph_version}.json")
        with open(path, 'w') as f:
            json.dump(snapshot.model_dump(), f, indent=2)

    def _evict_if_needed(self):
        """
        Basic Eviction Policy: Keep most recent max_entries based on last_accessed.
        """
        files = [os.path.join(self.l1_dir, f) for f in os.listdir(self.l1_dir) if f.endswith('.json')]
        if len(files) <= self.max_entries:
            return
            
        # Needs eviction. Parse metadata.
        entries_meta = []
        for path in files:
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    entries_meta.append({
                        "path": path,
                        "last_accessed": data["metadata"]["last_accessed"]
                    })
            except Exception:
                # Corrupt file, schedule for deletion
                entries_meta.append({"path": path, "last_accessed": "0"})
                
        # Sort by last_accessed descending
        entries_meta.sort(key=lambda x: x["last_accessed"], reverse=True)
        
        # Delete items beyond max_entries
        to_delete = entries_meta[self.max_entries:]
        for item in to_delete:
            try:
                os.remove(item["path"])
                # L2 eviction could also happen here, but for V1 we just prune L1
            except Exception:
                pass
