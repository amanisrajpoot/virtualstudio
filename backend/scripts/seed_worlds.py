"""Seed script for India-First World templates."""

import os
import sys

# Ensure backend module is resolvable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.models.world import WorldProfile, ZoneProfile, AmbienceProfile, FormationRef, PropRef, WorldConnection
from backend.repositories.worlds import WorldRepository

def seed_worlds(data_dir: str = "data/worlds"):
    repo = WorldRepository(data_dir=data_dir)
    
    worlds = [
        WorldProfile(
            id="village_market",
            name="Village Market",
            archetype="commercial",
            description="A bustling rural market with fresh produce and gossip.",
            zones=[
                ZoneProfile(id="market_stall", name="Market Stall", zone_type="selling_zone", capacity=2, adjacent=["road", "crowd_area"]),
                ZoneProfile(id="road", name="Main Road", zone_type="transit", capacity=5, adjacent=["market_stall"]),
                ZoneProfile(id="crowd_area", name="Crowd Area", zone_type="gathering", capacity=10, adjacent=["market_stall"])
            ],
            formations=[FormationRef(formation_id="SELLING", supported_zone_types=["selling_zone"])],
            props=[PropRef(prop_id="vegetable_cart", required=True), PropRef(prop_id="tea_stall", required=False)],
            ambience=AmbienceProfile(time_of_day="day", weather="clear", crowd_density=0.8, noise_profile="market_busy"),
            connected_worlds=[WorldConnection(target_world="tea_stall", connection_type="walking_distance"), WorldConnection(target_world="village_street", connection_type="road_connected")]
        ),
        WorldProfile(
            id="tea_stall",
            name="Tea Stall",
            archetype="commercial",
            description="A local gathering spot for chai and discussion.",
            zones=[ZoneProfile(id="bench", name="Wooden Bench", zone_type="seating", capacity=3, adjacent=["counter"])],
            formations=[FormationRef(formation_id="ARGUMENT", supported_zone_types=["seating"])],
            props=[PropRef(prop_id="chai_glasses", required=True)],
            ambience=AmbienceProfile(time_of_day="morning", weather="clear", crowd_density=0.5, noise_profile="chatter"),
            connected_worlds=[WorldConnection(target_world="village_market", connection_type="adjacent")]
        ),
        WorldProfile(id="village_street", name="Village Street", archetype="residential", description="A dusty path between village homes.", zones=[], formations=[], props=[], ambience=AmbienceProfile(), connected_worlds=[]),
        WorldProfile(id="police_chowki", name="Police Chowki", archetype="institutional", description="A small rural police outpost.", zones=[], formations=[], props=[], ambience=AmbienceProfile(), connected_worlds=[]),
        WorldProfile(id="marriage_hall", name="Marriage Hall", archetype="recreational", description="A vibrant venue decorated for a wedding.", zones=[], formations=[], props=[], ambience=AmbienceProfile(), connected_worlds=[]),
        WorldProfile(id="bus_stop", name="Bus Stop", archetype="transport", description="A shaded stop on the highway.", zones=[], formations=[], props=[], ambience=AmbienceProfile(), connected_worlds=[]),
        WorldProfile(id="railway_platform", name="Railway Platform", archetype="transport", description="A chaotic station platform.", zones=[], formations=[], props=[], ambience=AmbienceProfile(), connected_worlds=[]),
        WorldProfile(id="classroom", name="Classroom", archetype="institutional", description="A rural school classroom.", zones=[], formations=[], props=[], ambience=AmbienceProfile(), connected_worlds=[]),
        WorldProfile(id="local_shop", name="Local Shop", archetype="commercial", description="A tiny kirana store.", zones=[], formations=[], props=[], ambience=AmbienceProfile(), connected_worlds=[]),
        WorldProfile(id="panchayat_area", name="Panchayat Area", archetype="institutional", description="The village gathering tree.", zones=[], formations=[], props=[], ambience=AmbienceProfile(), connected_worlds=[]),
        WorldProfile(id="small_town_hospital", name="Small Town Hospital", archetype="institutional", description="A basic medical clinic.", zones=[], formations=[], props=[], ambience=AmbienceProfile(), connected_worlds=[]),
        WorldProfile(id="cricket_ground", name="Cricket Ground", archetype="recreational", description="An open dusty field.", zones=[], formations=[], props=[], ambience=AmbienceProfile(), connected_worlds=[]),
        WorldProfile(id="local_temple", name="Local Temple", archetype="religious", description="A small neighborhood shrine.", zones=[], formations=[], props=[], ambience=AmbienceProfile(), connected_worlds=[]),
        WorldProfile(id="barber_shop", name="Barber Shop", archetype="commercial", description="A small salon.", zones=[], formations=[], props=[], ambience=AmbienceProfile(), connected_worlds=[]),
        WorldProfile(id="election_rally", name="Election Rally Ground", archetype="recreational", description="A large field with a stage.", zones=[], formations=[], props=[], ambience=AmbienceProfile(), connected_worlds=[])
    ]

    for world in worlds:
        repo.save(world)
        print(f"Seeded World: {world.name}")

if __name__ == "__main__":
    seed_worlds()
    print("Seed complete.")
