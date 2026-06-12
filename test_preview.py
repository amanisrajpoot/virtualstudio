"""Verification Tests for Subsystem 22 (Live Scene Preview)."""

from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)

def test_intent_detection():
    # Test 10: Rule-Based Intent Engine works
    r_sell = client.post("/api/preview/build", json={"text": "Halku sells moonlight", "world_id": "market", "characters": ["c1"]}).json()
    assert r_sell["beats"][1]["intent"] == "SELL_PRODUCT"
    
    r_argue = client.post("/api/preview/build", json={"text": "Policeman argues", "world_id": "market", "characters": ["c1"]}).json()
    assert r_argue["beats"][1]["intent"] == "CONFRONT"
    
    r_run = client.post("/api/preview/build", json={"text": "They run away", "world_id": "market", "characters": ["c1"]}).json()
    assert r_run["beats"][1]["intent"] == "CHASE"
    
    print("Test 10 (Rule-Based Intent Detection logic) passed.")

def test_timeline_integrity():
    r = client.post("/api/preview/build", json={"text": "Halku sells moonlight"}).json()
    beats = r["beats"]
    
    # Test 2: Sequential time
    assert beats[0]["time"] < beats[1]["time"]
    
    # Test 3: Formation Schema
    assert "formation_id" in beats[0]
    assert "formation_visual" in beats[0]
    
    # Test 8: Scrubbing Integrity (Snapshots exist)
    assert "state_snapshot" in beats[0]
    assert "active_path" in beats[0]["state_snapshot"]
    
    # Test 6: Explanation generation
    assert len(beats[0]["explanation"]) > 0
    
    print("Test 2, 3, 6, 8 (Timeline Integrity & Schemas) passed.")

def test_preview_cache():
    # Test 9: Preview Cache Retrieval
    import time
    
    start_1 = time.time()
    r1 = client.post("/api/preview/build", json={"text": "Unique cache test", "world_id": "w1", "characters": []}).json()
    dur_1 = time.time() - start_1
    
    start_2 = time.time()
    r2 = client.post("/api/preview/build", json={"text": "Unique cache test", "world_id": "w1", "characters": []}).json()
    dur_2 = time.time() - start_2
    
    assert r1["story_id"] == r2["story_id"]
    
    print("Test 9 (Preview Cache behavior) passed.")

if __name__ == "__main__":
    test_intent_detection()
    test_timeline_integrity()
    test_preview_cache()
    print("All Preview Engine tests passed!")
