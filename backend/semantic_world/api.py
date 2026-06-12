"""FastAPI router factory for the Semantic World System."""

from __future__ import annotations

from collections.abc import Callable

from fastapi import APIRouter, Depends, HTTPException, status

from .repository import (
    SemanticAnchorNotFoundError,
    SemanticWorldConflictError,
    SemanticWorldNotFoundError,
    SemanticWorldRepository,
)
from .schemas import (
    AnchorResolution,
    AnchorResolveRequest,
    SemanticAnchorCreate,
    SemanticAnchorRead,
    SemanticWorldCreate,
    SemanticWorldRead,
)
from .validation import resolve_reference, validate_anchor_create


def create_semantic_world_router(
    repository_provider: Callable[[], SemanticWorldRepository],
    *,
    prefix: str = "/worlds",
) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=["semantic-world"])

    def get_repository() -> SemanticWorldRepository:
        return repository_provider()

    @router.get("", response_model=list[SemanticWorldRead])
    async def list_worlds(
        repository: SemanticWorldRepository = Depends(get_repository),
    ) -> list[SemanticWorldRead]:
        return await repository.list_worlds()

    @router.post("", response_model=SemanticWorldRead, status_code=status.HTTP_201_CREATED)
    async def create_world(
        world: SemanticWorldCreate,
        repository: SemanticWorldRepository = Depends(get_repository),
    ) -> SemanticWorldRead:
        try:
            return await repository.create_world(world)
        except SemanticWorldConflictError as exc:
            raise HTTPException(status.HTTP_409_CONFLICT, "semantic world already exists") from exc

    @router.get("/{scene_asset_id}", response_model=SemanticWorldRead)
    async def get_world(
        scene_asset_id: str,
        repository: SemanticWorldRepository = Depends(get_repository),
    ) -> SemanticWorldRead:
        try:
            return await repository.get_world(scene_asset_id)
        except SemanticWorldNotFoundError as exc:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "semantic world not found") from exc

    @router.get("/{scene_asset_id}/anchors", response_model=list[SemanticAnchorRead])
    async def list_anchors(
        scene_asset_id: str,
        repository: SemanticWorldRepository = Depends(get_repository),
    ) -> list[SemanticAnchorRead]:
        await _require_world(repository, scene_asset_id)
        return await repository.list_anchors(scene_asset_id)

    @router.post("/{scene_asset_id}/anchors", response_model=SemanticAnchorRead, status_code=status.HTTP_201_CREATED)
    async def create_anchor(
        scene_asset_id: str,
        anchor: SemanticAnchorCreate,
        repository: SemanticWorldRepository = Depends(get_repository),
    ) -> SemanticAnchorRead:
        await _require_world(repository, scene_asset_id)

        errors = validate_anchor_create(anchor)
        if errors:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"valid": False, "errors": errors},
            )

        try:
            return await repository.create_anchor(scene_asset_id, anchor)
        except SemanticWorldConflictError as exc:
            raise HTTPException(status.HTTP_409_CONFLICT, "semantic anchor already exists") from exc

    @router.get("/{scene_asset_id}/anchors/{anchor}", response_model=SemanticAnchorRead)
    async def get_anchor(
        scene_asset_id: str,
        anchor: str,
        repository: SemanticWorldRepository = Depends(get_repository),
    ) -> SemanticAnchorRead:
        try:
            return await repository.get_anchor(scene_asset_id, anchor)
        except SemanticAnchorNotFoundError as exc:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "semantic anchor not found") from exc

    @router.post("/{scene_asset_id}/resolve", response_model=AnchorResolution)
    async def resolve_anchor_reference(
        scene_asset_id: str,
        request: AnchorResolveRequest,
        repository: SemanticWorldRepository = Depends(get_repository),
    ) -> AnchorResolution:
        await _require_world(repository, scene_asset_id)
        anchors = await repository.list_anchors(scene_asset_id)
        known_anchors = {anchor.anchor: anchor for anchor in anchors}
        return resolve_reference(
            scene_asset_id=scene_asset_id,
            known_anchors=known_anchors,
            request=request,
        )

    return router


async def _require_world(repository: SemanticWorldRepository, scene_asset_id: str) -> None:
    try:
        await repository.get_world(scene_asset_id)
    except SemanticWorldNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "semantic world not found") from exc
