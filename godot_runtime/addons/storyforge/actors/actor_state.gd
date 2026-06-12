extends Resource
class_name StoryForgeActorState

@export var id: String = ""
@export var emotion: String = "neutral"
@export_range(0.0, 100.0, 1.0) var energy: float = 100.0
@export var attention: String = ""
@export var inventory: Array[String] = []
@export var current_anchor: String = ""
@export var machine_state: String = "idle"


func to_dictionary() -> Dictionary:
    return {
        "id": id,
        "emotion": emotion,
        "energy": energy,
        "attention": attention,
        "inventory": inventory.duplicate(),
        "current_anchor": current_anchor,
        "machine_state": machine_state
    }


func apply_dictionary(data: Dictionary) -> void:
    id = str(data.get("id", id))
    emotion = str(data.get("emotion", emotion))
    energy = clampf(float(data.get("energy", energy)), 0.0, 100.0)
    attention = str(data.get("attention", attention))
    current_anchor = str(data.get("current_anchor", current_anchor))
    machine_state = str(data.get("machine_state", machine_state))

    inventory.clear()
    for item in data.get("inventory", inventory):
        inventory.append(str(item))
