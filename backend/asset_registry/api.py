"""FastAPI router factory for the Asset Registry subsystem."""

from __future__ import annotations

from collections.abc import Callable

from fastapi import APIRouter, Depends, HTTPException, Query, status

from .schemas import AssetCreate, AssetRead, AssetType, AssetUpdate, AssetValidationResult
from .repository import AssetConflictError, AssetNotFoundError, AssetRepository
from .validation import validate_asset_create, validate_asset_update


def create_asset_registry_router(
    repository_provider: Callable[[], AssetRepository],
    *,
    prefix: str = "/assets",
) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=["asset-registry"])

    def get_repository() -> AssetRepository:
        return repository_provider()

    @router.get("", response_model=list[AssetRead])
    async def list_assets(
        type: AssetType | None = Query(None, description="Filter by asset type."),
        q: str | None = Query(None, min_length=1, description="Search by ID or name."),
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
        repository: AssetRepository = Depends(get_repository),
    ) -> list[AssetRead]:
        asset_type = type.value if type else None
        return await repository.list_assets(
            asset_type=asset_type,
            query=q,
            limit=limit,
            offset=offset,
        )

    @router.get("/{asset_id}", response_model=AssetRead)
    async def get_asset(
        asset_id: str,
        repository: AssetRepository = Depends(get_repository),
    ) -> AssetRead:
        try:
            return await repository.get_asset(asset_id)
        except AssetNotFoundError as exc:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "asset not found") from exc

    @router.post("/validate", response_model=AssetValidationResult)
    async def validate_asset(asset: AssetCreate) -> AssetValidationResult:
        return validate_asset_create(asset)

    @router.post("", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
    async def create_asset(
        asset: AssetCreate,
        repository: AssetRepository = Depends(get_repository),
    ) -> AssetRead:
        validation = validate_asset_create(asset)
        if not validation.valid:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=_model_dump(validation),
            )

        try:
            return await repository.create_asset(asset)
        except AssetConflictError as exc:
            raise HTTPException(status.HTTP_409_CONFLICT, "asset already exists") from exc

    @router.patch("/{asset_id}", response_model=AssetRead)
    async def update_asset(
        asset_id: str,
        patch: AssetUpdate,
        repository: AssetRepository = Depends(get_repository),
    ) -> AssetRead:
        try:
            existing = await repository.get_asset(asset_id)
        except AssetNotFoundError as exc:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "asset not found") from exc

        validation = validate_asset_update(existing.type, patch)
        if not validation.valid:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=_model_dump(validation),
            )

        return await repository.update_asset(asset_id, patch)

    @router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_asset(
        asset_id: str,
        repository: AssetRepository = Depends(get_repository),
    ) -> None:
        try:
            await repository.delete_asset(asset_id)
        except AssetNotFoundError as exc:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "asset not found") from exc

    return router


def _model_dump(model: AssetValidationResult) -> dict:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()
