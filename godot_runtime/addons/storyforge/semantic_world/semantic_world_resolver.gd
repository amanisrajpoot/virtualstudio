extends Node
class_name StoryForgeSemanticWorldResolver

signal anchor_indexed(anchor_id: String, node: Node3D)
signal anchor_missing(anchor_id: String)

const DEFAULT_DISTANCE_METERS := {
    "contact": 0.5,
    "near": 1.5,
    "medium": 3.0,
    "far": 6.0
}

@export var anchor_group: String = "storyforge_anchor"
@export var anchor_metadata_key: String = "storyforge_anchor_id"

var _anchors: Dictionary = {}


func index_scene(root: Node) -> void:
    _anchors.clear()
    if root == null:
        return

    var nodes := root.get_tree().get_nodes_in_group(anchor_group)
    for node in nodes:
        if node is Node3D:
            var anchor_id := _anchor_id_for_node(node)
            if anchor_id != "":
                _anchors[anchor_id] = node
                anchor_indexed.emit(anchor_id, node)


func has_anchor(anchor_id: String) -> bool:
    return _anchors.has(anchor_id)


func get_anchor_node(anchor_id: String) -> Node3D:
    if not _anchors.has(anchor_id):
        anchor_missing.emit(anchor_id)
        return null
    return _anchors[anchor_id]


func resolve(anchor_reference: Dictionary) -> Transform3D:
    var anchor_id := str(anchor_reference.get("anchor", ""))
    var relation := str(anchor_reference.get("relation", "at"))
    var relative_to := str(anchor_reference.get("relative_to", ""))
    var distance_key := str(anchor_reference.get("distance", "near"))

    if relation == "at" or relative_to == "":
        var anchor_node := get_anchor_node(anchor_id)
        if anchor_node == null:
            return Transform3D.IDENTITY
        return anchor_node.global_transform

    var base_node := get_anchor_node(relative_to)
    if base_node == null:
        return Transform3D.IDENTITY

    var transform := base_node.global_transform
    var offset := _relative_offset(transform.basis, relation, distance_key)
    transform.origin += offset

    if has_anchor(anchor_id):
        var target_node := get_anchor_node(anchor_id)
        if target_node != null:
            transform = transform.looking_at(target_node.global_transform.origin, Vector3.UP)

    return transform


func resolve_position(anchor_reference: Dictionary) -> Vector3:
    return resolve(anchor_reference).origin


func anchors() -> Array:
    return _anchors.keys()


func _anchor_id_for_node(node: Node) -> String:
    if node.has_meta(anchor_metadata_key):
        return str(node.get_meta(anchor_metadata_key))
    return node.name.to_snake_case()


func _relative_offset(basis: Basis, relation: String, distance_key: String) -> Vector3:
    var distance := float(DEFAULT_DISTANCE_METERS.get(distance_key, DEFAULT_DISTANCE_METERS["near"]))

    match relation:
        "near":
            return -basis.z.normalized() * distance
        "left_of":
            return -basis.x.normalized() * distance
        "right_of":
            return basis.x.normalized() * distance
        "in_front_of":
            return -basis.z.normalized() * distance
        "behind":
            return basis.z.normalized() * distance
        "facing":
            return -basis.z.normalized() * distance
        _:
            return Vector3.ZERO
