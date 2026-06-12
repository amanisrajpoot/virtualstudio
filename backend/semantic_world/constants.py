"""Semantic World constants."""

from __future__ import annotations

ANCHOR_ID_PATTERN = r"^[a-z][a-z0-9_]*$"

DEFAULT_ANCHOR_GROUP = "storyforge_anchor"

RELATION_DISTANCE_METERS = {
    "contact": 0.5,
    "near": 1.5,
    "medium": 3.0,
    "far": 6.0,
}
