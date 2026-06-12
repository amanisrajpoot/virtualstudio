"""Maps high-level Story DSL intents into Runtime DSL tracks."""

from __future__ import annotations

from backend.asset_registry.schemas import AssetRead
from .schemas import StoryBeat, ActorEvent, CameraEvent, DirectedSequence, TrackSet
from .timing_utils import estimate_speech_duration
from .camera_director import resolve_camera_track

# A temporary mock to resolve animation durations until we inject a registry client
MOCK_ANIMATION_DURATIONS = {
    "anim_idle_v1": 2.0, "anim_walk_v1": 1.5, "anim_talk_v1": 2.5,
    "anim_run_v1": 1.2, "anim_point_v1": 1.0, "anim_pickup_v1": 1.8,
    "anim_celebrate_v1": 2.0, "anim_laugh_v1": 1.5, "anim_inspect_v1": 2.0,
    "anim_argue_v1": 2.5
}

def map_intent_to_sequence(
    beat: StoryBeat, 
    intent_asset: AssetRead, 
    start_time: float = 0.0
) -> DirectedSequence:
    """
    Converts a single Story DSL beat into a track-based Godot runtime sequence.
    """
    actor_track: list[ActorEvent] = []
    current_time = start_time
    
    metadata = intent_asset.metadata
        
    # 1. Staging / Movement
    if beat.target:
        distance = metadata.get("distance", "near")
        # Direct the actor to move relative to the target
        actor_track.append(ActorEvent(
            time=current_time,
            actor_id=beat.actor,
            action="move_to",
            target={
                "anchor": beat.target, 
                "relation": "near", 
                "relative_to": beat.target, 
                "distance": distance
            }
        ))
        current_time += 2.0 # Mock movement time
        
        # Face the target
        actor_track.append(ActorEvent(
            time=current_time,
            actor_id=beat.actor,
            action="look_at_target",
            target=beat.target
        ))
        current_time += 0.5
        
    # 2. Emotion
    emotion = metadata.get("default_emotion")
    if emotion:
        actor_track.append(ActorEvent(
            time=current_time,
            actor_id=beat.actor,
            action="set_emotion",
            target=emotion
        ))

    # 3. Animations & Speech
    animations = metadata.get("animations", [])
    
    dialogue_time = current_time
    for i, anim in enumerate(animations):
        actor_track.append(ActorEvent(
            time=current_time,
            actor_id=beat.actor,
            action="play_animation",
            target=anim
        ))
        
        if "talk" in anim or "argue" in anim:
            dialogue_time = current_time
            
        anim_duration = MOCK_ANIMATION_DURATIONS.get(anim, 1.0)
        current_time += anim_duration
        
    if beat.dialogue:
        speech_duration = estimate_speech_duration(beat.dialogue)
        actor_track.append(ActorEvent(
            time=dialogue_time,
            actor_id=beat.actor,
            action="speak",
            target=beat.dialogue
        ))
        
        # Ensure the sequence is long enough to let the speech finish
        end_of_speech = dialogue_time + speech_duration
        if current_time < end_of_speech:
            current_time = end_of_speech
            
    # 4. Camera Resolution (Delegated to Camera Director)
    camera_goal = metadata.get("camera_goal")
    camera_track = resolve_camera_track(
        camera_goal=camera_goal,
        actor_track=actor_track,
        primary_actor=beat.actor,
        target_actor=beat.target,
        start_time=start_time
    )
            
    tracks = TrackSet(
        actor=actor_track,
        camera=camera_track
    )
    
    return DirectedSequence(
        schema_version="1.0",
        scene="", 
        tracks=tracks,
        duration=current_time - start_time
    )
