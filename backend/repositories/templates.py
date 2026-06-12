"""Template, Goal, and Archetype Repository."""

import json
import os
from typing import List, Optional
from backend.models.story import StoryTemplate, StoryGoal, StoryArchetype

class TemplateRepository:
    def __init__(self, data_dir: str = "data/templates"):
        self.data_dir = data_dir
        self.templates_dir = os.path.join(data_dir, "templates")
        self.goals_file = os.path.join(data_dir, "goals.json")
        self.archetypes_file = os.path.join(data_dir, "archetypes.json")
        
        os.makedirs(self.templates_dir, exist_ok=True)

    # --- Templates ---
    def save_template(self, tpl: StoryTemplate) -> None:
        path = os.path.join(self.templates_dir, f"{tpl.id}.json")
        with open(path, 'w') as f:
            json.dump(tpl.model_dump(), f, indent=2)

    def get_template(self, tpl_id: str) -> Optional[StoryTemplate]:
        path = os.path.join(self.templates_dir, f"{tpl_id}.json")
        if not os.path.exists(path):
            return None
        with open(path, 'r') as f:
            return StoryTemplate(**json.load(f))

    def list_templates(self) -> List[StoryTemplate]:
        res = []
        for filename in os.listdir(self.templates_dir):
            if filename.endswith(".json"):
                with open(os.path.join(self.templates_dir, filename), 'r') as f:
                    res.append(StoryTemplate(**json.load(f)))
        return res

    # --- Goals ---
    def save_goals(self, goals: List[StoryGoal]) -> None:
        with open(self.goals_file, 'w') as f:
            json.dump([g.model_dump() for g in goals], f, indent=2)

    def list_goals(self) -> List[StoryGoal]:
        if not os.path.exists(self.goals_file):
            return []
        with open(self.goals_file, 'r') as f:
            return [StoryGoal(**x) for x in json.load(f)]

    # --- Archetypes ---
    def save_archetypes(self, archetypes: List[StoryArchetype]) -> None:
        with open(self.archetypes_file, 'w') as f:
            json.dump([a.model_dump() for a in archetypes], f, indent=2)

    def list_archetypes(self) -> List[StoryArchetype]:
        if not os.path.exists(self.archetypes_file):
            return []
        with open(self.archetypes_file, 'r') as f:
            return [StoryArchetype(**x) for x in json.load(f)]
