"""Validation helpers for Semantic World definitions and references."""

from __future__ import annotations

import re

from .constants import ANCHOR_ID_PATTERN, DEFAULT_ANCHOR_GROUP
from .schemas import AnchorResolveRequest, AnchorResolution, SemanticAnchorCreate

ANCHOR_ID_RE = re.compile(ANCHOR_ID_PATTERN)


def validate_anchor_create(anchor: SemanticAnchorCreate) -> list[str]:
    errors: list[str] = []

    if not ANCHOR_ID_RE.match(anchor.anchor):
        errors.append("anchor must be lowercase snake_case, for example market_center")

    for tag in anchor.tags:
        if not ANCHOR_ID_RE.match(tag):
            errors.append(f"tag must be lowercase snake_case: {tag}")

    if not isinstance(anchor.metadata, dict):
        errors.append("metadata must be a JSON object")

    return errors


def resolve_reference(
    *,
    scene_asset_id: str,
    known_anchors: dict[str, SemanticAnchorCreate],
    request: AnchorResolveRequest,
) -> AnchorResolution:
    errors: list[str] = []

    if request.anchor not in known_anchors:
        errors.append(f"anchor does not exist in scene {scene_asset_id}: {request.anchor}")

    if request.relative_to and request.relative_to not in known_anchors:
        errors.append(f"relative_to anchor does not exist in scene {scene_asset_id}: {request.relative_to}")

    if request.relation.value != "at" and not request.relative_to:
        errors.append("relative_to is required when relation is not at")

    anchor_record = known_anchors.get(request.anchor)
    if anchor_record is not None:
        missing_tags = [tag for tag in request.require_tags if tag not in anchor_record.tags]
        if missing_tags:
            errors.append(f"anchor {request.anchor} is missing required tags: {', '.join(missing_tags)}")

    lookup = {
        "group": DEFAULT_ANCHOR_GROUP,
        "metadata_key": "storyforge_anchor_id",
        "node_name": request.anchor,
    }

    runtime_reference = {
        "anchor": request.anchor,
        "relation": request.relation.value,
        "relative_to": request.relative_to,
        "distance": request.distance.value,
    }

    return AnchorResolution(
        scene_asset_id=scene_asset_id,
        anchor=request.anchor,
        relation=request.relation,
        relative_to=request.relative_to,
        distance=request.distance,
        valid=not errors,
        errors=errors,
        lookup=lookup,
        runtime_reference=runtime_reference,
    )
