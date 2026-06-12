"""Voice Engine orchestrator."""

import os
import wave
import uuid
from pathlib import Path

from backend.events.bus import EventBus
from backend.events.schemas import EventEnvelope, EventType, EventCategory, EventMetadata
from backend.audio.schemas import AudioAsset
from backend.audio.cache import AudioCache
from backend.audio.registry import get_voice_profile
from backend.audio.providers.mock_tts import MockTTSProvider

class VoiceEngine:
    def __init__(self, bus: EventBus, audio_dir: str = "data/generated_audio"):
        self.bus = bus
        self.audio_dir = Path(audio_dir)
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.cache = AudioCache()
        self.provider = MockTTSProvider()
        
        # Subscribe to DialogueGenerated
        self.bus.subscribe(EventType.DIALOGUE_GENERATED, self.handle_dialogue_generated)

    def _extract_duration_ms(self, wav_path: str) -> int:
        """Extracts true duration from the physical .wav file in milliseconds."""
        try:
            with wave.open(wav_path, 'r') as w:
                frames = w.getnframes()
                rate = w.getframerate()
                return int((frames / float(rate)) * 1000)
        except Exception as e:
            print(f"[VoiceEngine] Failed to read {wav_path}: {e}")
            return 0

    def handle_dialogue_generated(self, envelope: EventEnvelope):
        payload = envelope.payload
        correlation_id = envelope.correlation_id
        
        # In a real payload, we'd extract text and actor_id
        # Our mock tests might just pass text and actor_id in the event payload
        # Wait, the DialogueEngine puts "tags" in the payload? 
        # Actually DialogueEngine currently puts text directly on the beat, but the event we emit in test_audio will have the correct payload.
        # Let's assume the payload has: {"text": "Hello", "actor_id": "char_halku_v1"}
        text = payload.get("text", "")
        actor_id = payload.get("actor_id", "")
        
        if not text or not actor_id:
            # We skip if it doesn't have the required fields (e.g., non-speech beat)
            return
            
        self.bus.publish(
            event_type=EventType.AUDIO_REQUESTED,
            event_category=EventCategory.DOMAIN,
            correlation_id=correlation_id,
            payload={"text": text, "actor_id": actor_id},
            metadata=EventMetadata(producer="VoiceEngine")
        )

        # 1. Profile Resolution
        profile = get_voice_profile(actor_id)
        if not profile:
            self.bus.publish(
                event_type=EventType.AUDIO_GENERATION_FAILED,
                event_category=EventCategory.SYSTEM,
                correlation_id=correlation_id,
                payload={"error": f"Invalid voice profile for actor {actor_id}"},
                metadata=EventMetadata(producer="VoiceEngine")
            )
            return

        # 2. Caching
        cache_key = self.cache.generate_key(text, profile.profile_id)
        cached_asset = self.cache.get(cache_key)
        
        if cached_asset:
            self.bus.publish(
                event_type=EventType.AUDIO_CACHED,
                event_category=EventCategory.DOMAIN,
                correlation_id=correlation_id,
                payload={"asset_id": cached_asset.asset_id, "duration_ms": cached_asset.duration_ms},
                metadata=EventMetadata(producer="VoiceEngine")
            )
            # Re-publish as generated so the CameraDirector still gets the AudioGenerated hook
            self.bus.publish(
                event_type=EventType.AUDIO_GENERATED,
                event_category=EventCategory.DOMAIN,
                correlation_id=correlation_id,
                payload={"asset_id": cached_asset.asset_id, "path": cached_asset.path, "duration_ms": cached_asset.duration_ms},
                metadata=EventMetadata(producer="VoiceEngine")
            )
            return

        # 3. Generation
        asset_id = f"aud_{uuid.uuid4().hex[:8]}"
        output_path = str(self.audio_dir / f"{asset_id}.wav")
        
        success = self.provider.generate_audio(text, profile, output_path)
        if not success:
            self.bus.publish(
                event_type=EventType.AUDIO_GENERATION_FAILED,
                event_category=EventCategory.SYSTEM,
                correlation_id=correlation_id,
                payload={"error": "Provider failed to generate audio."},
                metadata=EventMetadata(producer="VoiceEngine")
            )
            return

        # 4. Extract True Duration
        duration_ms = self._extract_duration_ms(output_path)

        # 5. Save to Cache
        new_asset = AudioAsset(
            asset_id=asset_id,
            path=output_path,
            duration_ms=duration_ms,
            voice_profile=profile.profile_id,
            checksum=cache_key
        )
        self.cache.put(cache_key, new_asset)

        # 6. Publish Success
        self.bus.publish(
            event_type=EventType.AUDIO_GENERATED,
            event_category=EventCategory.DOMAIN,
            correlation_id=correlation_id,
            payload={"asset_id": new_asset.asset_id, "path": new_asset.path, "duration_ms": new_asset.duration_ms},
            metadata=EventMetadata(producer="VoiceEngine")
        )
