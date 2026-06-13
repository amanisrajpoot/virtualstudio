"""Semantic Build System Orchestrator."""

import datetime
from typing import List, Dict, Optional
from backend.models.story_graph import StoryGraph, BeatNode, NodeStatus, GraphOverride
from backend.models.incremental import CompilationUnit, DirtyReason, SemanticCacheEntry, CacheMetadata, CompilationSnapshot
from backend.incremental.change_detector import ChangeDetector
from backend.incremental.dependency_tracker import DependencyTracker
from backend.incremental.cache import SemanticCache
from backend.repositories.graph_overrides import GraphOverrideRepository
from backend.preview.builder import PreviewBuilder
from backend.observability.tracker import telemetry

class SemanticCompiler:
    def __init__(self, preview_builder: PreviewBuilder, cache: SemanticCache, overrides_repo: GraphOverrideRepository):
        self.preview_builder = preview_builder
        self.cache = cache
        self.overrides_repo = overrides_repo

    def compile(self, story_id: str, text: str, world_id: str, characters: List[str]) -> StoryGraph:
        """
        Executes an incremental compilation pass.
        1. Computes hashes.
        2. Checks L1 Cache to flag DIRTY nodes.
        3. Propagates DIRTY status downstream.
        4. Rebuilds only DIRTY nodes using PreviewBuilder.
        5. Assembles final StoryGraph and Checkpoint.
        """
        telemetry.track_event("COMPILATION_STARTED", {"story_id": story_id})
        
        overrides = self.overrides_repo.get_overrides(story_id)
        override_map = {o.node_id: o for o in overrides}
        
        # Simplified parser for V1: split text by '.' for beats
        raw_beats = [b.strip() for b in text.split('.') if b.strip()]
        if not raw_beats:
            return StoryGraph(story_id=story_id, version=1, graph_health=100, nodes=[])

        compilation_units: Dict[str, CompilationUnit] = {}
        dirty_map: Dict[str, DirtyReason] = {}
        
        # Pass 1: Compute Node Hashes & Check Initial Cache Hits
        upstream_fingerprints = []
        for i, beat_text in enumerate(raw_beats):
            node_id = f"beat_{i+1}"
            override = override_map.get(node_id)
            
            node_hash = ChangeDetector.compute_node_hash(
                intent="", # We don't know intent before compile, we use text content proxy
                dialogue=beat_text, 
                characters=characters,
                world_id=world_id,
                override=override
            )
            
            dependency_hash = ChangeDetector.compute_dependency_hash(upstream_fingerprints)
            fingerprint = ChangeDetector.compute_fingerprint(node_hash, dependency_hash)
            upstream_fingerprints.append(fingerprint)
            
            cached_entry = self.cache.get_l1_entry(fingerprint)
            
            if cached_entry is None:
                # Content changed or never compiled
                dirty_map[node_id] = DirtyReason.CONTENT_CHANGED
                if override and cached_entry is None:
                     dirty_map[node_id] = DirtyReason.OVERRIDE_CHANGED
                     
            unit = CompilationUnit(
                node_id=node_id,
                node_hash=node_hash,
                dependency_hash=dependency_hash,
                fingerprint=fingerprint,
                dirty=node_id in dirty_map,
                dirty_reason=dirty_map.get(node_id),
                last_compiled_at=datetime.datetime.now().isoformat()
            )
            compilation_units[node_id] = unit

        # Pass 2: Propagate Dependencies (Sequential V1)
        edges = {}
        for i in range(len(raw_beats) - 1):
            edges[f"beat_{i+1}"] = [f"beat_{i+2}"]
            
        for node_id in list(dirty_map.keys()):
             DependencyTracker.propagate_dirty_state(node_id, dirty_map[node_id], edges, dirty_map)

        for node_id in dirty_map:
             if node_id in compilation_units:
                  compilation_units[node_id].dirty = True
                  compilation_units[node_id].dirty_reason = dirty_map[node_id]

        # Pass 3: Rebuild Dirty Nodes
        final_nodes = []
        nodes_recompiled = 0
        nodes_reused = 0
        invalidation_causes = {}
        graph_health = 100

        for i, beat_text in enumerate(raw_beats):
            node_id = f"beat_{i+1}"
            unit = compilation_units[node_id]
            override = override_map.get(node_id)
            
            if not unit.dirty:
                # CACHE HIT
                telemetry.track_event("CACHE_HIT", {"node_id": node_id})
                cached_entry = self.cache.get_l1_entry(unit.fingerprint)
                node = BeatNode(**cached_entry.graph_node_data)
                final_nodes.append(node)
                nodes_reused += 1
                if node.confidence < 80:
                    graph_health -= 15
            else:
                # CACHE MISS / DIRTY
                telemetry.track_event("CACHE_MISS", {"node_id": node_id, "reason": unit.dirty_reason})
                nodes_recompiled += 1
                cause = unit.dirty_reason.value if unit.dirty_reason else "unknown"
                invalidation_causes[cause] = invalidation_causes.get(cause, 0) + 1
                
                # Mock Heavy Compilation
                intent_val = override.overridden_intent if override else ("ARGUE" if "argue" in beat_text.lower() else "ACTION")
                status_val = NodeStatus.OVERRIDDEN if override else NodeStatus.GENERATED
                confidence = 90.0 if "argue" in beat_text.lower() else 100.0
                
                if override:
                     # Penalize confidence if intent doesn't match raw text
                     confidence = 70.0
                
                if confidence < 80:
                     graph_health -= 15
                     
                node = BeatNode(
                    id=node_id,
                    intent=intent_val,
                    beat_type="dialogue" if "said" in beat_text.lower() else "action",
                    dialogue=beat_text,
                    formation="face_to_face",
                    zone="default",
                    confidence=confidence,
                    status=status_val,
                    next_nodes=[f"beat_{i+2}"] if i < len(raw_beats)-1 else []
                )
                
                # Mark as explicitly dirty during the build pass so UI can render it orange temporarily
                # But actually, the final graph should not leave it DIRTY unless we want it to stay orange.
                # In StoryForge, we want the UI to flash orange then settle on GENERATED/OVERRIDDEN.
                # We'll leave it as GENERATED/OVERRIDDEN in the final struct, but the event tracks it.
                telemetry.track_event("NODE_RECOMPILED", {"node_id": node_id})
                
                # Save to Cache
                new_entry = SemanticCacheEntry(
                    fingerprint=unit.fingerprint,
                    graph_node_data=node.model_dump(),
                    metadata=CacheMetadata(
                        created_at=datetime.datetime.now().isoformat(),
                        last_accessed=datetime.datetime.now().isoformat(),
                        hit_count=0
                    )
                )
                self.cache.save_l1_entry(new_entry)
                # Mock L2 Cache Save
                self.cache.save_l2_preview(node_id, {"snapshot": "preview_data_mock"})
                
                final_nodes.append(node)

        # Build Graph
        version = len(overrides) + 1
        graph_health = max(0, graph_health)
        
        graph = StoryGraph(
            story_id=story_id,
            version=version,
            graph_health=graph_health,
            nodes=final_nodes
        )
        
        # Save Checkpoint
        snapshot = CompilationSnapshot(
            story_id=story_id,
            graph_version=version,
            compiled_nodes=[n.id for n in final_nodes],
            health_score=graph_health,
            timestamp=datetime.datetime.now().isoformat()
        )
        self.cache.save_checkpoint(snapshot)
        
        # Log Savings
        total = nodes_recompiled + nodes_reused
        savings_pct = (nodes_reused / total * 100) if total > 0 else 0
        telemetry.track_event("COMPILATION_COMPLETED", {
            "story_id": story_id,
            "nodes_recompiled": nodes_recompiled,
            "nodes_reused": nodes_reused,
            "cache_hit_rate": savings_pct,
            "top_invalidation_cause": max(invalidation_causes, key=invalidation_causes.get) if invalidation_causes else "none"
        })

        return graph
