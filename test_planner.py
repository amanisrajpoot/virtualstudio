from backend.compiler.schemas import StoryBeatDraft
from backend.director.planner import DirectorPlanner
from backend.director.scene_resolver import SceneResolver
import traceback

def print_beat(beat):
    print(f"Focus Actor: {beat.composition.focus_actor}")
    print(f"Formation: {beat.composition.formation.value}")
    print(f"Weight: {beat.dramatic_weight}")
    for d in beat.resolved_blocking:
        print(f"  Actor: {d.actor_id} -> AnchorIntent: {d.anchor_intent.value} -> Resolved: {d.resolved_anchor}")
    print(f"Reasoning: {beat.planner_reasoning}\n")

def run_tests():
    planner = DirectorPlanner()
    resolver = SceneResolver()
    
    # Base Draft Beats
    sell_beat = StoryBeatDraft(intent="intent_sell_product_v1", intent_confidence=0.9, actor="halku", target="police")
    argue_beat = StoryBeatDraft(intent="intent_argue_v1", intent_confidence=0.9, actor="halku", target="police")
    interrogation_beat = StoryBeatDraft(intent="intent_question_v1", intent_confidence=0.9, actor="police", target="halku")

    print("--- TEST 1: SELLING MAPPING ---")
    staged_sell = planner.plan_beat(sell_beat)
    resolved_sell = resolver.resolve_beat(staged_sell, "scene_village_market_v1")
    print_beat(resolved_sell)

    print("--- TEST 2: MISSING ZONE FALLBACK ---")
    # Using scene_empty_v1 which has no zones, should fallback to "fallback_origin"
    staged_sell_empty = planner.plan_beat(sell_beat)
    resolved_sell_empty = resolver.resolve_beat(staged_sell_empty, "scene_empty_v1")
    print_beat(resolved_sell_empty)

    print("--- TEST 3: ARGUMENT MAPPING ---")
    staged_argue = planner.plan_beat(argue_beat)
    resolved_argue = resolver.resolve_beat(staged_argue, "scene_village_market_v1")
    print_beat(resolved_argue)

    print("--- TEST 4: INTERROGATION MAPPING ---")
    staged_question = planner.plan_beat(interrogation_beat)
    resolved_question = resolver.resolve_beat(staged_question, "scene_village_market_v1")
    print_beat(resolved_question)

    print("--- TEST 5: INVALID SCENE FAILURE ---")
    try:
        resolver.resolve_beat(staged_sell, "scene_invalid_does_not_exist")
    except ValueError as e:
        print(f"Success: Caught expected error: {e}")

if __name__ == "__main__":
    run_tests()
