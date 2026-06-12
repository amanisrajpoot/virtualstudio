"""Schemas for the Director Planner and Scene Resolver."""

from enum import Enum
from pydantic import BaseModel, Field
from backend.compiler.schemas import StoryBeatDraft

class AnchorIntent(str, Enum):
    NEAREST_SELLING_ZONE = "nearest_selling_zone"
    NEAREST_REST_ZONE = "nearest_rest_zone"
    NEAREST_CONVERSATION_ZONE = "nearest_conversation_zone"
    NEAREST_INTERROGATION_ZONE = "nearest_interrogation_zone"
    NEAREST_GROUP_ZONE = "nearest_group_zone"
    SCENE_CENTER = "scene_center"
    SCENE_ENTRY = "scene_entry"
    SCENE_EXIT = "scene_exit"
    TARGET_FRONT = "target_front"
    TARGET_FLANK = "target_flank"

class SpatialRole(str, Enum):
    FOCUS = "focus"
    CUSTOMER = "customer"
    SELLER = "seller"
    PURSUER = "pursuer"
    TARGET = "target"
    OBSERVER = "observer"
    CROWD = "crowd"

class FormationCategory(str, Enum):
    DIALOGUE_2P = "dialogue_2p"
    ARGUMENT_2P = "argument_2p"
    SELLING = "selling"
    INTERROGATION = "interrogation"
    CHASE = "chase"

class RelationshipType(str, Enum):
    CONVERSATION = "conversation"
    CONFRONTATION = "confrontation"
    INTERROGATION = "interrogation"
    CHASE = "chase"

class BlockingDirective(BaseModel):
    actor_id: str
    spatial_role: SpatialRole | None = None
    anchor_intent: AnchorIntent | None = None
    formation: FormationCategory | None = None
    relationship: RelationshipType | None = None

class ResolvedBlockingDirective(BlockingDirective):
    resolved_anchor: str | None = None

class SceneComposition(BaseModel):
    focus_actor: str
    secondary_actor: str | None = None
    formation: FormationCategory | None = None
    dominant_zone: str | None = None
    emotional_tone: str | None = None

class StagedBeat(StoryBeatDraft):
    dramatic_weight: float = Field(0.5, ge=0.0, le=1.0)
    composition: SceneComposition | None = None
    blocking: list[BlockingDirective] = Field(default_factory=list)
    resolved_blocking: list[ResolvedBlockingDirective] = Field(default_factory=list)
    planner_reasoning: list[str] = Field(default_factory=list)
    planner_confidence: float = Field(0.0, ge=0.0, le=1.0)

class Placement(BaseModel):
    actor_id: str
    spatial_role: SpatialRole
    anchor_id: str
    occupancy_slot: int
    facing_target: str | None = None
    placement_confidence: float = 1.0

class SolvedBeat(StagedBeat):
    placements: list[Placement] = Field(default_factory=list)
