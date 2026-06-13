"""Verification Tests for Subsystem 30 (Asset Marketplace)."""

import os
import shutil
import time
from backend.repositories.marketplace import MarketplaceRepository
from backend.repositories.characters import CharacterRepository
from backend.models.character import CharacterProfile, VoiceProfileRef, AppearanceProfile, BehaviorProfile
from backend.models.marketplace import AssetType

def test_marketplace():
    test_dir = "data/test_marketplace_dir"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
        
    repo = MarketplaceRepository(data_dir=test_dir)
    char_repo = CharacterRepository()
    
    # Setup initial Character
    source_char = CharacterProfile(
        id="char_mock_1", name="Halku",
        voice_profile=VoiceProfileRef(provider="elevenlabs", profile_id="v1", language="en"),
        appearance=AppearanceProfile(description="Farmer"),
        behavior=BehaviorProfile(),
        speech_style="Clever",
        archetype="Farmer"
    )
    char_repo.save(source_char)

    # Test 1 & 8 & 10: Publish Character (with dependencies & health)
    pub_data = {
        "asset_type": AssetType.CHARACTER,
        "source_id": "char_mock_1",
        "title": "Halku",
        "description": "A clever farmer.",
        "tags": ["comedy", "villager"],
        "compatible_goals": ["SELL_PRODUCT"],
        "required_assets": ["Village Base Voice"],
        "health_score": 90
    }
    asset = repo.publish_asset(pub_data, "user_alpha")
    
    assert asset.title == "Halku"
    assert asset.asset_type == AssetType.CHARACTER
    assert asset.health_score == 90
    assert "Village Base Voice" in asset.required_assets
    print("Test 1, 8, 10 (Publish, Health, Dependencies) passed.")
    
    # Test 2 & 6: Fork Asset (creates physical clone and lineage)
    forked_asset = repo.fork_asset(asset.asset_id, "user_beta")
    assert forked_asset.title == "Halku (Fork)"
    assert forked_asset.author_id == "user_beta"
    assert forked_asset.lineage.parent_asset_id == asset.asset_id
    assert forked_asset.lineage.depth == 1
    
    # Verify Physical Clone
    assert forked_asset.source_id != "char_mock_1"
    cloned_char = char_repo.get(forked_asset.source_id)
    assert cloned_char is not None
    assert "Fork" in cloned_char.name
    print("Test 2 & 6 (Fork & Physical Clone) passed.")
    
    # Test 3: Rating Aggregation
    repo.rate_asset(asset.asset_id, "user_1", 5)
    repo.rate_asset(asset.asset_id, "user_2", 4)
    repo.rate_asset(asset.asset_id, "user_3", 5)
    
    updated = repo.get_asset(asset.asset_id)
    assert updated.rating_count == 3
    assert updated.rating == 4.67
    print("Test 3 (Rating Aggregation) passed.")
    
    # Test 4: Compatibility Search
    res_match = repo.get_assets(goal_filter="SELL_PRODUCT")
    assert len(res_match) >= 1
    
    res_miss = repo.get_assets(goal_filter="MURDER_MYSTERY")
    assert len(res_miss) == 0
    print("Test 4 (Compatibility Search) passed.")
    
    # Test 5 & 9: Version Tracking & History
    pub_data["version_summary"] = "Fixed appearance"
    pub_data["description"] = "A clever farmer. Now with better clothes."
    repo.publish_asset(pub_data, "user_alpha")
    
    v2 = repo.get_asset(asset.asset_id)
    assert v2.versions[-1].version == 2
    assert len(v2.versions) == 2
    assert v2.versions[-1].summary == "Fixed appearance"
    assert v2.description == "A clever farmer. Now with better clothes."
    print("Test 5 & 9 (Version Tracking & History) passed.")
    
    # Test 7: Download Tracking
    repo.record_download(asset.asset_id)
    repo.record_download(asset.asset_id)
    repo.record_download(asset.asset_id)
    
    v3 = repo.get_asset(asset.asset_id)
    assert v3.downloads == 3
    print("Test 7 (Download Tracking) passed.")
    
if __name__ == "__main__":
    test_marketplace()
    print("All Marketplace tests passed!")
