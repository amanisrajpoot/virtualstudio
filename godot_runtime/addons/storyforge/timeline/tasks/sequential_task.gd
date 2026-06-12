extends StoryForgeTask
class_name StoryForgeSequentialTask

var _tasks: Array[StoryForgeTask] = []
var _current_index: int = 0


func add_task(task: StoryForgeTask) -> void:
    if task != null:
        _tasks.append(task)


func _on_execute() -> void:
    _current_index = 0
    _start_next_task()


func _on_tick(delta: float) -> void:
    if _current_index < _tasks.size():
        _tasks[_current_index].tick(delta)


func _start_next_task() -> void:
    if _current_index >= _tasks.size():
        finish()
        return

    var next_task = _tasks[_current_index]
    next_task.finished.connect(_on_child_task_finished)
    next_task.execute()


func _on_child_task_finished(_task: StoryForgeTask) -> void:
    _current_index += 1
    _start_next_task()


func _on_cancel() -> void:
    if _current_index < _tasks.size():
        _tasks[_current_index].cancel()
