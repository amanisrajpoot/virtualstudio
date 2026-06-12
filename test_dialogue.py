from backend.director.staging_schemas import StagedBeat, SceneComposition, FormationCategory
from backend.dialogue.engine import DialogueEngine

def run_tests():
    engine = DialogueEngine()
    
    # 1. Setup Mock Staged Beats
    greet_beat = StagedBeat(
        intent="intent_greet_v1",
        intent_confidence=0.9,
        actor="char_halku_v1",
        target="char_policeman_v1",
        composition=SceneComposition(
            focus_actor="char_halku_v1",
            secondary_actor="char_policeman_v1",
            formation=FormationCategory.DIALOGUE_2P
        )
    )
    
    argue_beat = StagedBeat(
        intent="intent_argue_v1",
        intent_confidence=0.9,
        actor="char_policeman_v1",
        target="char_halku_v1",
        composition=SceneComposition(
            focus_actor="char_policeman_v1",
            secondary_actor="char_halku_v1",
            formation=FormationCategory.ARGUMENT_2P
        )
    )

    print("\n--- TEST 1: LOW IMPORTANCE (TEMPLATE) ---")
    dialogue_greet = engine.process_beat(greet_beat)
    line1 = dialogue_greet.dialogue_line
    print(f"Tags: Importance={line1.tags.importance.value}, Goal={line1.tags.speech_goal}")
    print(f"Speaker: {line1.speaker_id}")
    print(f"Text (Latin Script): {line1.text}")
    print(f"Audio: Path={line1.audio_path}, Exact Duration={line1.duration}s")
    
    print("\n--- TEST 2: HIGH IMPORTANCE (LLM) ---")
    dialogue_argue = engine.process_beat(argue_beat)
    line2 = dialogue_argue.dialogue_line
    print(f"Tags: Importance={line2.tags.importance.value}, Goal={line2.tags.speech_goal}")
    print(f"Speaker: {line2.speaker_id}")
    print(f"Text (Latin Script): {line2.text}")
    print(f"Audio: Path={line2.audio_path}, Exact Duration={line2.duration}s")

if __name__ == "__main__":
    run_tests()
