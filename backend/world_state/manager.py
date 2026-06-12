"""Core logic for managing persistent World State snapshots."""

import os
import json
import glob
from pathlib import Path
from datetime import datetime

from .schemas import StoryWorldState, SnapshotMetadata

class WorldStateManager:
    def __init__(self, storage_dir: str = "data/world_state"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_snapshot_path(self, version: int) -> Path:
        return self.storage_dir / f"snapshot_v{version}.json"

    def _get_latest_version(self) -> int:
        files = glob.glob(str(self.storage_dir / "snapshot_v*.json"))
        if not files:
            return 0
        versions = []
        for f in files:
            try:
                # Extract integer from 'snapshot_vX.json'
                base = os.path.basename(f)
                v = int(base.replace("snapshot_v", "").replace(".json", ""))
                versions.append(v)
            except ValueError:
                continue
        return max(versions) if versions else 0

    def load_latest(self) -> StoryWorldState | None:
        """Loads the most recent snapshot."""
        version = self._get_latest_version()
        if version == 0:
            return None
            
        path = self._get_snapshot_path(version)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return StoryWorldState(**data)

    def save_snapshot(self, state: StoryWorldState) -> int:
        """Saves a new snapshot, incrementing the version automatically."""
        latest_version = self._get_latest_version()
        new_version = latest_version + 1
        
        state.version = new_version
        path = self._get_snapshot_path(new_version)
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(state.model_dump_json(indent=2))
            
        return new_version

    def update_state(self, current: StoryWorldState, updates: dict, events: list) -> StoryWorldState:
        """
        Deep-merges updates into the current state and appends events.
        Does NOT commit to disk. Use save_snapshot() to commit.
        """
        # Create a deep copy using Pydantic
        new_state = StoryWorldState(**current.model_dump())
        
        # Merge entities
        if "entities" in updates:
            for entity_id, entity_data in updates["entities"].items():
                if entity_id in new_state.entities:
                    # Merge properties
                    if "properties" in entity_data:
                        new_state.entities[entity_id].properties.update(entity_data["properties"])
                else:
                    # Add new entity
                    # Note: expecting dict representation of EntityState here
                    from .schemas import EntityState
                    new_state.entities[entity_id] = EntityState(**entity_data)
                    
        # Update conditions
        if "conditions" in updates:
            for k, v in updates["conditions"].items():
                if hasattr(new_state.conditions, k):
                    setattr(new_state.conditions, k, v)
                    
        # Append events
        new_state.events.extend(events)
        
        return new_state

    def rollback(self, target_version: int) -> StoryWorldState | None:
        """
        Executes an append-only rollback.
        Copies the target_version and saves it as the newest version.
        """
        path = self._get_snapshot_path(target_version)
        if not path.exists():
            return None
            
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        # Create state from old data
        rolled_back_state = StoryWorldState(**data)
        
        # Save as new version
        new_v = self.save_snapshot(rolled_back_state)
        rolled_back_state.version = new_v
        
        return rolled_back_state

    def diff_state(self, old_state: StoryWorldState, new_state: StoryWorldState) -> dict:
        """Computes a simplistic diff between two states."""
        diff = {
            "entities_changed": [],
            "conditions_changed": {},
            "new_events": len(new_state.events) - len(old_state.events)
        }
        
        for e_id, new_ent in new_state.entities.items():
            if e_id not in old_state.entities:
                diff["entities_changed"].append(e_id)
            elif old_state.entities[e_id].properties != new_ent.properties:
                diff["entities_changed"].append(e_id)
                
        old_cond = old_state.conditions.model_dump()
        new_cond = new_state.conditions.model_dump()
        for k, v in new_cond.items():
            if old_cond.get(k) != v:
                diff["conditions_changed"][k] = {"from": old_cond.get(k), "to": v}
                
        return diff
