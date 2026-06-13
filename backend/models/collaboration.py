"""Collaboration Layer Schemas."""

from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class ProjectRole(str, Enum):
    OWNER = "owner"
    EDITOR = "editor"
    REVIEWER = "reviewer"
    VIEWER = "viewer"

class MockUser(BaseModel):
    user_id: str
    name: str
    role: ProjectRole

class ProjectMember(BaseModel):
    user_id: str
    role: ProjectRole
    joined_at: str

class CommentAnchorType(str, Enum):
    NODE = "node"
    DIALOGUE = "dialogue"
    FORMATION = "formation"
    ZONE = "zone"

class ProjectComment(BaseModel):
    comment_id: str
    project_id: str
    parent_comment_id: Optional[str] = None
    anchor_type: CommentAnchorType
    anchor_id: str
    author_id: str
    text: str
    resolved: bool = False
    resolved_by: Optional[str] = None
    created_at: str

class ApprovalStatus(str, Enum):
    NOT_REVIEWED = "not_reviewed"
    REVIEWED = "reviewed"
    APPROVED = "approved"

class RevisionApproval(BaseModel):
    revision_id: str
    required_approvals: int = 1
    approved_by: List[str] = [] # user_ids
    status: ApprovalStatus = ApprovalStatus.NOT_REVIEWED
