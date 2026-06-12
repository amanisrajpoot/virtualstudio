extends StoryForgeTask
class_name StoryForgeParallelTask

var _tasks: Array[StoryForgeTask] = []
var _finished_count: int = 0


func add_task(task: StoryForgeTask) -> void:
    if task != null:
        _tasks.append(task)


func _on_execute() -> void:
    _finished_count = 0
    if _tasks.is_empty():
        finish()
        return

    for task in _tasks:
        task.finished.connect(_on_child_task_finished)
        task.execute()


func _on_tick(delta: float) -> void:
    for task in _tasks:
        if task.is_running:
            task.tick(delta)


func _on_child_task_finished(_task: StoryForgeTask) -> void:
    _finished_count += 1
    if _finished_count >= _tasks.size():
        finish()


func _on_cancel() -> void:
    for task in _tasks:
        if task.is_running:
            task.cancel()
