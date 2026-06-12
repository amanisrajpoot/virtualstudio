extends RefCounted
class_name StoryForgeRuntimeDSLParser

## Parses a Runtime DSL JSON Dictionary into a StoryForgeParallelTask
static func parse(dsl_data: Dictionary) -> StoryForgeParallelTask:
    var root_task = StoryForgeParallelTask.new()
    
    if not dsl_data.has("tracks"):
        push_error("Invalid Runtime DSL: missing 'tracks' object.")
        return root_task
        
    var tracks = dsl_data["tracks"]
    
    if tracks.has("actor"):
        _parse_actor_track(tracks["actor"], root_task)
        
    if tracks.has("camera"):
        _parse_camera_track(tracks["camera"], root_task)
        
    if tracks.has("audio"):
        _parse_audio_track(tracks["audio"], root_task)
        
    if tracks.has("effects"):
        _parse_effects_track(tracks["effects"], root_task)
        
    return root_task


static func _parse_actor_track(events: Array, root_task: StoryForgeParallelTask) -> void:
    for event in events:
        if typeof(event) != TYPE_DICTIONARY:
            continue
            
        var time: float = event.get("time", 0.0)
        var actor_id: String = event.get("actor_id", "")
        var action: String = event.get("action", "")
        var target: Variant = event.get("target", null)
        var context: Dictionary = event.get("context", {})
        
        var seq = StoryForgeSequentialTask.new()
        if time > 0.0:
            seq.add_task(StoryForgeDelayTask.new(time))
            
        seq.add_task(StoryForgeActionTask.new(actor_id, action, target, context))
        root_task.add_task(seq)


static func _parse_camera_track(events: Array, root_task: StoryForgeParallelTask) -> void:
    for event in events:
        if typeof(event) != TYPE_DICTIONARY:
            continue
            
        var time: float = event.get("time", 0.0)
        var preset: String = event.get("preset", "")
        var target: Variant = event.get("target", null)
        
        # We will use an ActionTask directed at the generic "director" actor or event bus
        # For now, assume a global 'camera_manager' handles these cuts.
        var seq = StoryForgeSequentialTask.new()
        if time > 0.0:
            seq.add_task(StoryForgeDelayTask.new(time))
            
        var context = {"target": target}
        seq.add_task(StoryForgeActionTask.new("camera_manager", "cut_to_preset", preset, context))
        root_task.add_task(seq)


static func _parse_audio_track(events: Array, root_task: StoryForgeParallelTask) -> void:
    for event in events:
        if typeof(event) != TYPE_DICTIONARY:
            continue
            
        var time: float = event.get("time", 0.0)
        var asset_id: String = event.get("asset_id", "")
        var type: String = event.get("type", "sfx")
        var volume_db: float = event.get("volume_db", 0.0)
        
        var seq = StoryForgeSequentialTask.new()
        if time > 0.0:
            seq.add_task(StoryForgeDelayTask.new(time))
            
        var context = {"type": type, "volume_db": volume_db}
        seq.add_task(StoryForgeActionTask.new("audio_manager", "play_audio", asset_id, context))
        root_task.add_task(seq)


static func _parse_effects_track(events: Array, root_task: StoryForgeParallelTask) -> void:
    for event in events:
        if typeof(event) != TYPE_DICTIONARY:
            continue
            
        var time: float = event.get("time", 0.0)
        var asset_id: String = event.get("asset_id", "")
        var anchor: Variant = event.get("anchor", null)
        var duration: float = event.get("duration", 0.0)
        
        var seq = StoryForgeSequentialTask.new()
        if time > 0.0:
            seq.add_task(StoryForgeDelayTask.new(time))
            
        var context = {"anchor": anchor, "duration": duration}
        seq.add_task(StoryForgeActionTask.new("effects_manager", "spawn_effect", asset_id, context))
        root_task.add_task(seq)
