"""Verification Tests for Subsystem 20 (Character Studio)."""

import os
from backend.models.character import (
    CharacterProfile, AppearanceProfile, VoiceProfileRef, BehaviorProfile, Relationship
)
from backend.repositories.characters import CharacterRepository
from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)

def test_persistence_and_relationships():
    repo = CharacterRepository(data_dir="data/test_characters")
    
    # 1. Create Halku
    halku = CharacterProfile(
        id="test_halku",
        name="Halku",
        archetype="merchant",
        tags=["desi", "funny"],
        voice_profile=VoiceProfileRef(provider="elevenlabs", profile_id="halku_v1", language="en-IN"),
        behavior=BehaviorProfile(talkative=0.8, aggressive=0.2, energetic=0.7, greedy=0.6, curious=0.5),
        speech_style="desi_hinglish",
        appearance=AppearanceProfile(description="Green giant in kurta"),
        relationships=[
            Relationship(target_id="test_policeman", type="enemy", strength=0.8)
        ]
    )
    
    # Save
    repo.save(halku)
    
    # Prove JSON exists
    assert os.path.exists("data/test_characters/test_halku.json")
    
    # Load into new instance to prove it reinstantiates properly
    loaded = repo.get("test_halku")
    assert loaded is not None
    assert loaded.name == "Halku"
    assert loaded.archetype == "merchant"
    assert len(loaded.relationships) == 1
    assert loaded.relationships[0].target_id == "test_policeman"
    assert loaded.relationships[0].type == "enemy"
    
    print("Test 4 (Persistence) and Test 5 (Relationship Graph) passed.")

def test_asset_generation_contract():
    # 1. Call the Generate Concept endpoint
    response = client.post("/api/characters/generate-concept", json={"description": "Green giant in kurta"})
    assert response.status_code == 200
    data = response.json()
    
    assert "job_id" in data
    assert data["status"] == "completed"
    assert len(data["images"]) == 3
    
    # 2. Simulate User Picking Image and saving profile
    repo = CharacterRepository(data_dir="data/test_characters")
    halku = repo.get("test_halku")
    
    halku.appearance.concept_images = data["images"]
    halku.appearance.selected_concept = data["images"][1] # Picks the second image
    repo.save(halku)
    
    # 3. Reload and verify the selected appearance persisted
    reloaded = repo.get("test_halku")
    assert reloaded.appearance.selected_concept == "/mock/halku_concept_2.png"
    
    print("Test 6 (Asset Generation Contract & Appearance Selection) passed.")

if __name__ == "__main__":
    test_persistence_and_relationships()
    test_asset_generation_contract()
    print("All Character Studio tests passed!")
