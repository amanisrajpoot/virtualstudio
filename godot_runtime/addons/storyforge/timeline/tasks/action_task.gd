extends StoryForgeTask
class_name StoryForgeActionTask

var actor_id: String = ""
var action: String = ""
var target: Variant = null
var context: Dictionary = {}

var _actor: Node = null


func _init(p_actor_id: String, p_action: String, p_target: Variant = null, p_context: Dictionary = {}) -> void:
    actor_id = p_actor_id
    action = p_action
    target = p_target
    context = p_context


func _on_execute() -> void:
    # 1. Resolve actor (assuming a global registry or event bus can provide it)
    # For now, we will assume actors register to a central group
    var actors = Engine.get_main_loop().get_nodes_in_group("storyforge_actors")
    for a in actors:
        if a.get("actor_id") == actor_id:
            _actor = a
            break

    if _actor == null:
        push_warning("Timeline ActionTask could not find actor: " + actor_id)
        finish()
        return

    if not _actor.has_method(action):
        push_warning("Actor %s does not have method: %s" % [actor_id, action])
        finish()
        return

    # 2. Call the method
    var args = []
    if target != null:
        args.append(target)
    # Could dynamically append context if needed, but keeping it simple for now.

    var result = _actor.callv(action, args)
    
    # If the action returned a signal or boolean, we could handle it here.
    # For now, we assume actions execute instantly or manage their own state.
    # A true "ActionTask" might connect to the actor's "state_changed" signal to know when done.
    finish()
