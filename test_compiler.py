from backend.compiler.compiler import MockStoryCompiler
from backend.world_state.schemas import StoryWorldState, SnapshotMetadata, EntityState

def run_test():
    compiler = MockStoryCompiler()
    
    # 1. Setup mocked World State
    world_state = StoryWorldState(
        version=1,
        metadata=SnapshotMetadata(
            story_id="s1", episode_id="e1", title="Test", created_at="2024-01-01"
        ),
        entities={
            "char_halku_v1": EntityState(id="char_halku_v1", type="character", properties={"inventory": ["prop_bottle_v1"]})
        }
    )
    
    # 2. Test Success Flow
    print("\n\n--- TEST 1: SUCCESS FLOW ---")
    story_1 = "Halku tries to sell his moonlight bottle. The policeman questions him."
    result_1 = compiler.compile(story_1, world_state)
    print(f"Status: {result_1.status}")
    print(f"Scene: {result_1.scene} (Confidence: {result_1.scene_confidence})")
    print("Beats:")
    for b in result_1.beats:
        print(f"  - {b.actor} -> {b.intent} (Target: {b.target}, Object: {b.object}, Confidence: {b.intent_confidence})")
        
    # 3. Test Clarification Flow
    print("\n\n--- TEST 2: CLARIFICATION FLOW ---")
    story_2 = "Halku opens a quantum portal to escape the market."
    result_2 = compiler.compile(story_2, world_state)
    print(f"Status: {result_2.status}")
    print(f"Unknown Concepts: {result_2.unknown_concepts}")

if __name__ == "__main__":
    run_test()
