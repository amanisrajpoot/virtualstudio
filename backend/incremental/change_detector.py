"""Change Detector for computing Semantic Fingerprints."""

import hashlib
import json
from typing import List, Optional
from backend.models.story_graph import GraphOverride

class ChangeDetector:
    
    @staticmethod
    def compute_node_hash(
        intent: str,
        dialogue: Optional[str],
        characters: List[str],
        world_id: str,
        override: Optional[GraphOverride] = None
    ) -> str:
        """
        Computes a deterministic hash of the inputs for a single node.
        Includes override patches to invalidate downstream when intents are manually changed.
        """
        payload = {
            "intent": intent,
            "dialogue": dialogue or "",
            "characters": sorted(characters),
            "world": world_id,
            "override": override.overridden_intent if override else None
        }
        
        serialized = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        
    @staticmethod
    def compute_dependency_hash(upstream_fingerprints: List[str]) -> str:
        """
        Computes a hash of all upstream dependencies.
        """
        if not upstream_fingerprints:
            return hashlib.sha256(b"root").hexdigest()
            
        serialized = json.dumps(sorted(upstream_fingerprints))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        
    @staticmethod
    def compute_fingerprint(node_hash: str, dependency_hash: str) -> str:
        """
        Computes the final compilation fingerprint (L1 Cache Key).
        """
        return hashlib.sha256(f"{node_hash}:{dependency_hash}".encode("utf-8")).hexdigest()
