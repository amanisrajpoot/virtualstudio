"""JSON-backed World Repository."""

import os
import json
from typing import List, Optional
from backend.models.world import WorldProfile

class WorldRepository:
    def __init__(self, data_dir: str = "data/worlds"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

    def _get_path(self, world_id: str) -> str:
        return os.path.join(self.data_dir, f"{world_id}.json")

    def save(self, profile: WorldProfile) -> None:
        path = self._get_path(profile.id)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(profile.model_dump_json(indent=2))

    def get(self, world_id: str) -> Optional[WorldProfile]:
        path = self._get_path(world_id)
        if not os.path.exists(path):
            return None
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return WorldProfile(**data)

    def list(self) -> List[WorldProfile]:
        profiles = []
        if not os.path.exists(self.data_dir):
            return profiles
            
        for filename in os.listdir(self.data_dir):
            if filename.endswith(".json"):
                path = os.path.join(self.data_dir, filename)
                with open(path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        profiles.append(WorldProfile(**data))
                    except Exception as e:
                        print(f"Failed to load {filename}: {e}")
        return profiles

    def delete(self, world_id: str) -> bool:
        path = self._get_path(world_id)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False
