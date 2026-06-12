import os
import shutil
from backend.world_state.manager import WorldStateManager
from backend.world_state.schemas import StoryWorldState, SnapshotMetadata, EntityState, WorldConditions, StoryEvent

def run_test():
    test_dir = "data/test_world_state"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
        
    manager = WorldStateManager(storage_dir=test_dir)
    
    # 1. Create Initial State
    initial_state = StoryWorldState(
        version=0,
        metadata=SnapshotMetadata(
            story_id="story_001",
            episode_id="ep_001",
            title="A Quiet Morning",
            created_at="2024-01-01T08:00:00Z"
        ),
        entities={
            "halku": EntityState(id="halku", type="character", properties={"inventory": []}),
            "moonlight_bottle_001": EntityState(id="moonlight_bottle_001", type="prop", properties={"owner": None})
        },
        conditions=WorldConditions(weather="clear", time_of_day="morning"),
        events=[]
    )
    
    v1 = manager.save_snapshot(initial_state)
    print(f"Saved initial snapshot: v{v1}")
    
    # 2. Episode happens (Halku picks up bottle)
    updates = {
        "entities": {
            "halku": {"id": "halku", "type": "character", "properties": {"inventory": ["moonlight_bottle_001"]}},
            "moonlight_bottle_001": {"id": "moonlight_bottle_001", "type": "prop", "properties": {"owner": "halku"}}
        },
        "conditions": {
            "time_of_day": "afternoon"
        }
    }
    events = [
        StoryEvent(event_id="evt_001", actor="halku", action="pickup", target="moonlight_bottle_001")
    ]
    
    current_state = manager.load_latest()
    new_state = manager.update_state(current_state, updates, events)
    new_state.metadata.episode_id = "ep_002"
    new_state.metadata.title = "The Transaction"
    
    # Check diff before saving
    diff = manager.diff_state(current_state, new_state)
    print("\nDiff before saving v2:")
    print(diff)
    
    v2 = manager.save_snapshot(new_state)
    print(f"\nSaved new snapshot: v{v2}")
    
    # 3. Verify Rollback (Append-Only)
    print(f"\nRolling back to v{v1}...")
    rolled_back = manager.rollback(v1)
    print(f"Rolled back state is now version: v{rolled_back.version}")
    print(f"Halku's inventory in newest version: {rolled_back.entities['halku'].properties['inventory']}")
    
if __name__ == "__main__":
    run_test()
