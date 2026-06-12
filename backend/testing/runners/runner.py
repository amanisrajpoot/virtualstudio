"""Orchestrates end-to-end testing of StoryForge scenarios."""

import yaml
from pathlib import Path
from typing import Dict, Any

from backend.compiler.schemas import StoryBeatDraft
from backend.director.planner import DirectorPlanner
from backend.director.scene_resolver import SceneResolver
from backend.director.staging_solver import StagingSolver, SolverFailure
from backend.dialogue.engine import DialogueEngine
from backend.events.bus import InProcessEventBus
from backend.events.store import EventStore
from backend.events.schemas import EventType, EventCategory, EventMetadata

from .golden_master import GoldenMasterEngine
from backend.testing.assertions import semantic_assertions

class StoryTestRunner:
    def __init__(self, scenarios_dir: str = "backend/testing/scenarios"):
        self.scenarios_dir = Path(scenarios_dir)
        self.golden_engine = GoldenMasterEngine()
        
        self.store = EventStore(base_dir="backend/testing/reports/events")
        self.bus = InProcessEventBus(store=self.store)
        
        # Pipeline modules
        self.planner = DirectorPlanner()
        self.resolver = SceneResolver()
        self.solver = StagingSolver()
        self.dialogue = DialogueEngine()

    def load_scenario(self, scenario_id: str) -> Dict[str, Any]:
        path = self.scenarios_dir / f"{scenario_id}.yaml"
        with open(path, "r") as f:
            return yaml.safe_load(f)

    def run(self, scenario_id: str, update_goldens: bool = False) -> bool:
        """Executes a scenario end-to-end. Returns True if passed, False otherwise."""
        print(f"\n[{scenario_id}] Starting Scenario Execution")
        
        try:
            scenario = self.load_scenario(scenario_id)
        except Exception as e:
            print(f"[{scenario_id}] ❌ Failed to load scenario: {e}")
            return False
            
        correlation_id = f"test_{scenario_id}"
        expected = scenario.get("expected", {})
        
        # Clear out historical events for this correlation_id just in case
        # (in a real test runner, we'd use a unique correlation_id or clear the store)
        
        # We will mock the Compiler output directly from the scenario or use a hardcoded map
        # For V1, the 'compiler' step is a mock parser based on scenario ID to keep it contained without connecting to an actual LLM.
        compiler_outputs = self._mock_compiler(scenario_id)
        
        if expected.get("compiler_status") == "needs_clarification":
            # Test failure expectations
            if not compiler_outputs:
                print(f"[{scenario_id}] ✅ Compiler correctly returned failure/needs_clarification")
                return True
            else:
                print(f"[{scenario_id}] ❌ Compiler expected needs_clarification but generated output")
                return False

        if not compiler_outputs:
            print(f"[{scenario_id}] ❌ Compiler failed to output anything")
            return False
            
        pipeline_output = []
        solved_beats = []
        
        try:
            for beat_draft in compiler_outputs:
                self.bus.publish(EventType.INTENT_MAPPED, EventCategory.DOMAIN, correlation_id, {"intent": beat_draft.intent}, EventMetadata(producer="Compiler"))
                
                # 1. Planner
                staged = self.planner.plan_beat(beat_draft)
                self.bus.publish(EventType.BEAT_PLANNED, EventCategory.DOMAIN, correlation_id, {}, EventMetadata(producer="Planner"))
                
                # 2. Scene Resolver
                resolved = self.resolver.resolve_beat(staged, expected.get("scene", "scene_village_market_v1"))
                self.bus.publish(EventType.SCENE_RESOLVED, EventCategory.DOMAIN, correlation_id, {}, EventMetadata(producer="Resolver"))
                
                # 3. Solver
                solved = self.solver.solve_beat(resolved, expected.get("scene", "scene_village_market_v1"))
                self.bus.publish(EventType.BEAT_STAGED, EventCategory.DOMAIN, correlation_id, {}, EventMetadata(producer="Solver"))
                solved_beats.append(solved)
                
                # 4. Dialogue
                dialogue = self.dialogue.process_beat(solved)
                if dialogue.dialogue_line:
                    self.bus.publish(EventType.DIALOGUE_GENERATED, EventCategory.DOMAIN, correlation_id, {"tags": dialogue.dialogue_line.tags.model_dump()}, EventMetadata(producer="Dialogue"))
                
                pipeline_output.append(dialogue)
                
        except SolverFailure as e:
            self.bus.publish(EventType.SOLVER_FAILED, EventCategory.SYSTEM, correlation_id, {"error": str(e)}, EventMetadata(producer="Solver"))
            if expected.get("solver_failure_expected"):
                print(f"[{scenario_id}] ✅ Solver correctly threw expected failure.")
                return True
            print(f"[{scenario_id}] ❌ Unexpected SolverFailure: {e}")
            return False

        except Exception as e:
            print(f"[{scenario_id}] ❌ Unexpected Pipeline Exception: {e}")
            return False

        # Apply Assertions
        try:
            # 1. Goldens
            if not self.golden_engine.capture_and_compare(scenario_id, pipeline_output, update_goldens=update_goldens):
                print(f"[{scenario_id}] ❌ Golden Master mismatch")
                return False
                
            # 2. Semantic Assertions
            if "formations" in expected:
                for b in solved_beats:
                    semantic_assertions.assert_valid_formations(b, expected["formations"])
            if "roles" in expected:
                for b in solved_beats:
                    semantic_assertions.assert_valid_roles(b.placements, expected["roles"])
                    
            for b in solved_beats:
                semantic_assertions.assert_no_collisions(b.placements)
                
            # 3. Event Bus Assertions
            events = self.store.load_events(correlation_id)
            semantic_assertions.assert_event_published(events, EventType.BEAT_STAGED)
            semantic_assertions.assert_event_order(events, [EventType.INTENT_MAPPED, EventType.BEAT_PLANNED, EventType.SCENE_RESOLVED, EventType.BEAT_STAGED])
            
        except AssertionError as e:
            print(f"[{scenario_id}] ❌ Assertion Failed: {e}")
            return False
            
        print(f"[{scenario_id}] ✅ PASS")
        return True

    def _mock_compiler(self, scenario_id: str) -> list[StoryBeatDraft]:
        """A simple mock to replace the actual compiler LLM for these deterministic tests."""
        if scenario_id == "sell_moonlight":
            return [StoryBeatDraft(intent="sell_product", intent_confidence=0.9, actor="char_halku_v1", target="char_policeman_v1")]
        elif scenario_id == "police_argument":
            return [StoryBeatDraft(intent="argue", intent_confidence=0.9, actor="char_policeman_v1", target="char_halku_v1")]
        elif scenario_id == "market_crowd":
            return [
                StoryBeatDraft(intent="idle", intent_confidence=1.0, actor="v1"),
                StoryBeatDraft(intent="idle", intent_confidence=1.0, actor="v2"),
                StoryBeatDraft(intent="idle", intent_confidence=1.0, actor="v3"),
            ]
        elif scenario_id == "overflow_failure":
            return [StoryBeatDraft(intent="idle", intent_confidence=1.0, actor=f"actor_{i}") for i in range(25)]
        return []
