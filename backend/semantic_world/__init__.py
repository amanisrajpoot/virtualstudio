"""Semantic World subsystem.

Semantic worlds replace authored coordinates with scene-specific anchors. This
package stores and validates anchor contracts; Godot resolves anchors to real
transforms at runtime.
"""

from .schemas import (
    AnchorRelation,
    AnchorResolution,
    AnchorResolveRequest,
    SemanticAnchorCreate,
    SemanticAnchorRead,
    SemanticWorldCreate,
    SemanticWorldRead,
)

__all__ = [
    "AnchorRelation",
    "AnchorResolution",
    "AnchorResolveRequest",
    "SemanticAnchorCreate",
    "SemanticAnchorRead",
    "SemanticWorldCreate",
    "SemanticWorldRead",
]
