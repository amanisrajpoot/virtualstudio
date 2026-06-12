import hashlib
import json
import time
from typing import List, Optional
from backend.models.preview import PreviewPackage, PreviewBeat, PreviewState
from backend.observability.tracker import telemetry

class PreviewCache:
    def __init__(self):
        self._cache = {}

    def _generate_key(self, text: str, world_id: str, characters: List[str]) -> str:
        data = f"{text}|{world_id}|{','.join(sorted(characters))}"
        return hashlib.sha256(data.encode()).hexdigest()

    def get(self, text: str, world_id: str, characters: List[str]) -> Optional[PreviewPackage]:
        key = self._generate_key(text, world_id, characters)
        return self._cache.get(key)

    def set(self, text: str, world_id: str, characters: List[str], package: PreviewPackage) -> None:
        key = self._generate_key(text, world_id, characters)
        self._cache[key] = package

class PreviewBuilder:
    def __init__(self, cache: PreviewCache):
        self.cache = cache

    def build(self, story_id: str, text: str, world_id: str, characters: List[str]) -> PreviewPackage:
        start_t = time.time()
        
        cached = self.cache.get(text, world_id, characters)
        if cached:
            telemetry.record_cache("preview", True)
            telemetry.record_latency("preview_ms", (time.time() - start_t) * 1000)
            return cached
            
        telemetry.record_cache("preview", False)

        beats = self._simulate_story(text, characters)
        
        package = PreviewPackage(
            story_id=story_id,
            world_id=world_id,
            characters=characters,
            beats=beats
        )
        
        self.cache.set(text, world_id, characters, package)
        
        telemetry.record_latency("preview_ms", (time.time() - start_t) * 1000)
        return package

    def _simulate_story(self, text: str, characters: List[str]) -> List[PreviewBeat]:
        text_lower = text.lower()
        beats = []
        
        if "sell" in text_lower:
            # Generate SELL_PRODUCT sequence
            beats = [
                self._create_beat("b1", 0.0, "approach", "side_by_side", "MOVE", "Moving to stall", ["Actor navigating to selling zone"]),
                self._create_beat("b2", 2.0, "selling", "face_to_face", "SELL_PRODUCT", None, ["Actor owns product", "Customer nearby"]),
                self._create_beat("b3", 4.0, "selling", "face_to_face", "INTERACT", "Bhaiya, kitne ka hai?", ["Customer responding to offer"]),
                self._create_beat("b4", 6.0, "selling", "face_to_face", "DIALOGUE", "Asli moonlight hai sir!", ["Actor pushing sale"])
            ]
        elif "argue" in text_lower:
            # Generate ARGUMENT sequence
            beats = [
                self._create_beat("b1", 0.0, "approach", "side_by_side", "APPROACH", None, ["Actor approaching target"]),
                self._create_beat("b2", 2.0, "argument_2p", "face_to_face", "CONFRONT", "Yeh kya badtameezi hai?", ["Argument intent detected", "Distance rule selected"]),
                self._create_beat("b3", 4.0, "argument_2p", "face_to_face", "DIALOGUE", "Mera koi kasoor nahi hai!", ["Target defending position"])
            ]
        elif "run" in text_lower or "chase" in text_lower:
            # Generate CHASE sequence
            beats = [
                self._create_beat("b1", 0.0, "alert", "far_apart", "ALERT", "Ruko!", ["Threat detected"]),
                self._create_beat("b2", 2.0, "chase", "pursuit", "CHASE", None, ["Target fleeing", "Actor in pursuit"])
            ]
        else:
            # Generic beat
            beats = [
                self._create_beat("b1", 0.0, "idle", "side_by_side", "IDLE", "...", ["No specific intent matched"])
            ]
            
        return beats

    def _create_beat(self, b_id: str, time: float, form_id: str, form_vis: str, intent: str, diag: Optional[str], expl: List[str]) -> PreviewBeat:
        state = PreviewState(
            current_beat_id=b_id,
            active_zone="market_stall", # Mock logic
            active_path=["market_stall", "road"],
            visible_characters=[],
            active_dialogue=diag
        )
        return PreviewBeat(
            id=b_id,
            time=time,
            formation_id=form_id,
            formation_visual=form_vis,
            intent=intent,
            dialogue=diag,
            explanation=expl,
            state_snapshot=state
        )
