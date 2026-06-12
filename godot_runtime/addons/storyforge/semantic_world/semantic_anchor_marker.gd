extends Marker3D
class_name StoryForgeSemanticAnchorMarker

@export var anchor_id: String = ""
@export var tags: PackedStringArray = PackedStringArray()


func _ready() -> void:
    if anchor_id == "":
        anchor_id = name.to_snake_case()

    add_to_group("storyforge_anchor")
    set_meta("storyforge_anchor_id", anchor_id)
    set_meta("storyforge_anchor_tags", tags)
