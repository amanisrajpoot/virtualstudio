"""Staging Solver assigns collision-free placements based on zone topologies."""

from typing import Dict, Any, List
from .staging_schemas import StagedBeat, SolvedBeat, Placement, SpatialRole
from .scene_resolver import SceneResolutionCache

class AnchorOccupancy:
    def __init__(self, anchor_id: str, capacity: int):
        self.anchor_id = anchor_id
        self.capacity = capacity
        self.occupied_slots = set()
        
    def get_free_slot(self) -> int | None:
        """Returns the first available slot index, or None if full."""
        for i in range(self.capacity):
            if i not in self.occupied_slots:
                return i
        return None
        
    def reserve_slot(self, slot: int):
        self.occupied_slots.add(slot)

class ZoneScore:
    def __init__(self, zone_id: str, score: float):
        self.zone_id = zone_id
        self.score = score

class SolverFailure(Exception):
    pass

class StagingSolver:
    def __init__(self):
        self.cache = SceneResolutionCache()
        
        # Mock Formation Registry
        self.formations = {
            "selling": {
                "seller": {"anchor_strategy": "primary"},
                "customer": {"anchor_strategy": "adjacent", "facing": "seller"}
            },
            "argument_2p": {
                "focus": {"anchor_strategy": "primary"},
                "target": {"anchor_strategy": "opposite", "facing": "focus"}
            },
            "dialogue_2p": {
                "focus": {"anchor_strategy": "primary"},
                "target": {"anchor_strategy": "adjacent", "facing": "focus"}
            }
        }

    def _score_zones(self, zones: List[Dict[str, Any]], required_role: SpatialRole, occupancy_map: Dict[str, AnchorOccupancy]) -> List[ZoneScore]:
        """Scores zones based on priority and remaining capacity."""
        scores = []
        for z in zones:
            occ = occupancy_map.get(z["id"])
            capacity_remaining = occ.capacity - len(occ.occupied_slots) if occ else 0
            
            if capacity_remaining <= 0:
                continue
                
            priority = z.get("priority", 0)
            
            # Simple weighting: 60% priority, 40% capacity
            # In a real engine, distance_from_focus would be calculated here
            normalized_prio = priority / 100.0
            normalized_cap = min(1.0, capacity_remaining / 5.0)
            
            final_score = (normalized_prio * 0.6) + (normalized_cap * 0.4)
            scores.append(ZoneScore(z["id"], final_score))
            
        scores.sort(key=lambda x: x.score, reverse=True)
        return scores

    def solve_beat(self, beat: StagedBeat, scene_id: str) -> SolvedBeat:
        """Takes a Scene-Resolved Beat and calculates precise Placements."""
        
        solved = SolvedBeat(**beat.model_dump(), placements=[])
        
        # Load scene topology
        metadata = self.cache.load_scene_metadata(scene_id)
        zones = metadata.get("interaction_zones", [])
        
        # Initialize occupancy map
        occupancy_map: Dict[str, AnchorOccupancy] = {}
        for z in zones:
            occupancy_map[z["id"]] = AnchorOccupancy(z["id"], z.get("capacity", 1))
            
        # Get Formation template
        formation_id = beat.composition.formation.value if beat.composition and beat.composition.formation else "dialogue_2p"
        formation_template = self.formations.get(formation_id, {})
        
        for blocking in beat.resolved_blocking:
            role_str = blocking.spatial_role.value if blocking.spatial_role else "focus"
            role_rules = formation_template.get(role_str, {})
            
            # 1. Primary Strategy
            target_anchor = blocking.resolved_anchor
            slot = None
            placement_conf = 1.0
            
            if target_anchor and target_anchor.startswith("offset_"):
                # Handle dynamic offsets (like TARGET_FRONT) without strict occupancy for now
                slot = 0
                final_anchor = target_anchor
            else:
                occ = occupancy_map.get(target_anchor)
                if occ:
                    slot = occ.get_free_slot()
                    
                # 2. Adjacent / Fallback Strategy
                if slot is None:
                    # Check adjacent zones first
                    target_zone = next((z for z in zones if z["id"] == target_anchor), None)
                    if target_zone and "adjacent" in target_zone:
                        for adj_id in target_zone["adjacent"]:
                            adj_occ = occupancy_map.get(adj_id)
                            if adj_occ:
                                adj_slot = adj_occ.get_free_slot()
                                if adj_slot is not None:
                                    slot = adj_slot
                                    target_anchor = adj_id
                                    placement_conf = 0.8
                                    beat.planner_reasoning.append(f"Solver: Primary full. Used adjacent anchor '{target_anchor}'.")
                                    occ = adj_occ
                                    break
                                    
                    # 3. Global Fallback Scoring
                    if slot is None:
                        placement_conf = 0.5
                        beat.planner_reasoning.append(f"Solver: Primary/Adjacent full. Scoring fallbacks...")
                        
                        # Score all available zones
                        valid_scores = self._score_zones(zones, blocking.spatial_role, occupancy_map)
                        
                        if not valid_scores:
                            raise SolverFailure(f"No available slots in scene '{scene_id}' to place actor '{blocking.actor_id}'")
                            
                        best_zone_id = valid_scores[0].zone_id
                        occ = occupancy_map[best_zone_id]
                        slot = occ.get_free_slot()
                        target_anchor = best_zone_id
                        beat.planner_reasoning.append(f"Solver: Fallback selected '{target_anchor}' with score {valid_scores[0].score:.2f}")

                occ.reserve_slot(slot)
                final_anchor = target_anchor

            # Resolve Facing
            facing = role_rules.get("facing")
            if facing == "focus" and beat.composition.focus_actor:
                facing = beat.composition.focus_actor
            elif facing == "seller":
                # Find who the seller is (in a real app, scan the beats)
                facing = beat.composition.focus_actor # approximation for MVP
                
            placement = Placement(
                actor_id=blocking.actor_id,
                spatial_role=blocking.spatial_role or SpatialRole.FOCUS,
                anchor_id=final_anchor,
                occupancy_slot=slot,
                facing_target=facing,
                placement_confidence=placement_conf
            )
            solved.placements.append(placement)
            
        return solved
