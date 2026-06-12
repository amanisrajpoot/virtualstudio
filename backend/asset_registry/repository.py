"""PostgreSQL repository for Asset Registry records.

This repository expects an asyncpg-compatible connection pool. The API layer
passes records through validation before persistence.
"""

from __future__ import annotations

import json
from typing import Any

from .schemas import AssetCreate, AssetRead, AssetUpdate


class AssetNotFoundError(LookupError):
    """Raised when an asset ID is not present in the registry."""


class AssetConflictError(ValueError):
    """Raised when an asset ID or versioned identity already exists."""


class AssetRepository:
    def __init__(self, pool: Any) -> None:
        self._pool = pool

    async def list_assets(
        self,
        *,
        asset_type: str | None = None,
        query: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AssetRead]:
        clauses: list[str] = []
        values: list[Any] = []

        if asset_type:
            values.append(asset_type)
            clauses.append(f"type = ${len(values)}::asset_type")

        if query:
            values.append(f"%{query}%")
            clauses.append(f"(name ILIKE ${len(values)} OR id ILIKE ${len(values)})")

        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        values.extend([limit, offset])
        limit_param = len(values) - 1
        offset_param = len(values)

        sql = f"""
            SELECT id, type::text, name, version, path, metadata, created_at, updated_at
            FROM assets
            {where}
            ORDER BY type, name, version
            LIMIT ${limit_param}
            OFFSET ${offset_param}
        """

        async with self._pool.acquire() as conn:
            rows = await conn.fetch(sql, *values)

        return [_row_to_asset(row) for row in rows]

    async def get_asset(self, asset_id: str) -> AssetRead:
        sql = """
            SELECT id, type::text, name, version, path, metadata, created_at, updated_at
            FROM assets
            WHERE id = $1
        """
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(sql, asset_id)

        if row is None:
            raise AssetNotFoundError(asset_id)
        return _row_to_asset(row)

    async def create_asset(self, asset: AssetCreate) -> AssetRead:
        sql = """
            INSERT INTO assets (id, type, name, version, path, metadata)
            VALUES ($1, $2::asset_type, $3, $4, $5, $6::jsonb)
            RETURNING id, type::text, name, version, path, metadata, created_at, updated_at
        """
        values = (
            asset.id,
            asset.type.value,
            asset.name,
            asset.version,
            asset.path,
            json.dumps(asset.metadata),
        )

        try:
            async with self._pool.acquire() as conn:
                row = await conn.fetchrow(sql, *values)
        except Exception as exc:
            if _is_unique_violation(exc):
                raise AssetConflictError(asset.id) from exc
            raise

        return _row_to_asset(row)

    async def update_asset(self, asset_id: str, patch: AssetUpdate) -> AssetRead:
        existing = await self.get_asset(asset_id)

        name = patch.name if patch.name is not None else existing.name
        path = patch.path if patch.path is not None else existing.path
        metadata = patch.metadata if patch.metadata is not None else existing.metadata

        sql = """
            UPDATE assets
            SET name = $2,
                path = $3,
                metadata = $4::jsonb
            WHERE id = $1
            RETURNING id, type::text, name, version, path, metadata, created_at, updated_at
        """

        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(sql, asset_id, name, path, json.dumps(metadata))

        if row is None:
            raise AssetNotFoundError(asset_id)
        return _row_to_asset(row)

    async def delete_asset(self, asset_id: str) -> None:
        async with self._pool.acquire() as conn:
            result = await conn.execute("DELETE FROM assets WHERE id = $1", asset_id)

        if result == "DELETE 0":
            raise AssetNotFoundError(asset_id)


def _row_to_asset(row: Any) -> AssetRead:
    metadata = row["metadata"]
    if isinstance(metadata, str):
        metadata = json.loads(metadata)

    return AssetRead(
        id=row["id"],
        type=row["type"],
        name=row["name"],
        version=row["version"],
        path=row["path"],
        metadata=metadata,
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _is_unique_violation(exc: Exception) -> bool:
    sqlstate = getattr(exc, "sqlstate", None)
    if sqlstate == "23505":
        return True
    return exc.__class__.__name__ in {"UniqueViolationError", "IntegrityError"}
