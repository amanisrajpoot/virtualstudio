"""Dependency Builder."""

from typing import List, Set, Tuple
from .schemas import AssetManifest, DependencyEdge
from .bundles import is_bundle, get_bundle_assets
from .registry_hooks import get_asset_dependencies

class DependencyBuilder:
    def __init__(self):
        # In a real app, this might track previously built manifests for the "warm_start" feature
        self.known_loaded_assets: Set[str] = set()

    def build_manifest(self, story_id: str, requested_items: List[str]) -> AssetManifest:
        """
        Takes a list of required items (can be raw assets or bundles).
        Unpacks bundles, recursively resolves dependencies, builds the graph,
        and generates an immutable AssetManifest.
        """
        required_assets = set()
        graph_edges: List[DependencyEdge] = []
        visited = set()
        warm_starts = []

        def resolve(item_id: str, parent_id: str = None):
            if item_id in visited and parent_id:
                # Add edge even if visited to complete graph, but don't recurse
                graph_edges.append(DependencyEdge(parent_id=parent_id, child_id=item_id))
                return
                
            visited.add(item_id)
            
            if parent_id:
                graph_edges.append(DependencyEdge(parent_id=parent_id, child_id=item_id))

            # If it's a bundle, unpack it
            if is_bundle(item_id):
                for child_asset in get_bundle_assets(item_id):
                    resolve(child_asset, item_id)
            else:
                # It's an asset
                required_assets.add(item_id)
                # Check warm start
                if item_id in self.known_loaded_assets:
                    warm_starts.append(item_id)
                
                # Recurse dependencies
                deps = get_asset_dependencies(item_id)
                for dep in deps:
                    resolve(dep, item_id)

        # Start resolution
        for item in requested_items:
            resolve(item)
            
        # Update our known loaded assets (mocking the fact that building a manifest means they will be loaded soon)
        self.known_loaded_assets.update(required_assets)

        return AssetManifest(
            story_id=story_id,
            required_assets=list(required_assets),
            dependency_graph=graph_edges,
            warm_starts=warm_starts
        )
