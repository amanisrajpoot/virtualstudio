import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import asyncpg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.asset_registry.api import create_asset_registry_router
from backend.asset_registry.repository import AssetRepository
from backend.semantic_world.api import create_semantic_world_router
from backend.semantic_world.repository import SemanticWorldRepository

# Database configuration
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "storyforge")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

class AppState:
    pool: asyncpg.Pool | None = None

app_state = AppState()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    pool = await asyncpg.create_pool(dsn=DATABASE_URL)
    if pool is None:
        raise RuntimeError("Failed to create database pool")
    app_state.pool = pool
    yield
    # Shutdown
    await app_state.pool.close()

app = FastAPI(title="StoryForge API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_asset_repository() -> AssetRepository:
    if app_state.pool is None:
        raise RuntimeError("Database pool not initialized")
    return AssetRepository(app_state.pool)

def get_semantic_world_repository() -> SemanticWorldRepository:
    if app_state.pool is None:
        raise RuntimeError("Database pool not initialized")
    return SemanticWorldRepository(app_state.pool)

app.include_router(create_asset_registry_router(get_asset_repository))
app.include_router(create_semantic_world_router(get_semantic_world_repository))

@app.get("/health")
async def health_check() -> dict:
    if app_state.pool is None:
        return {"status": "unhealthy", "reason": "db pool not initialized"}
    
    try:
        async with app_state.pool.acquire() as conn:
            await conn.execute("SELECT 1")
    except Exception as e:
        return {"status": "unhealthy", "reason": str(e)}
        
    return {"status": "ok"}
