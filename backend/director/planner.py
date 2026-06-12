"""Director Planner maps raw Compiler outputs into semantic Staged Beats."""

from backend.compiler.schemas import StoryBeatDraft
from .staging_schemas import (
    StagedBeat, BlockingDirective, SceneComposition,
    FormationCategory, RelationshipType, AnchorIntent, SpatialRole
)

class DirectorPlanner:
    def plan_beat(self, beat: StoryBeatDraft) -> StagedBeat:
        """Translates a semantic intent beat into a staged beat with blocking directives."""
        staged = StagedBeat(
            **beat.model_dump(),
            focus_actor=beat.actor,
            secondary_actor=beat.target,
            blocking=[],
            planner_reasoning=[]
        )
        
        # Rule-based generation for MVP
        if "sell_product" in beat.intent:
            staged.dramatic_weight = 0.5
            staged.planner_confidence = 0.95
            staged.planner_reasoning.append(f"Detected sell_product intent.")
            
            staged.composition = SceneComposition(
                focus_actor=beat.actor,
                secondary_actor=beat.target,
                formation=FormationCategory.SELLING,
                emotional_tone="persuasive"
            )
            
            staged.blocking.append(BlockingDirective(
                actor_id=beat.actor,
                spatial_role=SpatialRole.SELLER,
                anchor_intent=AnchorIntent.NEAREST_SELLING_ZONE,
                formation=FormationCategory.SELLING,
                relationship=RelationshipType.CONVERSATION
            ))
            staged.planner_reasoning.append(f"Assigned {beat.actor} (SELLER) to NEAREST_SELLING_ZONE.")
            
            if beat.target:
                staged.blocking.append(BlockingDirective(
                    actor_id=beat.target,
                    spatial_role=SpatialRole.CUSTOMER,
                    anchor_intent=AnchorIntent.TARGET_FRONT,
                    formation=FormationCategory.SELLING,
                    relationship=RelationshipType.CONVERSATION
                ))
                staged.planner_reasoning.append(f"Assigned {beat.target} (CUSTOMER) to TARGET_FRONT.")

        elif "argue" in beat.intent:
            staged.dramatic_weight = 1.0
            staged.planner_confidence = 0.90
            staged.planner_reasoning.append(f"Detected argue intent.")
            
            staged.composition = SceneComposition(
                focus_actor=beat.actor,
                secondary_actor=beat.target,
                formation=FormationCategory.ARGUMENT_2P,
                emotional_tone="hostile"
            )
            
            staged.blocking.append(BlockingDirective(
                actor_id=beat.actor,
                spatial_role=SpatialRole.FOCUS,
                anchor_intent=AnchorIntent.SCENE_CENTER,
                formation=FormationCategory.ARGUMENT_2P,
                relationship=RelationshipType.CONFRONTATION
            ))
            staged.planner_reasoning.append(f"Assigned {beat.actor} (FOCUS) to SCENE_CENTER.")
            
            if beat.target:
                staged.blocking.append(BlockingDirective(
                    actor_id=beat.target,
                    spatial_role=SpatialRole.TARGET,
                    anchor_intent=AnchorIntent.TARGET_FRONT,
                    formation=FormationCategory.ARGUMENT_2P,
                    relationship=RelationshipType.CONFRONTATION
                ))
                staged.planner_reasoning.append(f"Assigned {beat.target} (TARGET) to TARGET_FRONT with CONFRONTATION relationship.")

        elif "question" in beat.intent:
            staged.dramatic_weight = 0.7
            staged.planner_confidence = 0.85
            staged.planner_reasoning.append(f"Detected question intent.")
            
            staged.composition = SceneComposition(
                focus_actor=beat.actor,
                secondary_actor=beat.target,
                formation=FormationCategory.INTERROGATION,
                emotional_tone="suspicious"
            )
            
            staged.blocking.append(BlockingDirective(
                actor_id=beat.actor,
                spatial_role=SpatialRole.FOCUS,
                anchor_intent=AnchorIntent.NEAREST_INTERROGATION_ZONE,
                formation=FormationCategory.INTERROGATION,
                relationship=RelationshipType.INTERROGATION
            ))
            staged.planner_reasoning.append(f"Assigned {beat.actor} (FOCUS) to NEAREST_INTERROGATION_ZONE.")
            
            if beat.target:
                staged.blocking.append(BlockingDirective(
                    actor_id=beat.target,
                    spatial_role=SpatialRole.TARGET,
                    anchor_intent=AnchorIntent.TARGET_FRONT,
                    formation=FormationCategory.INTERROGATION,
                    relationship=RelationshipType.INTERROGATION
                ))
                staged.planner_reasoning.append(f"Assigned {beat.target} (TARGET) to TARGET_FRONT with INTERROGATION relationship.")
        else:
            # Fallback
            staged.dramatic_weight = 0.3
            staged.planner_confidence = 0.5
            staged.planner_reasoning.append(f"Unknown intent {beat.intent}, applying fallback staging.")
            
            staged.composition = SceneComposition(
                focus_actor=beat.actor,
                secondary_actor=beat.target,
                formation=FormationCategory.DIALOGUE_2P
            )
            
            staged.blocking.append(BlockingDirective(
                actor_id=beat.actor,
                spatial_role=SpatialRole.FOCUS,
                anchor_intent=AnchorIntent.SCENE_CENTER,
                formation=FormationCategory.DIALOGUE_2P,
                relationship=RelationshipType.CONVERSATION
            ))

        return staged
