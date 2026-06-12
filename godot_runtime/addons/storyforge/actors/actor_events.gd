extends Node
class_name StoryForgeActorEvents

signal actor_registered(actor_id: String, actor: Node)
signal actor_state_changed(actor_id: String, state: Dictionary)
signal actor_move_requested(actor_id: String, anchor_reference: Dictionary)
signal actor_move_completed(actor_id: String, anchor_reference: Dictionary)
signal actor_spoke(actor_id: String, text: String, metadata: Dictionary)
signal actor_looked_at(actor_id: String, target: Variant)
signal actor_inventory_changed(actor_id: String, inventory: Array)
signal actor_intent_requested(actor_id: String, intent_id: String, context: Dictionary)
signal actor_intent_completed(actor_id: String, intent_id: String, result: Dictionary)
signal actor_error(actor_id: String, message: String)


func publish_registered(actor_id: String, actor: Node) -> void:
    actor_registered.emit(actor_id, actor)


func publish_state_changed(actor_id: String, state: Dictionary) -> void:
    actor_state_changed.emit(actor_id, state)


func publish_move_requested(actor_id: String, anchor_reference: Dictionary) -> void:
    actor_move_requested.emit(actor_id, anchor_reference)


func publish_move_completed(actor_id: String, anchor_reference: Dictionary) -> void:
    actor_move_completed.emit(actor_id, anchor_reference)


func publish_spoke(actor_id: String, text: String, metadata: Dictionary) -> void:
    actor_spoke.emit(actor_id, text, metadata)


func publish_looked_at(actor_id: String, target: Variant) -> void:
    actor_looked_at.emit(actor_id, target)


func publish_inventory_changed(actor_id: String, inventory: Array) -> void:
    actor_inventory_changed.emit(actor_id, inventory)


func publish_intent_requested(actor_id: String, intent_id: String, context: Dictionary) -> void:
    actor_intent_requested.emit(actor_id, intent_id, context)


func publish_intent_completed(actor_id: String, intent_id: String, result: Dictionary) -> void:
    actor_intent_completed.emit(actor_id, intent_id, result)


func publish_error(actor_id: String, message: String) -> void:
    actor_error.emit(actor_id, message)
