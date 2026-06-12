"""PostgreSQL repository for Semantic World records."""

from __future__ import annotations

import json
from typing import Any

from .schemas import SemanticAnchorCreate, SemanticAnchorRead, SemanticWorldCreate, SemanticWorldRead


class SemanticWorldNotFoundError(LookupError):
    """Raised when a scene has no semantic world definition."""


class SemanticAnchorNotFoundError(LookupError):
    """Raised when a scene-local anchor does not exist."""


class SemanticWorldConflictError(ValueError):
    """Raised when a world or anchor already exists."""


class SemanticWorldRepository:
    def __init__(self, pool: Any) -> None:
        self._pool = pool

    async def list_worlds(self) -> list[SemanticWorldRead]:
        sql = """
            SELECT scene_asset_id, version, metadata, created_at, updated_at
            FROM semantic_worlds
            ORDER BY scene_asset_id
        """
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(sql)
        return [_row_to_world(row) for row in rows]

    async def get_world(self, scene_asset_id: str) -> SemanticWorldRead:
        sql = """
            SELECT scene_asset_id, version, metadata, created_at, updated_at
            FROM semantic_worlds
            WHERE scene_asset_id = $1
        """
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(sql, scene_asset_id)
        if row is None:
            raise SemanticWorldNotFoundError(scene_asset_id)
        return _row_to_world(row)

    async def create_world(self, world: SemanticWorldCreate) -> SemanticWorldRead:
        sql = """
            INSERT INTO semantic_worlds (scene_asset_id, version, metadata)
            VALUES ($1, $2, $3::jsonb)
            RETURNING scene_asset_id, version, metadata, created_at, updated_at
        """
        try:
            async with self._pool.acquire() as conn:
                row = await conn.fetchrow(
                    sql,
                    world.scene_asset_id,
                    world.version,
                    json.dumps(world.metadata),
                )
        except Exception as exc:
            if _is_unique_violation(exc):
                raise SemanticWorldConflictError(world.scene_asset_id) from exc
            raise
        return _row_to_world(row)

    async def list_anchors(self, scene_asset_id: str) -> list[SemanticAnchorRead]:
        sql = """
            SELECT scene_asset_id, anchor, display_name, tags, metadata, created_at, updated_at
            FROM semantic_anchors
            WHERE scene_asset_id = $1
            ORDER BY anchor
        """
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(sql, scene_asset_id)
        return [_row_to_anchor(row) for row in rows]

    async def get_anchor(self, scene_asset_id: str, anchor: str) -> SemanticAnchorRead:
        sql = """
            SELECT scene_asset_id, anchor, display_name, tags, metadata, created_at, updated_at
            FROM semantic_anchors
            WHERE scene_asset_id = $1 AND anchor = $2
        """
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(sql, scene_asset_id, anchor)
        if row is None:
            raise SemanticAnchorNotFoundError(anchor)
        return _row_to_anchor(row)

    async def create_anchor(self, scene_asset_id: str, anchor: SemanticAnchorCreate) -> SemanticAnchorRead:
        sql = """
            INSERT INTO semantic_anchors (scene_asset_id, anchor, display_name, tags, metadata)
            VALUES ($1, $2, $3, $4, $5::jsonb)
            RETURNING scene_asset_id, anchor, display_name, tags, metadata, created_at, updated_at
        """
        try:
            async with self._pool.acquire() as conn:
                row = await conn.fetchrow(
                    sql,
                    scene_asset_id,
                    anchor.anchor,
                    anchor.display_name,
                    anchor.tags,
                    json.dumps(anchor.metadata),
                )
        except Exception as exc:
            if _is_unique_violation(exc):
                raise SemanticWorldConflictError(anchor.anchor) from exc
            raise
        return _row_to_anchor(row)


def _row_to_world(row: Any) -> SemanticWorldRead:
    metadata = row["metadata"]
    if isinstance(metadata, str):
        metadata = json.loads(metadata)
    return SemanticWorldRead(
        scene_asset_id=row["scene_asset_id"],
        version=row["version"],
        metadata=metadata,
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _row_to_anchor(row: Any) -> SemanticAnchorRead:
    metadata = row["metadata"]
    if isinstance(metadata, str):
        metadata = json.loads(metadata)
    return SemanticAnchorRead(
        scene_asset_id=row["scene_asset_id"],
        anchor=row["anchor"],
        display_name=row["display_name"],
        tags=list(row["tags"] or []),
        metadata=metadata,
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _is_unique_violation(exc: Exception) -> bool:
    sqlstate = getattr(exc, "sqlstate", None)
    if sqlstate == "23505":
        return True
    return exc.__class__.__name__ in {"UniqueViolationError", "IntegrityError"}
