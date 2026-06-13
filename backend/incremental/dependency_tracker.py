"""Dependency Tracker for Graph Invalidations."""

from typing import Dict, List, Set
from backend.models.incremental import DirtyReason

class DependencyTracker:
    
    @staticmethod
    def propagate_dirty_state(
        node_id: str, 
        dirty_reason: DirtyReason, 
        edges: Dict[str, List[str]], 
        dirty_map: Dict[str, DirtyReason]
    ):
        """
        Recursively marks downstream nodes as dirty.
        """
        # Base case
        if node_id not in dirty_map:
            dirty_map[node_id] = dirty_reason
            
        # Recursive downstream invalidation
        downstream_nodes = edges.get(node_id, [])
        for child_id in downstream_nodes:
            # If downstream is not already dirty, mark it as UPSTREAM_CHANGED
            if child_id not in dirty_map:
                DependencyTracker.propagate_dirty_state(
                    child_id,
                    DirtyReason.UPSTREAM_CHANGED,
                    edges,
                    dirty_map
                )

    @staticmethod
    def get_upstream_fingerprints(
        node_id: str,
        reverse_edges: Dict[str, List[str]],
        fingerprint_map: Dict[str, str]
    ) -> List[str]:
        """
        Retrieves the fingerprints of all immediate upstream parents.
        """
        parents = reverse_edges.get(node_id, [])
        return [fingerprint_map[p] for p in parents if p in fingerprint_map]
