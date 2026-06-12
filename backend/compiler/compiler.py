"""Mock Story Compiler for testing the pipeline without an LLM API key."""

from .schemas import StoryDSLDraft, StoryBeatDraft
from .prompts import SYSTEM_PROMPT_TEMPLATE
from backend.world_state.schemas import StoryWorldState

class MockStoryCompiler:
    def _assemble_context(self, world_state: StoryWorldState | None) -> dict:
        # In a real app, query the Asset Registry database.
        # For the mock, we'll return hardcoded lists.
        scenes = "- scene_village_market_v1 (Village Market)"
        characters = "- char_halku_v1 (Halku, Seller)\n- char_policeman_v1 (Policeman, Authority)"
        props = "- prop_bottle_v1 (Bottle)"
        intents = (
            "- intent_sell_product_v1: Actor presents or offers a product to nearby characters.\n"
            "- intent_argue_v1: Actor argues with a target character.\n"
            "- intent_question_v1: Actor questions a target character."
        )
        
        world_summary = "No world state provided."
        if world_state:
            # Generate a summary string
            lines = []
            for e_id, ent in world_state.entities.items():
                if ent.type == "character":
                    inv = ent.properties.get("inventory", [])
                    if inv:
                        lines.append(f"{e_id} owns: {', '.join(inv)}")
                    else:
                        lines.append(f"{e_id} owns: nothing")
            world_summary = "\n".join(lines) if lines else "World is empty."

        return {
            "scenes": scenes,
            "characters": characters,
            "props": props,
            "intents": intents,
            "world_summary": world_summary
        }

    def compile(self, user_story: str, world_state: StoryWorldState | None = None) -> StoryDSLDraft:
        context = self._assemble_context(world_state)
        
        prompt = SYSTEM_PROMPT_TEMPLATE.format(
            scenes=context["scenes"],
            characters=context["characters"],
            props=context["props"],
            intents=context["intents"],
            world_summary=context["world_summary"]
        )
        prompt += f"\n\nUSER STORY:\n{user_story}"
        
        # Print prompt to simulate sending it to the LLM
        print("====== GENERATED LLM PROMPT ======")
        print(prompt)
        print("==================================\n")
        
        # Mock LLM Response Generation based on input keywords
        if "quantum portal" in user_story.lower():
            return StoryDSLDraft(
                status="needs_clarification",
                unknown_concepts=["quantum portal"]
            )
            
        # Simulate a successful semantic mapping
        return StoryDSLDraft(
            status="success",
            scene="scene_village_market_v1",
            scene_confidence=0.95,
            characters=["char_halku_v1", "char_policeman_v1"],
            beats=[
                StoryBeatDraft(
                    intent="intent_sell_product_v1",
                    intent_confidence=0.92,
                    actor="char_halku_v1",
                    target="char_policeman_v1",
                    object="prop_bottle_v1"
                ),
                StoryBeatDraft(
                    intent="intent_question_v1",
                    intent_confidence=0.88,
                    actor="char_policeman_v1",
                    target="char_halku_v1"
                )
            ]
        )
