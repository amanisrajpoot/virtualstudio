"""Story Repository."""

import json
import os
from typing import List, Optional
from backend.models.story import Story

class StoryRepository:
    def __init__(self, data_dir: str = "data/stories"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

    def _get_path(self, story_id: str) -> str:
        return os.path.join(self.data_dir, f"{story_id}.json")

    def save(self, story: Story) -> None:
        with open(self._get_path(story.id), 'w') as f:
            json.dump(story.model_dump(), f, indent=2)

    def get(self, story_id: str) -> Optional[Story]:
        path = self._get_path(story_id)
        if not os.path.exists(path):
            return None
        with open(path, 'r') as f:
            data = json.load(f)
            return Story(**data)

    def list(self) -> List[Story]:
        stories = []
        for filename in os.listdir(self.data_dir):
            if filename.endswith(".json"):
                path = os.path.join(self.data_dir, filename)
                with open(path, 'r') as f:
                    data = json.load(f)
                    stories.append(Story(**data))
        return stories
