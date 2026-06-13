"""Marketplace Repository."""

import os
import json
import uuid
import datetime
from typing import List, Optional, Dict, Any
from backend.models.marketplace import MarketplaceAsset, AssetRating, AssetLineage, AssetVersion, AssetType
from backend.repositories.characters import CharacterRepository

class MarketplaceRepository:
    def __init__(self, data_dir: str = "data/marketplace"):
        self.data_dir = data_dir
        self.assets_path = os.path.join(data_dir, "assets.json")
        self.ratings_path = os.path.join(data_dir, "ratings.json")
        os.makedirs(data_dir, exist_ok=True)
        self.char_repo = CharacterRepository() # Used for forking characters

    def _load_assets(self) -> List[MarketplaceAsset]:
        if not os.path.exists(self.assets_path):
            return []
        try:
            with open(self.assets_path, 'r') as f:
                data = json.load(f)
                return [MarketplaceAsset(**x) for x in data]
        except Exception:
            return []

    def _save_assets(self, assets: List[MarketplaceAsset]):
        with open(self.assets_path, 'w') as f:
            json.dump([a.model_dump() for a in assets], f, indent=2)

    def _load_ratings(self) -> List[AssetRating]:
        if not os.path.exists(self.ratings_path):
            return []
        try:
            with open(self.ratings_path, 'r') as f:
                data = json.load(f)
                return [AssetRating(**x) for x in data]
        except Exception:
            return []

    def _save_ratings(self, ratings: List[AssetRating]):
        with open(self.ratings_path, 'w') as f:
            json.dump([r.model_dump() for r in ratings], f, indent=2)

    def get_assets(self, type_filter: Optional[str] = None, goal_filter: Optional[str] = None, tag_filter: Optional[str] = None, featured_only: bool = False) -> List[MarketplaceAsset]:
        assets = self._load_assets()
        res = []
        for a in assets:
            if type_filter and a.asset_type != type_filter:
                continue
            if goal_filter and goal_filter not in a.compatible_goals:
                continue
            if tag_filter and tag_filter not in a.tags:
                continue
            if featured_only and not a.featured:
                continue
            res.append(a)
        return res

    def get_asset(self, asset_id: str) -> Optional[MarketplaceAsset]:
        assets = self._load_assets()
        for a in assets:
            if a.asset_id == asset_id:
                return a
        return None

    def publish_asset(self, req_data: Dict[str, Any], author_id: str) -> MarketplaceAsset:
        assets = self._load_assets()
        now = datetime.datetime.now().isoformat()
        
        # Check if updating
        existing = None
        for a in assets:
            if a.source_id == req_data.get("source_id") and a.asset_type == req_data.get("asset_type"):
                existing = a
                break
                
        if existing:
            # Bump version
            new_v = existing.versions[-1].version + 1 if existing.versions else 1
            v_sum = req_data.get("version_summary", f"Updated to v{new_v}")
            existing.versions.append(AssetVersion(version=new_v, summary=v_sum, timestamp=now))
            existing.updated_at = now
            # Update meta
            existing.title = req_data.get("title", existing.title)
            existing.description = req_data.get("description", existing.description)
            existing.tags = req_data.get("tags", existing.tags)
            self._save_assets(assets)
            return existing
        
        # New asset
        new_id = str(uuid.uuid4())
        lineage = AssetLineage(root_asset_id=new_id, parent_asset_id=None, depth=0)
        
        asset = MarketplaceAsset(
            asset_id=new_id,
            asset_type=req_data["asset_type"],
            source_id=req_data["source_id"],
            title=req_data["title"],
            description=req_data["description"],
            author_id=author_id,
            tags=req_data.get("tags", []),
            versions=[AssetVersion(version=1, summary="Initial Publish", timestamp=now)],
            lineage=lineage,
            compatible_worlds=req_data.get("compatible_worlds", []),
            compatible_formations=req_data.get("compatible_formations", []),
            compatible_goals=req_data.get("compatible_goals", []),
            required_assets=req_data.get("required_assets", []),
            health_score=req_data.get("health_score", 100),
            created_at=now,
            updated_at=now
        )
        assets.append(asset)
        self._save_assets(assets)
        return asset

    def record_download(self, asset_id: str):
        assets = self._load_assets()
        for a in assets:
            if a.asset_id == asset_id:
                a.downloads += 1
                self._save_assets(assets)
                return True
        return False

    def fork_asset(self, asset_id: str, new_author_id: str) -> Optional[MarketplaceAsset]:
        assets = self._load_assets()
        parent = None
        for a in assets:
            if a.asset_id == asset_id:
                parent = a
                break
                
        if not parent:
            return None
            
        now = datetime.datetime.now().isoformat()
        
        # Physical clone logic for V1: Characters
        new_source_id = str(uuid.uuid4())
        if parent.asset_type == AssetType.CHARACTER:
            char = self.char_repo.get(parent.source_id)
            if char:
                char.id = new_source_id
                char.name = f"{char.name} (Fork)"
                self.char_repo.save(char)
        # For worlds/templates etc., similar logic would apply.
        
        # Create Marketplace record
        parent.forks += 1
        
        new_asset_id = str(uuid.uuid4())
        lineage = AssetLineage(
            root_asset_id=parent.lineage.root_asset_id if parent.lineage else parent.asset_id,
            parent_asset_id=parent.asset_id,
            depth=(parent.lineage.depth + 1) if parent.lineage else 1
        )
        
        forked = MarketplaceAsset(
            asset_id=new_asset_id,
            asset_type=parent.asset_type,
            source_id=new_source_id,
            title=f"{parent.title} (Fork)",
            description=f"Fork of {parent.title}",
            author_id=new_author_id,
            tags=parent.tags,
            versions=[AssetVersion(version=1, summary="Forked", timestamp=now)],
            lineage=lineage,
            compatible_worlds=parent.compatible_worlds,
            compatible_formations=parent.compatible_formations,
            compatible_goals=parent.compatible_goals,
            required_assets=parent.required_assets,
            health_score=parent.health_score,
            created_at=now,
            updated_at=now
        )
        assets.append(forked)
        self._save_assets(assets)
        return forked

    def rate_asset(self, asset_id: str, user_id: str, score: int) -> Optional[MarketplaceAsset]:
        if score < 1 or score > 5:
            return None
            
        ratings = self._load_ratings()
        
        # Check if already rated by this user
        existing_idx = next((i for i, r in enumerate(ratings) if r.asset_id == asset_id and r.user_id == user_id), None)
        if existing_idx is not None:
            ratings[existing_idx].score = score
            ratings[existing_idx].timestamp = datetime.datetime.now().isoformat()
        else:
            ratings.append(AssetRating(
                asset_id=asset_id,
                user_id=user_id,
                score=score,
                timestamp=datetime.datetime.now().isoformat()
            ))
            
        self._save_ratings(ratings)
        
        # Recalculate
        asset_ratings = [r.score for r in ratings if r.asset_id == asset_id]
        total_score = sum(asset_ratings)
        count = len(asset_ratings)
        
        assets = self._load_assets()
        for a in assets:
            if a.asset_id == asset_id:
                a.rating_count = count
                a.rating = round(total_score / count, 2) if count > 0 else 0.0
                self._save_assets(assets)
                return a
        return None
