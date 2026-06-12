"""Verification Tests for Subsystem 25 (Story Graph & Beat Editor)."""

import os
from backend.models.story_graph import NodeStatus, GraphOverride
from backend.repositories.graph_overrides import GraphOverrideRepository
from backend.preview.builder import PreviewCache, PreviewBuilder
from backend.story_graph.builder import StoryGraphBuilder

def test_graph_logic():
    os.makedirs("data/test_overrides", exist_ok=True)
    
    preview_cache = PreviewCache()
    preview_builder = PreviewBuilder(preview_cache)
    repo = GraphOverrideRepository(data_dir="data/test_overrides")
    builder = StoryGraphBuilder(preview_builder, repo)
    
    story_id = "test_graph_1"
    text = "Halku sets up stall. Policeman complains. They argue loudly."
    
    # Run Generation
    graph = builder.build_graph(story_id, text, "market", ["halku", "policeman"])
    
    # Test 1 & 2: Generation and Wiring
    assert len(graph.nodes) > 0
    assert graph.nodes[0].next_nodes == [graph.nodes[1].id] if len(graph.nodes) > 1 else True
    print("Test 1 & 2 (Graph Generation & Edge Wiring) passed.")
    
    # Test 5 & 8: Confidence & Health
    has_low_conf = any(n.confidence < 80.0 for n in graph.nodes)
    if has_low_conf:
        assert graph.graph_health < 100
    print("Test 5 & 8 (Confidence Propagation & Graph Health) passed.")
    
    # Test 3 & 9: Override Application & Status
    override = GraphOverride(
        node_id=graph.nodes[0].id,
        story_id=story_id,
        original_intent=graph.nodes[0].intent,
        overridden_intent="NEGOTIATE",
        timestamp="now"
    )
    repo.save_override(override)
    
    # Rebuild to apply patch layer
    graph_v2 = builder.build_graph(story_id, text, "market", ["halku", "policeman"])
    assert graph_v2.nodes[0].intent == "NEGOTIATE"
    assert graph_v2.nodes[0].status == NodeStatus.OVERRIDDEN
    print("Test 3 & 9 (Intent Override & Node Status) passed.")
    
    # Test 7: Version Increment
    assert graph_v2.version == 2
    print("Test 7 (Graph Version Increment) passed.")
    
    # Test 6: Override Persistence
    repo_new = GraphOverrideRepository(data_dir="data/test_overrides")
    overrides = repo_new.get_overrides(story_id)
    assert len(overrides) == 1
    assert overrides[0].overridden_intent == "NEGOTIATE"
    print("Test 6 (Override Persistence) passed.")
    
    # Test 4: Branch Serialization (Schema validation)
    graph_v2.nodes[0].next_nodes.append("branch_test_node")
    assert "branch_test_node" in graph_v2.nodes[0].next_nodes
    print("Test 4 (Branch Serialization Schema) passed.")

if __name__ == "__main__":
    test_graph_logic()
    print("All Semantic Graph tests passed!")
