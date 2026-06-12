"""Validation rules for registry assets.

The database enforces broad shape constraints. This module enforces the
StoryForge-specific registry conventions before records are persisted.
"""

from __future__ import annotations

import re
from typing import Any

from .constants import ASSET_TYPE_PREFIXES, METADATA_REQUIRED_KEYS, RESOURCE_BACKED_TYPES
from .schemas import AssetCreate, AssetType, AssetUpdate, AssetValidationResult

ASSET_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]*_v[0-9]+$")
SEMVER_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")


def validate_asset_create(asset: AssetCreate) -> AssetValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    asset_type = _type_value(asset.type)
    _validate_id(asset.id, asset_type, errors)
    _validate_version(asset.version, asset.id, errors)
    _validate_path(asset_type, asset.path, errors, warnings)
    _validate_metadata(asset_type, asset.metadata, errors)

    return AssetValidationResult(valid=not errors, errors=errors, warnings=warnings)


def validate_asset_update(asset_type: AssetType | str, patch: AssetUpdate) -> AssetValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    type_value = _type_value(asset_type)
    if patch.metadata is not None:
        _validate_metadata(type_value, patch.metadata, errors)

    if "path" in patch.model_fields_set:
        _validate_path(type_value, patch.path, errors, warnings)

    return AssetValidationResult(valid=not errors, errors=errors, warnings=warnings)


def _validate_id(asset_id: str, asset_type: str, errors: list[str]) -> None:
    if not ASSET_ID_PATTERN.match(asset_id):
        errors.append("id must be lowercase snake_case and end with _vN, for example char_halku_v1")
        return

    expected_prefix = ASSET_TYPE_PREFIXES[asset_type]
    if not asset_id.startswith(f"{expected_prefix}_"):
        errors.append(f"id for type {asset_type} must start with {expected_prefix}_")


def _validate_version(version: str, asset_id: str, errors: list[str]) -> None:
    if not SEMVER_PATTERN.match(version):
        errors.append("version must use semantic version format, for example 1.0.0")
        return

    id_major = asset_id.rsplit("_v", 1)[-1]
    version_major = version.split(".", 1)[0]
    if id_major.isdigit() and id_major != version_major:
        errors.append("id version suffix must match semantic version major, for example *_v1 with 1.0.0")


def _validate_path(asset_type: str, path: str | None, errors: list[str], warnings: list[str]) -> None:
    if asset_type in RESOURCE_BACKED_TYPES and not path:
        errors.append(f"path is required for resource-backed asset type {asset_type}")
        return

    if not path:
        return

    valid_prefixes = ("res://", "s3://", "file://", "registry://")
    if not path.startswith(valid_prefixes):
        warnings.append("path should use res://, s3://, file://, or registry://")


def _validate_metadata(asset_type: str, metadata: dict[str, Any], errors: list[str]) -> None:
    if not isinstance(metadata, dict):
        errors.append("metadata must be a JSON object")
        return

    for key in METADATA_REQUIRED_KEYS[asset_type]:
        if key not in metadata:
            errors.append(f"metadata for {asset_type} assets must include {key}")


def _type_value(asset_type: AssetType | str) -> str:
    return asset_type.value if isinstance(asset_type, AssetType) else asset_type
