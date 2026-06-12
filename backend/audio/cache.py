"""Audio Cache Engine."""

import os
import json
import hashlib
from pathlib import Path
from typing import Optional
from .schemas import AudioAsset

class AudioCache:
    def __init__(self, cache_dir: str = "data/audio_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.cache_dir / "index.json"
        self._load_index()

    def _load_index(self):
        if self.index_path.exists():
            with open(self.index_path, "r") as f:
                self.index = json.load(f)
        else:
            self.index = {}

    def _save_index(self):
        with open(self.index_path, "w") as f:
            json.dump(self.index, f, indent=2)

    def generate_key(self, text: str, profile_id: str) -> str:
        raw = f"{text}:{profile_id}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get(self, cache_key: str) -> Optional[AudioAsset]:
        if cache_key in self.index:
            data = self.index[cache_key]
            # Verify file exists
            if Path(data["path"]).exists():
                return AudioAsset(**data)
        return None

    def put(self, cache_key: str, asset: AudioAsset):
        self.index[cache_key] = asset.model_dump()
        self._save_index()
