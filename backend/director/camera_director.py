"""Resolves high-level camera goals into deterministic cuts based on the actor track."""

from __future__ import annotations

from .schemas import ActorEvent, CameraEvent

def resolve_camera_track(
    camera_goal: str | None,
    actor_track: list[ActorEvent],
    primary_actor: str,
    target_actor: str | None,
    start_time: float = 0.0
) -> list[CameraEvent]:
    """
    Analyzes the actor track and generates a camera track using the specified goal.
    """
    camera_track: list[CameraEvent] = []
    
    if not camera_goal:
        # Fallback to a wide shot
        camera_track.append(CameraEvent(time=start_time, preset="cam_wide_v1"))
        return camera_track

    # Extract speech events to know exactly when people talk
    speech_events = [e for e in actor_track if e.action == "speak"]

    if camera_goal == "show_dialogue":
        # 1. Establish with a medium shot
        camera_track.append(CameraEvent(time=start_time, preset="cam_medium_v1"))
        
        # 2. Cut to closeup when someone speaks
        for event in speech_events:
            camera_track.append(CameraEvent(
                time=event.time,
                preset="cam_closeup_v1",
                target=event.actor_id
            ))
            
    elif camera_goal == "show_argument":
        # 1. Start with shot reverse shot preset
        camera_track.append(CameraEvent(time=start_time, preset="cam_shot_reverse_shot_v1"))
        
        # 2. Cut to closeup on speaker, then immediately to a reaction shot of the listener
        for event in speech_events:
            camera_track.append(CameraEvent(
                time=event.time,
                preset="cam_closeup_v1",
                target=event.actor_id
            ))
            
            # Find the listener (the other person)
            listener = target_actor if event.actor_id == primary_actor else primary_actor
            if listener:
                # Add a reaction shot 1 second into the speech
                camera_track.append(CameraEvent(
                    time=event.time + 1.0,
                    preset="cam_reaction_v1",
                    target=listener
                ))
                
    elif camera_goal == "show_chase":
        # 1. Wide shot to see the chase start
        camera_track.append(CameraEvent(time=start_time, preset="cam_wide_v1"))
        # 2. Cut to tracking shot on the primary actor (the chaser or runner)
        camera_track.append(CameraEvent(
            time=start_time + 1.5,
            preset="cam_tracking_v1",
            target=primary_actor
        ))
        
    elif camera_goal == "show_reaction":
        # 1. Immediately drop into a reaction shot
        camera_track.append(CameraEvent(
            time=start_time,
            preset="cam_reaction_v1",
            target=primary_actor
        ))
    else:
        # Fallback
        camera_track.append(CameraEvent(time=start_time, preset="cam_wide_v1"))

    # Sort to ensure monotonic time
    camera_track.sort(key=lambda e: e.time)
    
    return camera_track
