"""Verification Tests for Subsystem 21 (World Studio)."""

import os
from backend.models.world import WorldProfile, ZoneProfile, AmbienceProfile, FormationRef, PropRef, WorldConnection
from backend.repositories.worlds import WorldRepository
from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)

def test_world_persistence_and_graph():
    repo = WorldRepository(data_dir="data/test_worlds")
    
    world = WorldProfile(
        id="test_village_market",
        name="Test Village Market",
        archetype="commercial",
        description="A bustling rural market.",
        zones=[
            ZoneProfile(id="market_stall", name="Market Stall", zone_type="selling_zone", capacity=2, adjacent=["road"]),
            ZoneProfile(id="road", name="Main Road", zone_type="transit", capacity=5, adjacent=["tea_stall"]),
            ZoneProfile(id="tea_stall", name="Tea Stall", zone_type="gathering", capacity=5, adjacent=[])
        ],
        formations=[FormationRef(formation_id="SELLING", supported_zone_types=["selling_zone"])],
        props=[PropRef(prop_id="vegetable_cart", required=True)],
        ambience=AmbienceProfile(),
        connected_worlds=[WorldConnection(target_world="test_village_street", connection_type="road_connected")]
    )
    
    repo.save(world)
    assert os.path.exists("data/test_worlds/test_village_market.json")
    
    loaded = repo.get("test_village_market")
    assert loaded is not None
    assert loaded.name == "Test Village Market"
    
    # Test 2: Zone Graph traversal
    stall = next(z for z in loaded.zones if z.id == "market_stall")
    assert "road" in stall.adjacent
    road = next(z for z in loaded.zones if z.id == "road")
    assert "tea_stall" in road.adjacent
    
    # Test 3: Connected worlds persistence
    assert len(loaded.connected_worlds) == 1
    assert loaded.connected_worlds[0].target_world == "test_village_street"
    
    # Test 4: Formation compatibility checks
    assert len(loaded.formations) == 1
    assert "selling_zone" in loaded.formations[0].supported_zone_types
    
    print("Tests 1, 2, 3, 4 (Persistence, Zone Graph, Connected Worlds, Formation Compatibility) passed.")

def test_world_generation_contract():
    response = client.post("/api/worlds/generate", json={"description": "A dark spooky forest"})
    assert response.status_code == 200
    data = response.json()
    
    assert "job_id" in data
    assert data["status"] == "completed"
    assert len(data["zones"]) > 0
    assert "capacity" in data["zones"][0]
    assert "adjacent" in data["zones"][0]
    
    print("Test 5 (World Generation Contract) passed.")

def test_seed_validation():
    # Verify the 15 India-first worlds were successfully seeded into the active repository
    repo = WorldRepository(data_dir="data/worlds")
    worlds = repo.list()
    assert len(worlds) >= 15
    
    names = [w.name for w in worlds]
    assert "Village Market" in names
    assert "Election Rally Ground" in names
    assert "Police Chowki" in names
    
    print("Test 7 (Seed Pack Validation) passed.")

def test_required_prop_validation():
    repo = WorldRepository(data_dir="data/test_worlds")
    world = repo.get("test_village_market")
    
    has_required_prop = any(p.required for p in world.props)
    assert has_required_prop
    
    print("Test 9 (Required Prop Validation logic) passed.")

if __name__ == "__main__":
    test_world_persistence_and_graph()
    test_world_generation_contract()
    test_seed_validation()
    test_required_prop_validation()
    print("All World Studio tests passed!")
