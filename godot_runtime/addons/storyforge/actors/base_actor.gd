extends CharacterBody3D
class_name StoryForgeBaseActor

signal state_changed(actor_id: String, state: Dictionary)
signal move_requested(actor_id: String, anchor_reference: Dictionary)
signal move_completed(actor_id: String, anchor_reference: Dictionary)
signal spoke(actor_id: String, text: String, metadata: Dictionary)
signal looked_at(actor_id: String, target: Variant)
signal inventory_changed(actor_id: String, inventory: Array)
signal intent_requested(actor_id: String, intent_id: String, context: Dictionary)
signal intent_completed(actor_id: String, intent_id: String, result: Dictionary)
signal actor_error(actor_id: String, message: String)

enum ActorMachineState {
    IDLE,
    WALK,
    TALK,
    RUN,
    INTERACT
}

const STATE_NAMES := {
    ActorMachineState.IDLE: "idle",
    ActorMachineState.WALK: "walk",
    ActorMachineState.TALK: "talk",
    ActorMachineState.RUN: "run",
    ActorMachineState.INTERACT: "interact"
}

@export var actor_id: String = ""
@export var emotion: String = "neutral"
@export_range(0.0, 100.0, 1.0) var energy: float = 100.0
@export var attention: String = ""
@export var inventory: Array[String] = []
@export var current_anchor: String = ""
@export var walk_speed: float = 2.4
@export var run_speed: float = 5.0
@export var arrival_distance: float = 0.25
@export var semantic_world_resolver_path: NodePath
@export var event_bus_path: NodePath
@export var navigation_agent_path: NodePath
@export var animation_player_path: NodePath

var actor_state: StoryForgeActorState

var _machine_state: int = ActorMachineState.IDLE
var _navigation_agent: NavigationAgent3D
var _animation_player: AnimationPlayer
var _target_anchor_reference: Dictionary = {}
var _target_anchor: String = ""


func _ready() -> void:
    if actor_id == "":
        actor_id = name.to_snake_case()

    actor_state = StoryForgeActorState.new()
    actor_state.id = actor_id
    actor_state.emotion = emotion
    actor_state.energy = energy
    actor_state.attention = attention
    actor_state.inventory = inventory.duplicate()
    actor_state.current_anchor = current_anchor
    actor_state.machine_state = STATE_NAMES[_machine_state]

    _ensure_navigation_agent()
    _ensure_animation_player()
    _publish_registered()
    _emit_state_changed()


func _physics_process(_delta: float) -> void:
    if _machine_state != ActorMachineState.WALK and _machine_state != ActorMachineState.RUN:
        return

    if _navigation_agent == null:
        _fail("NavigationAgent3D is required for movement.")
        _set_machine_state(ActorMachineState.IDLE)
        return

    if _navigation_agent.is_navigation_finished():
        _finish_movement()
        return

    var next_position := _navigation_agent.get_next_path_position()
    var direction := global_position.direction_to(next_position)
    var speed := run_speed if _machine_state == ActorMachineState.RUN else walk_speed

    velocity = direction * speed
    move_and_slide()

    if direction.length_squared() > 0.001:
        _face_position(global_position + direction)

    if global_position.distance_to(_navigation_agent.target_position) <= arrival_distance:
        _finish_movement()


func move_to(anchor_reference: Variant, run: bool = false) -> bool:
    var reference := _normalize_anchor_reference(anchor_reference)
    var resolver := _semantic_resolver()
    if resolver == null:
        _fail("Semantic world resolver is required for anchor movement.")
        return false

    var target_position: Vector3 = resolver.resolve_position(reference)
    if target_position == Vector3.ZERO and not resolver.has_anchor(str(reference.get("anchor", ""))):
        _fail("Cannot resolve anchor: %s" % str(reference.get("anchor", "")))
        return false

    _ensure_navigation_agent()
    if _navigation_agent == null:
        _fail("NavigationAgent3D is required for movement.")
        return false

    _target_anchor_reference = reference
    _target_anchor = str(reference.get("anchor", ""))
    _navigation_agent.target_position = target_position

    _set_machine_state(ActorMachineState.RUN if run else ActorMachineState.WALK)
    move_requested.emit(actor_id, reference)
    _publish_move_requested(reference)
    return true


func speak(text: String, metadata: Dictionary = {}, duration_seconds: float = 0.0) -> void:
    _set_machine_state(ActorMachineState.TALK)
    spoke.emit(actor_id, text, metadata)
    _publish_spoke(text, metadata)

    if duration_seconds > 0.0:
        var expected_state := _machine_state
        await get_tree().create_timer(duration_seconds).timeout
        if _machine_state == expected_state:
            _set_machine_state(ActorMachineState.IDLE)


func look_at(target: Vector3, up: Vector3 = Vector3.UP, use_model_front: bool = false) -> void:
    _face_position(target, up, use_model_front)
    attention = "position"
    actor_state.attention = attention

    looked_at.emit(actor_id, target)
    _publish_looked_at(target)
    _emit_state_changed()


func look_at_target(target: Variant) -> bool:
    var target_position := _target_to_position(target)
    if target_position == null:
        _fail("Cannot resolve look target.")
        return false

    _face_position(target_position)
    attention = _target_to_attention(target)
    actor_state.attention = attention

    looked_at.emit(actor_id, target)
    _publish_looked_at(target)
    _emit_state_changed()
    return true


func look_at_anchor(anchor_reference: Variant) -> bool:
    return look_at_target(anchor_reference)


func perform_intent(intent_id: String, context: Dictionary = {}) -> Dictionary:
    _set_machine_state(ActorMachineState.INTERACT)
    var event_context := context.duplicate(true)
    event_context["actor_id"] = actor_id
    intent_requested.emit(actor_id, intent_id, event_context)
    _publish_intent_requested(intent_id, event_context)
    return event_context


func complete_intent(intent_id: String, result: Dictionary = {}) -> void:
    intent_completed.emit(actor_id, intent_id, result)
    _publish_intent_completed(intent_id, result)
    _set_machine_state(ActorMachineState.IDLE)


func pickup(item_id: String, item_metadata: Dictionary = {}) -> bool:
    if item_id == "":
        _fail("Cannot pickup an empty item id.")
        return false

    if not actor_state.inventory.has(item_id):
        actor_state.inventory.append(item_id)

    inventory = actor_state.inventory.duplicate()
    inventory_changed.emit(actor_id, inventory)
    _publish_inventory_changed(inventory)

    if not item_metadata.is_empty():
        var context := {"item_id": item_id, "item_metadata": item_metadata}
        perform_intent("pickup", context)

    _emit_state_changed()
    return true


func drop(item_id: String) -> bool:
    if not actor_state.inventory.has(item_id):
        _fail("Actor does not have item: %s" % item_id)
        return false

    actor_state.inventory.erase(item_id)
    inventory = actor_state.inventory.duplicate()
    inventory_changed.emit(actor_id, inventory)
    _publish_inventory_changed(inventory)
    _emit_state_changed()
    return true


func play_animation(anim_id: String) -> bool:
    if _animation_player == null:
        _fail("AnimationPlayer is not available to play: %s" % anim_id)
        return false
        
    if not _animation_player.has_animation(anim_id):
        _fail("Animation %s not found on actor %s" % [anim_id, actor_id])
        return false
        
    _animation_player.play(anim_id)
    return true


func set_emotion(next_emotion: String) -> void:
    emotion = next_emotion
    actor_state.emotion = next_emotion
    _emit_state_changed()


func set_energy(next_energy: float) -> void:
    energy = clampf(next_energy, 0.0, 100.0)
    actor_state.energy = energy
    _emit_state_changed()


func set_attention(next_attention: String) -> void:
    attention = next_attention
    actor_state.attention = next_attention
    _emit_state_changed()


func state_snapshot() -> Dictionary:
    return actor_state.to_dictionary()


func apply_state_snapshot(snapshot: Dictionary) -> void:
    actor_state.apply_dictionary(snapshot)
    actor_id = actor_state.id
    emotion = actor_state.emotion
    energy = actor_state.energy
    attention = actor_state.attention
    inventory = actor_state.inventory.duplicate()
    current_anchor = actor_state.current_anchor
    _machine_state = _state_from_name(actor_state.machine_state)
    _emit_state_changed()


func _finish_movement() -> void:
    velocity = Vector3.ZERO
    if _target_anchor != "":
        current_anchor = _target_anchor
        actor_state.current_anchor = current_anchor

    var completed_reference := _target_anchor_reference.duplicate(true)
    _target_anchor_reference.clear()
    _target_anchor = ""

    move_completed.emit(actor_id, completed_reference)
    _publish_move_completed(completed_reference)
    _set_machine_state(ActorMachineState.IDLE)


func _set_machine_state(next_state: int) -> void:
    if _machine_state == next_state:
        return

    _machine_state = next_state
    actor_state.machine_state = STATE_NAMES[_machine_state]
    
    if _animation_player != null:
        var anim_name = STATE_NAMES[_machine_state]
        if _animation_player.has_animation(anim_name):
            _animation_player.play(anim_name)

    _emit_state_changed()


func _emit_state_changed() -> void:
    var snapshot := actor_state.to_dictionary()
    state_changed.emit(actor_id, snapshot)
    _publish_state_changed(snapshot)


func _ensure_navigation_agent() -> void:
    if _navigation_agent != null:
        return

    if navigation_agent_path != NodePath(""):
        _navigation_agent = get_node_or_null(navigation_agent_path) as NavigationAgent3D

    if _navigation_agent == null:
        _navigation_agent = find_child("NavigationAgent3D", false, false) as NavigationAgent3D

    if _navigation_agent == null:
        _navigation_agent = NavigationAgent3D.new()
        _navigation_agent.name = "NavigationAgent3D"
        add_child(_navigation_agent)

    _navigation_agent.path_desired_distance = arrival_distance
    _navigation_agent.target_desired_distance = arrival_distance


func _ensure_animation_player() -> void:
    if _animation_player != null:
        return

    if animation_player_path != NodePath(""):
        _animation_player = get_node_or_null(animation_player_path) as AnimationPlayer

    if _animation_player == null:
        _animation_player = find_child("AnimationPlayer", false, false) as AnimationPlayer


func _semantic_resolver():
    if semantic_world_resolver_path == NodePath(""):
        return null
    return get_node_or_null(semantic_world_resolver_path) as StoryForgeSemanticWorldResolver


func _event_bus():
    if event_bus_path == NodePath(""):
        return null
    return get_node_or_null(event_bus_path) as StoryForgeActorEvents


func _normalize_anchor_reference(anchor_reference: Variant) -> Dictionary:
    if typeof(anchor_reference) == TYPE_STRING:
        return {
            "anchor": str(anchor_reference),
            "relation": "at",
            "relative_to": null,
            "distance": "near"
        }

    if typeof(anchor_reference) == TYPE_DICTIONARY:
        var reference: Dictionary = anchor_reference.duplicate(true)
        reference["anchor"] = str(reference.get("anchor", ""))
        reference["relation"] = str(reference.get("relation", "at"))
        reference["distance"] = str(reference.get("distance", "near"))
        if not reference.has("relative_to"):
            reference["relative_to"] = null
        return reference

    return {
        "anchor": "",
        "relation": "at",
        "relative_to": null,
        "distance": "near"
    }


func _target_to_position(target: Variant):
    if typeof(target) == TYPE_VECTOR3:
        return target

    if target is Node3D:
        return target.global_position

    if typeof(target) == TYPE_STRING:
        var resolver := _semantic_resolver()
        if resolver == null:
            return null
        var anchor_reference := _normalize_anchor_reference(str(target))
        return resolver.resolve_position(anchor_reference)

    if typeof(target) == TYPE_DICTIONARY:
        var resolver := _semantic_resolver()
        if resolver == null:
            return null
        return resolver.resolve_position(target)

    return null


func _target_to_attention(target: Variant) -> String:
    if typeof(target) == TYPE_STRING:
        return str(target)
    if typeof(target) == TYPE_DICTIONARY:
        return str(target.get("anchor", ""))
    if target is Node:
        return target.name
    return ""


func _face_position(target_position: Vector3, up: Vector3 = Vector3.UP, use_model_front: bool = false) -> void:
    var flat_target := Vector3(target_position.x, global_position.y, target_position.z)
    if global_position.distance_to(flat_target) > 0.001:
        super.look_at(flat_target, up, use_model_front)


func _state_from_name(state_name: String) -> int:
    match state_name:
        "walk":
            return ActorMachineState.WALK
        "talk":
            return ActorMachineState.TALK
        "run":
            return ActorMachineState.RUN
        "interact":
            return ActorMachineState.INTERACT
        _:
            return ActorMachineState.IDLE


func _publish_registered() -> void:
    var bus := _event_bus()
    if bus != null:
        bus.publish_registered(actor_id, self)


func _publish_state_changed(snapshot: Dictionary) -> void:
    var bus := _event_bus()
    if bus != null:
        bus.publish_state_changed(actor_id, snapshot)


func _publish_move_requested(anchor_reference: Dictionary) -> void:
    var bus := _event_bus()
    if bus != null:
        bus.publish_move_requested(actor_id, anchor_reference)


func _publish_move_completed(anchor_reference: Dictionary) -> void:
    var bus := _event_bus()
    if bus != null:
        bus.publish_move_completed(actor_id, anchor_reference)


func _publish_spoke(text: String, metadata: Dictionary) -> void:
    var bus := _event_bus()
    if bus != null:
        bus.publish_spoke(actor_id, text, metadata)


func _publish_looked_at(target: Variant) -> void:
    var bus := _event_bus()
    if bus != null:
        bus.publish_looked_at(actor_id, target)


func _publish_inventory_changed(next_inventory: Array) -> void:
    var bus := _event_bus()
    if bus != null:
        bus.publish_inventory_changed(actor_id, next_inventory)


func _publish_intent_requested(intent_id: String, context: Dictionary) -> void:
    var bus := _event_bus()
    if bus != null:
        bus.publish_intent_requested(actor_id, intent_id, context)


func _publish_intent_completed(intent_id: String, result: Dictionary) -> void:
    var bus := _event_bus()
    if bus != null:
        bus.publish_intent_completed(actor_id, intent_id, result)


func _fail(message: String) -> void:
    actor_error.emit(actor_id, message)
    var bus := _event_bus()
    if bus != null:
        bus.publish_error(actor_id, message)
