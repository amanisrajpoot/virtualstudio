extends RefCounted
class_name StoryForgeTask

signal finished(task: StoryForgeTask)

var is_running: bool = false
var is_finished: bool = false


func execute() -> void:
    if is_running or is_finished:
        return
    is_running = true
    _on_execute()


func tick(delta: float) -> void:
    if not is_running:
        return
    _on_tick(delta)


func finish() -> void:
    if not is_running:
        return
    is_running = false
    is_finished = true
    _on_finish()
    finished.emit(self)


func cancel() -> void:
    if not is_running:
        return
    is_running = false
    is_finished = true
    _on_cancel()


# Virtual methods to be overridden by subclasses
func _on_execute() -> void:
    finish() # Default behavior is to finish immediately


func _on_tick(_delta: float) -> void:
    pass


func _on_finish() -> void:
    pass


func _on_cancel() -> void:
    pass
