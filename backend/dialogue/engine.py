"""Orchestrator for the Dialogue Subsystem."""

import json
from backend.director.staging_schemas import StagedBeat
from .schemas import DialogueBeat, DialogueLine
from .planner import DialoguePlanner
from .generator import DialogueGenerator
from .audio import AudioEngine

class DialogueEngine:
    def __init__(self):
        self.planner = DialoguePlanner()
        self.generator = DialogueGenerator()
        self.audio = AudioEngine()
        
        # Mock Asset Registry Cache for Character Profiles
        self.registry_cache = {
            "char_halku_v1": {
                "voice": "voice_cheerful_male_v1",
                "dialogue_profile": {
                    "speech_style": "hustler",
                    "sentence_length": "short",
                    "humor_level": 0.8
                }
            },
            "char_policeman_v1": {
                "voice": "voice_stern_male_v1",
                "dialogue_profile": {
                    "speech_style": "authoritative",
                    "sentence_length": "short",
                    "aggression": 0.8
                }
            }
        }
        
    def process_beat(self, beat: StagedBeat) -> DialogueBeat:
        """Takes a StagedBeat, generates dialogue (if needed), and returns a DialogueBeat."""
        
        dialogue_beat = DialogueBeat(**beat.model_dump(), dialogue_line=None)
        
        # 1. Plan Dialogue
        tags = self.planner.plan_dialogue(beat)
        
        if not tags:
            return dialogue_beat # No dialogue needed
            
        # 2. Fetch Profile
        actor_id = beat.composition.focus_actor
        actor_data = self.registry_cache.get(actor_id, {})
        profile = actor_data.get("dialogue_profile", {})
        voice_id = actor_data.get("voice", "default_voice")
        
        # 3. Generate Text
        text = self.generator.generate(
            actor_id=actor_id,
            tags=tags,
            profile=profile,
            intent=beat.intent
        )
        
        # 4. Generate TTS and Measure Duration
        audio_path, duration = self.audio.generate_tts_and_measure(text, voice_id)
        
        # 5. Attach Line
        dialogue_beat.dialogue_line = DialogueLine(
            speaker_id=actor_id,
            text=text,
            language="hinglish",
            tags=tags,
            audio_path=audio_path,
            duration=duration
        )
        
        return dialogue_beat
