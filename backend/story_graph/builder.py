"""Story Graph Builder."""

from typing import List, Optional
from backend.models.story_graph import StoryGraph, BeatNode, NodeStatus, GraphOverride
from backend.repositories.graph_overrides import GraphOverrideRepository
from backend.preview.builder import PreviewBuilder

class StoryGraphBuilder:
    def __init__(self, preview_builder: PreviewBuilder, overrides_repo: GraphOverrideRepository):
        self.preview_builder = preview_builder
        self.overrides_repo = overrides_repo

    def build_graph(self, story_id: str, text: str, world_id: str, characters: List[str]) -> StoryGraph:
        # 1. Generate base preview beats
        preview_package = self.preview_builder.build(story_id, text, world_id, characters)
        
        # 2. Fetch patch layer
        overrides = self.overrides_repo.get_overrides(story_id)
        override_map = {o.node_id: o for o in overrides}
        
        # 3. Construct Semantic Nodes
        nodes = []
        graph_health = 100
        
        for i, beat in enumerate(preview_package.beats):
            # Base logic
            confidence = 90.0 if "argue" in beat.intent.lower() else 100.0 # Mock confidence variance
            
            node = BeatNode(
                id=beat.id,
                intent=beat.intent,
                beat_type="dialogue" if beat.dialogue else "action",
                dialogue=beat.dialogue,
                formation=beat.formation_id,
                zone=beat.state_snapshot.active_zone,
                confidence=confidence,
                status=NodeStatus.GENERATED,
                next_nodes=[]
            )
            
            # Penalize health for low confidence
            if node.confidence < 80.0:
                graph_health -= 15
                
            # Wire edges (sequential V1)
            if i < len(preview_package.beats) - 1:
                node.next_nodes.append(preview_package.beats[i+1].id)
                
            # Apply Override Patch Layer
            if node.id in override_map:
                patch = override_map[node.id]
                node.intent = patch.overridden_intent
                node.status = NodeStatus.OVERRIDDEN
                
            nodes.append(node)
            
        # Ensure health doesn't drop below 0
        graph_health = max(0, graph_health)
        
        version = len(overrides) + 1

        return StoryGraph(
            story_id=story_id,
            version=version,
            graph_health=graph_health,
            nodes=nodes
        )
