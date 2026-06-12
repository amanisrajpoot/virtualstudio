"""Verification Tests for Subsystem 24 (Story Templates)."""

import os
from backend.repositories.stories import StoryRepository
from backend.models.story import Story
from backend.templates.skeleton_generator import SkeletonGenerator
from backend.repositories.templates import TemplateRepository
from backend.scripts.seed_templates import seed
import datetime

def test_persistence():
    # Test 3: Story Persistence
    repo = StoryRepository(data_dir="data/test_stories")
    s = Story(
        id="test_story_1",
        title="Test Story",
        script="A script",
        created_at=datetime.datetime.now().isoformat(),
        updated_at=datetime.datetime.now().isoformat()
    )
    repo.save(s)
    
    loaded = repo.get("test_story_1")
    assert loaded is not None
    assert loaded.id == "test_story_1"
    assert loaded.script == "A script"
    print("Test 3 (Story Persistence) passed.")

def test_skeleton_generator():
    # Test 4: Skeleton Generation (Goal + Archetype)
    gen = SkeletonGenerator()
    script_comedy = gen.generate("market", ["Halku", "Sony"], "sell_product", "comedy")
    script_drama = gen.generate("market", ["Halku", "Sony"], "sell_product", "drama")
    
    assert script_comedy != script_drama
    assert "stall" in script_comedy.lower()
    assert "value" in script_drama.lower() or "desperate" in script_drama.lower()
    print("Test 4 (Skeleton Generation aware of Archetype) passed.")

def test_template_application():
    # Test 5: Template Application Schema
    seed() # Ensure data/templates has data
    repo = TemplateRepository("data/templates")
    tpl = repo.get_template("village_comedy")
    
    assert tpl is not None
    assert tpl.world_id == "village_market"
    assert tpl.goal_id == "sell_product"
    assert tpl.archetype_id == "comedy"
    assert tpl.starter_script != ""
    print("Test 5 (Template Application) passed.")

if __name__ == "__main__":
    os.makedirs("data/test_stories", exist_ok=True)
    test_persistence()
    test_skeleton_generator()
    test_template_application()
    print("All Templates tests passed!")
