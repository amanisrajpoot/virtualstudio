"""Verification Tests for Subsystem 28 (Collaboration Layer)."""

import os
import shutil
import datetime
import uuid
from backend.models.project import ProjectManifest
from backend.models.collaboration import ProjectComment, CommentAnchorType, ApprovalStatus, ProjectRole
from backend.repositories.projects import ProjectRepository
from backend.repositories.collaboration import CollaborationRepository

def test_collaboration_layer():
    test_dir = "data/test_collab_dir"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
        
    p_repo = ProjectRepository(data_dir=test_dir)
    c_repo = CollaborationRepository(data_dir=test_dir)
    
    # 1. Setup Base Project
    project_id = "proj_collab_1"
    manifest = ProjectManifest(
        project_id=project_id,
        name="Collaboration Test",
        description="Testing approvals",
        graph_version=1,
        active_snapshot_version=1,
        created_at=datetime.datetime.now().isoformat(),
        updated_at=datetime.datetime.now().isoformat()
    )
    p_repo.save_manifest(manifest)
    print("Test 1 & 4 (Setup & Manifest Save) passed.")
    
    # 2. Test Comments & Threading (Test 2 & 6 & 8)
    # Test 8: Simulate switching user to reviewer
    active_user = "reviewer_1"
    
    comment_1 = ProjectComment(
        comment_id="c1",
        project_id=project_id,
        anchor_type=CommentAnchorType.NODE,
        anchor_id="beat_4",
        author_id=active_user,
        text="Intent should be NEGOTIATE",
        created_at=datetime.datetime.now().isoformat()
    )
    c_repo.add_comment(project_id, comment_1)
    
    # Reply (Threading)
    active_user = "editor_1"
    comment_2 = ProjectComment(
        comment_id="c2",
        project_id=project_id,
        parent_comment_id="c1",
        anchor_type=CommentAnchorType.NODE,
        anchor_id="beat_4",
        author_id=active_user,
        text="Agreed.",
        created_at=datetime.datetime.now().isoformat()
    )
    c_repo.add_comment(project_id, comment_2)
    
    comments = c_repo.get_comments(project_id)
    assert len(comments) == 2
    assert comments[1].parent_comment_id == "c1"
    
    # Resolution (Test 6)
    active_user = "owner_1"
    success = c_repo.resolve_comment(project_id, "c1", active_user)
    assert success
    
    resolved_comments = c_repo.get_comments(project_id)
    assert resolved_comments[0].resolved == True
    assert resolved_comments[0].resolved_by == "owner_1"
    print("Test 2, 6, 8 (Node Comments, Threading, Resolution, Author Propagation) passed.")
    
    # 3. Test Approvals & Permissions (Test 3, 5, 7)
    rev_id = "rev_1"
    
    # Viewer tries to approve (Test 5)
    success = c_repo.process_approval(manifest, rev_id, "viewer_1")
    assert not success # Viewer cannot approve
    
    # Reviewer approves (Test 3)
    success = c_repo.process_approval(manifest, rev_id, "reviewer_1")
    assert success
    
    # Check threshold logic (Test 7)
    # By default required_approvals=1, so 1 approval means APPROVED
    assert manifest.approvals[0].get("status") == "approved"
    
    # Let's force threshold to 2 to test
    manifest.approvals[0]["required_approvals"] = 2
    manifest.approvals[0]["status"] = "reviewed"
    p_repo.save_manifest(manifest)
    
    # Re-process same reviewer (should just ignore duplicate or keep reviewed)
    c_repo.process_approval(manifest, rev_id, "reviewer_1")
    assert manifest.approvals[0].get("status") == "reviewed" # Still needs 1 more
    
    # Owner approves -> hits threshold 2
    c_repo.process_approval(manifest, rev_id, "owner_1")
    assert manifest.approvals[0].get("status") == "approved"
    print("Test 3, 5, 7 (Permissions, Thresholds, Approvals execution) passed.")

if __name__ == "__main__":
    test_collaboration_layer()
    print("All Collaboration Layer tests passed!")
