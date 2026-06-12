"""Pydantic contracts for Asset Registry API payloads."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AssetType(str, Enum):
    CHARACTER = "character"
    SCENE = "scene"
    PROP = "prop"
    ANIMATION = "animation"
    VOICE = "voice"
    CAMERA = "camera"
    INTENT = "intent"


class AssetBase(BaseModel):
    id: str = Field(
        ...,
        min_length=3,
        max_length=120,
        description="Stable lowercase asset ID, for example char_halku_v1.",
    )
    type: AssetType
    name: str = Field(..., min_length=1, max_length=160)
    version: str = Field("1.0.0", description="Semantic version for this asset record.")
    path: str | None = Field(
        None,
        description="Godot resource path, external object path, or null for logical assets.",
    )
    metadata: dict[str, Any] = Field(default_factory=dict)


class AssetCreate(AssetBase):
    """Payload used to register a new versioned asset."""


class AssetUpdate(BaseModel):
    """Mutable fields for an existing asset.

    ID, type, and version are immutable. Register a new asset row for a new
    asset version.
    """

    name: str | None = Field(None, min_length=1, max_length=160)
    path: str | None = None
    metadata: dict[str, Any] | None = None


class AssetRead(AssetBase):
    created_at: datetime
    updated_at: datetime


class AssetValidationResult(BaseModel):
    valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
