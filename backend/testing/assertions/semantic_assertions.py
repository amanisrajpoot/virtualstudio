"""Reusable Semantic Assertions for Story Testing."""

from typing import List, Dict, Any

def assert_no_collisions(placements: List[Any]):
    """Ensures no two actors occupy the exact same anchor and slot."""
    occupancy = set()
    for p in placements:
        key = f"{p.anchor_id}:{p.occupancy_slot}"
        if key in occupancy:
            raise AssertionError(f"Collision Detected! Multiple actors assigned to {key}")
        occupancy.add(key)

def assert_valid_roles(placements: List[Any], expected_roles: List[str]):
    """Ensures that specific roles are present in the final placements."""
    found_roles = {p.spatial_role.value if hasattr(p.spatial_role, 'value') else str(p.spatial_role) for p in placements}
    for role in expected_roles:
        if role not in found_roles:
            raise AssertionError(f"Missing expected role: {role}. Found: {found_roles}")

def assert_valid_formations(beat: Any, expected_formations: List[str]):
    """Ensures expected formations were assigned by the planner."""
    actual_formation = None
    if getattr(beat, "composition", None) and getattr(beat.composition, "formation", None):
        actual_formation = beat.composition.formation.value if hasattr(beat.composition.formation, 'value') else str(beat.composition.formation)
        
    for expected in expected_formations:
        if expected != actual_formation:
            raise AssertionError(f"Expected formation {expected}, but got {actual_formation}")

def assert_event_published(events: List[Any], target_event_type: str):
    """Ensures an event of target_event_type was published to the bus."""
    found = any((e.event_type.value if hasattr(e.event_type, 'value') else str(e.event_type)) == target_event_type for e in events)
    if not found:
        types = [(e.event_type.value if hasattr(e.event_type, 'value') else str(e.event_type)) for e in events]
        raise AssertionError(f"Expected event {target_event_type} was not published. Events: {types}")

def assert_event_order(events: List[Any], expected_sequence: List[str]):
    """Ensures that a list of event types occurred in the specified order."""
    types = [(e.event_type.value if hasattr(e.event_type, 'value') else str(e.event_type)) for e in events]
    
    last_index = -1
    for expected in expected_sequence:
        try:
            # Find the first occurrence after the last index
            index = types.index(expected, last_index + 1)
            last_index = index
        except ValueError:
            raise AssertionError(f"Expected sequence failed at '{expected}'. Actual sequence: {types}")
