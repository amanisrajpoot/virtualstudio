"""Pydantic contracts for the Semantic World System."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AnchorRelation(str, Enum):
    AT = "at"
    NEAR = "near"
    LEFT_OF = "left_of"
    RIGHT_OF = "right_of"
    IN_FRONT_OF = "in_front_of"
    BEHIND = "behind"
    FACING = "facing"


class RelativeDistance(str, Enum):
    CONTACT = "contact"
    NEAR = "near"
    MEDIUM = "medium"
    FAR = "far"


class SemanticWorldCreate(BaseModel):
    scene_asset_id: str = Field(..., description="Scene asset ID from the Asset Registry.")
    version: str = Field("1.0.0", description="Semantic world definition version.")
    metadata: dict[str, Any] = Field(default_factory=dict)


class SemanticWorldRead(SemanticWorldCreate):
    created_at: datetime
    updated_at: datetime


class SemanticAnchorCreate(BaseModel):
    anchor: str = Field(
        ...,
        min_length=1,
        max_length=80,
        description="Scene-local semantic anchor ID, for example market_center.",
    )
    display_name: str = Field(..., min_length=1, max_length=160)
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SemanticAnchorRead(SemanticAnchorCreate):
    scene_asset_id: str
    created_at: datetime
    updated_at: datetime


class AnchorResolveRequest(BaseModel):
    anchor: str = Field(..., description="Primary anchor to resolve.")
    relation: AnchorRelation = Field(AnchorRelation.AT)
    relative_to: str | None = Field(
        None,
        description="Anchor used as the relation base for relative positioning.",
    )
    distance: RelativeDistance = Field(RelativeDistance.NEAR)
    require_tags: list[str] = Field(
        default_factory=list,
        description="Optional tags the resolved anchor must include.",
    )


class AnchorResolution(BaseModel):
    scene_asset_id: str
    anchor: str
    relation: AnchorRelation
    relative_to: str | None = None
    distance: RelativeDistance
    valid: bool
    errors: list[str] = Field(default_factory=list)
    lookup: dict[str, Any] = Field(default_factory=dict)
    runtime_reference: dict[str, Any] = Field(default_factory=dict)
