"""JSON-backed Character Repository."""

import os
import json
from typing import List, Optional
from backend.models.character import CharacterProfile

class CharacterRepository:
    def __init__(self, data_dir: str = "data/characters"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

    def _get_path(self, character_id: str) -> str:
        return os.path.join(self.data_dir, f"{character_id}.json")

    def save(self, profile: CharacterProfile) -> None:
        path = self._get_path(profile.id)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(profile.model_dump_json(indent=2))

    def get(self, character_id: str) -> Optional[CharacterProfile]:
        path = self._get_path(character_id)
        if not os.path.exists(path):
            return None
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return CharacterProfile(**data)

    def list(self) -> List[CharacterProfile]:
        profiles = []
        if not os.path.exists(self.data_dir):
            return profiles
            
        for filename in os.listdir(self.data_dir):
            if filename.endswith(".json"):
                path = os.path.join(self.data_dir, filename)
                with open(path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        profiles.append(CharacterProfile(**data))
                    except Exception as e:
                        print(f"Failed to load {filename}: {e}")
        return profiles

    def delete(self, character_id: str) -> bool:
        path = self._get_path(character_id)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False
