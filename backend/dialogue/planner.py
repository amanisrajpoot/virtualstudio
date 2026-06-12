"""Dialogue Planner assigns speech goals and importance to staged beats."""

from backend.director.staging_schemas import StagedBeat
from .schemas import DialogueTags, DialogueImportance

class DialoguePlanner:
    def plan_dialogue(self, beat: StagedBeat) -> DialogueTags | None:
        """Determines the requirements for dialogue generation. Returns None if no dialogue is needed."""
        
        intent = beat.intent
        
        if "sell_product" in intent:
            return DialogueTags(
                speech_goal="persuade_and_sell",
                emotion="persuasive",
                importance=DialogueImportance.MEDIUM,  # Can use template if available
                response_expected=True
            )
        elif "argue" in intent:
            return DialogueTags(
                speech_goal="confront_and_accuse",
                emotion="hostile",
                importance=DialogueImportance.HIGH,   # Needs LLM
                response_expected=True
            )
        elif "question" in intent:
            return DialogueTags(
                speech_goal="investigate",
                emotion="suspicious",
                importance=DialogueImportance.HIGH,   # Needs LLM
                response_expected=True
            )
        elif "greet" in intent:
            return DialogueTags(
                speech_goal="acknowledge",
                emotion="neutral",
                importance=DialogueImportance.LOW,    # Always use template
                response_expected=True
            )
        
        # E.g., for walk, run, or idle, no dialogue needed
        return None
