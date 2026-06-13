"""Marketplace Schemas."""

from enum import Enum
from pydantic import BaseModel
from typing import List, Optional

class AssetType(str, Enum):
    CHARACTER = "character"
    WORLD = "world"
    TEMPLATE = "template"
    STORY_GRAPH = "story_graph"
    FORMATION = "formation"
    VOICE_PROFILE = "voice_profile"

class AssetLineage(BaseModel):
    root_asset_id: str
    parent_asset_id: Optional[str] = None
    depth: int = 0

class AssetVersion(BaseModel):
    version: int
    summary: str
    timestamp: str

class MarketplaceAsset(BaseModel):
    asset_id: str
    asset_type: AssetType
    source_id: str
    title: str
    description: str
    author_id: str
    tags: List[str] = []
    
    versions: List[AssetVersion] = []
    
    downloads: int = 0
    forks: int = 0
    
    rating: float = 0.0
    rating_count: int = 0
    
    health_score: int = 100
    compatibility_score: float = 0.0
    featured: bool = False
    
    lineage: Optional[AssetLineage] = None
    
    # Semantic Compatibility Vectors
    compatible_worlds: List[str] = []
    compatible_formations: List[str] = []
    compatible_goals: List[str] = []
    required_assets: List[str] = []
    
    created_at: str
    updated_at: str

class AssetRating(BaseModel):
    asset_id: str
    user_id: str
    score: int # 1 to 5
    timestamp: str
