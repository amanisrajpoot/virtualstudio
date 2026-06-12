"""Seed script for StoryForge Templates."""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.models.story import StoryGoal, StoryArchetype, StoryTemplate
from backend.repositories.templates import TemplateRepository

def seed():
    repo = TemplateRepository(data_dir="data/templates")
    
    # 1. Seed Goals
    goals = [
        StoryGoal(id="sell_product", name="Sell Something", category="commerce", supported_formations=["face_to_face"], supported_worlds=[]),
        StoryGoal(id="argue", name="Argue", category="conflict", supported_formations=["face_to_face", "argument_2p"], supported_worlds=[]),
        StoryGoal(id="prank", name="Prank Someone", category="comedy", supported_formations=["side_by_side", "pursuit"], supported_worlds=[]),
        StoryGoal(id="run_away", name="Run Away", category="action", supported_formations=["pursuit"], supported_worlds=[]),
        StoryGoal(id="convince", name="Convince Someone", category="drama", supported_formations=["face_to_face"], supported_worlds=[])
    ]
    repo.save_goals(goals)
    
    # 2. Seed Archetypes
    archetypes = [
        StoryArchetype(id="comedy", name="Comedy"),
        StoryArchetype(id="drama", name="Drama"),
        StoryArchetype(id="conflict", name="Conflict"),
        StoryArchetype(id="mystery", name="Mystery"),
        StoryArchetype(id="action", name="Action")
    ]
    repo.save_archetypes(archetypes)
    
    # 3. Seed Templates
    templates = [
        StoryTemplate(
            id="village_comedy",
            name="Village Comedy",
            category="Comedy",
            difficulty="beginner",
            world_id="village_market",
            character_ids=["halku", "policeman"],
            goal_id="sell_product",
            archetype_id="comedy",
            starter_script="Halku sets up a ridiculous stall in the village market.\nHe tries to sell a clearly fake item.\nThe policeman approaches, looking extremely skeptical.\nThey argue about the price."
        ),
        StoryTemplate(
            id="police_confrontation",
            name="Police Confrontation",
            category="Conflict",
            difficulty="beginner",
            world_id="police_chowki",
            character_ids=["policeman", "sony_spark"],
            goal_id="argue",
            archetype_id="drama",
            starter_script="Sony Spark enters the Police Chowki demanding justice.\nThe policeman asks for details.\nAn argument breaks out."
        ),
        StoryTemplate(
            id="tea_stall_gossip",
            name="Tea Stall Gossip",
            category="Daily Life",
            difficulty="beginner",
            world_id="tea_stall",
            character_ids=["halku", "desi_ironman"],
            goal_id="convince",
            archetype_id="comedy",
            starter_script="Halku and Desi Ironman are having tea.\nHalku tries to convince Ironman to start a new business."
        ),
        StoryTemplate(
            id="wedding_chaos",
            name="Wedding Chaos",
            category="Festival",
            difficulty="intermediate",
            world_id="marriage_hall",
            character_ids=["sony_spark", "halku"],
            goal_id="argue",
            archetype_id="comedy",
            starter_script="Sony Spark and Halku are at a crowded marriage hall.\nThey realize they are wearing the exact same outfit.\nAn argument begins."
        ),
        StoryTemplate(
            id="cricket_ground_rivalry",
            name="Cricket Ground Rivalry",
            category="Sports",
            difficulty="beginner",
            world_id="cricket_ground",
            character_ids=["halku", "desi_ironman"],
            goal_id="argue",
            archetype_id="drama",
            starter_script="Halku claims he hit a six.\nDesi Ironman claims it was a catch.\nA huge fight starts on the pitch."
        ),
        StoryTemplate(
            id="temple_donation_scam",
            name="Temple Donation Scam",
            category="Conflict",
            difficulty="advanced",
            world_id="local_temple",
            character_ids=["policeman", "halku"],
            goal_id="sell_product",
            archetype_id="conflict",
            starter_script="Halku is trying to collect fake donations outside the temple.\nThe policeman catches him."
        ),
        StoryTemplate(
            id="bus_stop_confusion",
            name="Bus Stop Confusion",
            category="Comedy",
            difficulty="beginner",
            world_id="bus_stand",
            character_ids=["sony_spark", "desi_ironman"],
            goal_id="prank",
            archetype_id="comedy",
            starter_script="Sony Spark convinces Desi Ironman that the bus to Mumbai leaves from here.\nIt's actually a local village stop."
        ),
        StoryTemplate(
            id="lost_mobile_mystery",
            name="Lost Mobile Mystery",
            category="Mystery",
            difficulty="intermediate",
            world_id="village_market",
            character_ids=["policeman", "halku"],
            goal_id="convince",
            archetype_id="mystery",
            starter_script="The policeman has lost his phone.\nHe tries to convince Halku that he saw someone steal it."
        ),
        StoryTemplate(
            id="panchayat_dispute",
            name="Panchayat Dispute",
            category="Drama",
            difficulty="advanced",
            world_id="panchayat_area",
            character_ids=["halku", "desi_ironman"],
            goal_id="argue",
            archetype_id="drama",
            starter_script="A serious land dispute is brought before the Panchayat.\nHalku and Desi Ironman argue their cases."
        ),
        StoryTemplate(
            id="election_rally",
            name="Election Rally",
            category="Event",
            difficulty="intermediate",
            world_id="election_rally_ground",
            character_ids=["desi_ironman", "policeman"],
            goal_id="convince",
            archetype_id="conflict",
            starter_script="Desi Ironman is giving a speech.\nThe policeman tries to shut down the rally."
        )
    ]
    
    for t in templates:
        repo.save_template(t)
        
    print(f"Successfully seeded {len(goals)} goals, {len(archetypes)} archetypes, and {len(templates)} templates.")

if __name__ == "__main__":
    seed()
