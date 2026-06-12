extends StoryForgeTask
class_name StoryForgeDelayTask

var duration: float = 0.0
var _elapsed: float = 0.0


func _init(p_duration: float = 0.0) -> void:
    duration = p_duration


func _on_execute() -> void:
    _elapsed = 0.0
    if duration <= 0.0:
        finish()


func _on_tick(delta: float) -> void:
    _elapsed += delta
    if _elapsed >= duration:
        finish()
