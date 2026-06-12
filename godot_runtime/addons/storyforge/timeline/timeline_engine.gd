extends Node
class_name StoryForgeTimelineEngine

signal sequence_started(sequence_id: String)
signal sequence_finished(sequence_id: String)

var _active_tasks: Array[StoryForgeTask] = []


func _process(delta: float) -> void:
    var i = _active_tasks.size() - 1
    while i >= 0:
        var task = _active_tasks[i]
        if task.is_running:
            task.tick(delta)
        if task.is_finished:
            _active_tasks.remove_at(i)
        i -= 1


func play(task: StoryForgeTask) -> void:
    if task == null:
        return
        
    _active_tasks.append(task)
    task.finished.connect(_on_task_finished)
    task.execute()


func _on_task_finished(task: StoryForgeTask) -> void:
    task.finished.disconnect(_on_task_finished)
