"""Constants for Asset Registry validation and discovery."""

from __future__ import annotations

ASSET_TYPES = (
    "character",
    "scene",
    "prop",
    "animation",
    "voice",
    "camera",
    "intent",
)

ASSET_TYPE_PREFIXES = {
    "character": "char",
    "scene": "scene",
    "prop": "prop",
    "animation": "anim",
    "voice": "voice",
    "camera": "cam",
    "intent": "intent",
}

RESOURCE_BACKED_TYPES = {
    "character",
    "scene",
    "prop",
    "animation",
    "voice",
}

METADATA_REQUIRED_KEYS = {
    "character": (),
    "scene": (),
    "prop": (),
    "animation": (),
    "voice": (),
    "camera": ("preset",),
    "intent": ("description",),
}
