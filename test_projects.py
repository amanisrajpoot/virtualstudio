"""Verification Tests for Subsystem 27 (Project Packaging & Runtime)."""

import os
import shutil
import datetime
from backend.models.project import ProjectManifest, ProjectSnapshot, ProjectRevision
from backend.repositories.projects import ProjectRepository

def test_project_runtime():
    test_dir = "data/test_projects_dir"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
        
    repo = ProjectRepository(data_dir=test_dir)
    
    # 1. Test Manifest Creation
    manifest = ProjectManifest(
        project_id="proj_001",
        name="Village Comedy",
        description="A hilarious interaction at the market.",
        story_ids=["story_1"],
        character_ids=["halku", "policeman"],
        world_ids=["market"],
        active_story_id="story_1",
        graph_version=1,
        created_at=datetime.datetime.now().isoformat(),
        updated_at=datetime.datetime.now().isoformat()
    )
    repo.save_manifest(manifest)
    
    loaded = repo.get_manifest("proj_001")
    assert loaded is not None
    assert loaded.name == "Village Comedy"
    print("Test 1 (Project Creation & Manifest Persistence) passed.")
    
    # 2. Test Snapshot Commit & Revision History
    loaded.graph_version += 1
    loaded.active_snapshot_version = loaded.graph_version
    rev = ProjectRevision(
        revision_id=f"rev_{loaded.graph_version}",
        graph_version=loaded.graph_version,
        summary="Added Policeman chase sequence",
        timestamp=datetime.datetime.now().isoformat()
    )
    loaded.revisions.append(rev)
    
    snapshot = ProjectSnapshot(
        project_id=loaded.project_id,
        graph_version=loaded.graph_version,
        semantic_graph={"nodes": []},
        overrides=[],
        preview_state={}
    )
    
    repo.save_snapshot(snapshot)
    repo.save_manifest(loaded)
    
    snap_loaded = repo.get_snapshot("proj_001", 2)
    assert snap_loaded is not None
    assert snap_loaded.graph_version == 2
    print("Test 2 (Snapshot Commits & Execution State saved) passed.")
    
    manifest_v2 = repo.get_manifest("proj_001")
    assert len(manifest_v2.revisions) == 1
    assert manifest_v2.revisions[0].summary == "Added Policeman chase sequence"
    assert manifest_v2.active_snapshot_version == 2
    print("Test 3 (Semantic History Logging & Active Pointer) passed.")
    
    # 4. Test Listing
    manifests = repo.list_manifests()
    assert len(manifests) == 1
    assert manifests[0].project_id == "proj_001"
    print("Test 4 (Project Retrieval & Listing) passed.")

if __name__ == "__main__":
    test_project_runtime()
    print("All Project Runtime tests passed!")
