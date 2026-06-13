"""Collaboration Repository for managing comments, roles, and mock users."""

import os
import json
import uuid
import datetime
from typing import List, Optional
from backend.models.collaboration import ProjectComment, MockUser, ProjectRole, RevisionApproval, ApprovalStatus
from backend.models.project import ProjectManifest

MOCK_USERS = [
    MockUser(user_id="owner_1", name="Sarah (Owner)", role=ProjectRole.OWNER),
    MockUser(user_id="editor_1", name="David (Editor)", role=ProjectRole.EDITOR),
    MockUser(user_id="reviewer_1", name="Elena (Reviewer)", role=ProjectRole.REVIEWER),
    MockUser(user_id="viewer_1", name="Mike (Viewer)", role=ProjectRole.VIEWER)
]

class CollaborationRepository:
    def __init__(self, data_dir: str = "data/projects"):
        self.data_dir = data_dir
        
    def _get_comments_path(self, project_id: str) -> str:
        return os.path.join(self.data_dir, project_id, "comments.json")
        
    def get_mock_users(self) -> List[MockUser]:
        return MOCK_USERS

    def get_user_role(self, user_id: str) -> Optional[ProjectRole]:
        for u in MOCK_USERS:
            if u.user_id == user_id:
                return u.role
        return None

    def get_comments(self, project_id: str) -> List[ProjectComment]:
        path = self._get_comments_path(project_id)
        if not os.path.exists(path):
            return []
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                return [ProjectComment(**x) for x in data]
        except Exception:
            return []

    def save_comments(self, project_id: str, comments: List[ProjectComment]):
        path = self._get_comments_path(project_id)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump([c.model_dump() for c in comments], f, indent=2)

    def add_comment(self, project_id: str, comment: ProjectComment):
        comments = self.get_comments(project_id)
        comments.append(comment)
        self.save_comments(project_id, comments)

    def resolve_comment(self, project_id: str, comment_id: str, resolved_by: str) -> bool:
        comments = self.get_comments(project_id)
        for c in comments:
            if c.comment_id == comment_id:
                c.resolved = True
                c.resolved_by = resolved_by
                self.save_comments(project_id, comments)
                return True
        return False

    def can_approve(self, user_id: str) -> bool:
        role = self.get_user_role(user_id)
        return role in [ProjectRole.OWNER, ProjectRole.REVIEWER]

    def process_approval(self, manifest: ProjectManifest, revision_id: str, user_id: str) -> bool:
        if not self.can_approve(user_id):
            return False
            
        # Find or create approval state for revision
        target_app = None
        for app_dict in manifest.approvals:
            if app_dict.get("revision_id") == revision_id:
                target_app = RevisionApproval(**app_dict)
                break
                
        if not target_app:
            target_app = RevisionApproval(revision_id=revision_id, required_approvals=1, approved_by=[], status=ApprovalStatus.NOT_REVIEWED)
            
        if user_id not in target_app.approved_by:
            target_app.approved_by.append(user_id)
            
        if len(target_app.approved_by) >= target_app.required_approvals:
            target_app.status = ApprovalStatus.APPROVED
        elif len(target_app.approved_by) > 0:
            target_app.status = ApprovalStatus.REVIEWED
            
        # Update manifest
        filtered = [a for a in manifest.approvals if a.get("revision_id") != revision_id]
        filtered.append(target_app.model_dump())
        manifest.approvals = filtered
        return True
