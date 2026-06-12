"""Graph Overrides Repository."""

import json
import os
from typing import List
from backend.models.story_graph import GraphOverride

class GraphOverrideRepository:
    def __init__(self, data_dir: str = "data/story_graph_overrides"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

    def _get_path(self, story_id: str) -> str:
        return os.path.join(self.data_dir, f"{story_id}.json")

    def save_override(self, override: GraphOverride) -> None:
        overrides = self.get_overrides(override.story_id)
        
        # Check if node already overridden, then update or append
        found = False
        for i, o in enumerate(overrides):
            if o.node_id == override.node_id:
                overrides[i] = override
                found = True
                break
                
        if not found:
            overrides.append(override)
            
        with open(self._get_path(override.story_id), 'w') as f:
            json.dump([o.model_dump() for o in overrides], f, indent=2)

    def get_overrides(self, story_id: str) -> List[GraphOverride]:
        path = self._get_path(story_id)
        if not os.path.exists(path):
            return []
        with open(path, 'r') as f:
            data = json.load(f)
            return [GraphOverride(**x) for x in data]
