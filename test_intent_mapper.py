import json
from backend.director.schemas import StoryBeat
from backend.director.intent_mapper import map_intent_to_sequence
from backend.asset_registry.schemas import AssetRead

def run_test():
    beat = StoryBeat(
        intent="intent_argue_v1",
        actor="char_policeman_v1",
        target="char_halku_v1",
        dialogue="You call this moonlight? It's just tap water in a jar! I'm taking you in."
    )
    
    mock_intent_asset = AssetRead(
        id="intent_argue_v1",
        type="intent",
        name="Argue",
        version="1.0.0",
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
        metadata={
            "description": "Actor argues with a target character.",
            "camera_goal": "show_argument",
            "default_emotion": "angry",
            "distance": "confrontation",
            "animations": ["anim_argue_v1"]
        }
    )
    
    sequence = map_intent_to_sequence(beat, mock_intent_asset)
    
    print("--- ACTOR TRACK ---")
    for event in sequence.tracks.actor:
        print(f"[{event.time:.1f}s] {event.actor_id} -> {event.action}({event.target})")
        
    print("\n--- CAMERA TRACK ---")
    for event in sequence.tracks.camera:
        print(f"[{event.time:.1f}s] {event.preset} (target: {event.target})")
        
    print(f"\nTotal Duration: {sequence.duration:.1f}s")

if __name__ == "__main__":
    run_test()
