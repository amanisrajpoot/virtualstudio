"""FastAPI Wrapper for StoryForge Backend."""

from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import uuid
from backend.models.character import CharacterProfile
from backend.repositories.characters import CharacterRepository
from backend.models.world import WorldProfile
from backend.repositories.worlds import WorldRepository
from backend.models.story import Story
from backend.repositories.stories import StoryRepository
from backend.repositories.templates import TemplateRepository
from backend.templates.skeleton_generator import SkeletonGenerator
from backend.models.story_graph import GraphOverride
from backend.repositories.graph_overrides import GraphOverrideRepository
from backend.story_graph.builder import StoryGraphBuilder
from backend.preview.builder import PreviewCache, PreviewBuilder
from backend.observability.tracker import telemetry
from backend.observability.schemas import StoryHealthBreakdown
import datetime

app = FastAPI(title="StoryForge API")
char_repo = CharacterRepository()
world_repo = WorldRepository()
story_repo = StoryRepository()
template_repo = TemplateRepository()
skeleton_gen = SkeletonGenerator()
preview_cache = PreviewCache()
preview_builder = PreviewBuilder(preview_cache)
graph_repo = GraphOverrideRepository()
graph_builder = StoryGraphBuilder(preview_builder, graph_repo)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow nextjs frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from typing import List, Optional

class StoryCompileRequest(BaseModel):
    text: str
    world_id: Optional[str] = None
    characters: Optional[List[str]] = None

@app.get("/api/health")
async def health():
    return {"status": "ok"}

@app.get("/api/projects")
async def list_projects():
    return {
        "projects": [
            {"id": "p1", "name": "Moonlight Seller", "status": "Active"},
            {"id": "p2", "name": "Police Interrogation", "status": "Draft"}
        ]
    }

@app.post("/api/story/compile")
async def compile_story(request: StoryCompileRequest):
    # Route compilation request directly through PreviewBuilder for seamless integration
    world_id = request.world_id if request.world_id is not None else ""
    characters = request.characters if request.characters is not None else []
    
    # We use a dummy story_id for now, the frontend expects a package
    package = preview_builder.build(
        story_id=str(uuid.uuid4()),
        text=request.text,
        world_id=world_id,
        characters=characters
    )
    
    return package.model_dump()

@app.post("/api/preview/build")
async def build_preview(request: StoryCompileRequest):
    # Direct access to the preview package builder
    world_id = request.world_id if request.world_id is not None else ""
    characters = request.characters if request.characters is not None else []
    
    package = preview_builder.build(
        story_id=str(uuid.uuid4()),
        text=request.text,
        world_id=world_id,
        characters=characters
    )
    return package.model_dump()

@app.post("/api/preview/refresh")
async def refresh_preview(request: StoryCompileRequest):
    # In future, partial refresh logic goes here.
    # For now, it behaves identically to build.
    world_id = request.world_id if request.world_id is not None else ""
    characters = request.characters if request.characters is not None else []
    
    package = preview_builder.build(
        story_id=str(uuid.uuid4()),
        text=request.text,
        world_id=world_id,
        characters=characters
    )
    return package.model_dump()

# --- Character Studio Endpoints ---

@app.get("/api/characters")
async def list_characters():
    return {"characters": char_repo.list()}

@app.get("/api/characters/{character_id}")
async def get_character(character_id: str):
    profile = char_repo.get(character_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Character not found")
    return profile

@app.post("/api/characters")
async def save_character(profile: CharacterProfile):
    char_repo.save(profile)
    return {"status": "success", "id": profile.id}

class GenerateConceptRequest(BaseModel):
    description: str

@app.post("/api/characters/generate-concept")
async def generate_concept(request: GenerateConceptRequest):
    # The Asset Generation Contract
    return {
        "job_id": str(uuid.uuid4()),
        "status": "completed",
        "images": [
            "/mock/halku_concept_1.png",
            "/mock/halku_concept_2.png",
            "/mock/halku_concept_3.png"
        ]
    }

# --- World Studio Endpoints ---

@app.get("/api/worlds")
async def list_worlds():
    return {"worlds": world_repo.list()}

@app.get("/api/worlds/{world_id}")
async def get_world(world_id: str):
    profile = world_repo.get(world_id)
    if not profile:
        raise HTTPException(status_code=404, detail="World not found")
    return profile

@app.post("/api/worlds")
async def save_world(profile: WorldProfile):
    world_repo.save(profile)
    return {"status": "success", "id": profile.id}

class GenerateWorldRequest(BaseModel):
    description: str

@app.post("/api/worlds/generate")
async def generate_world(request: GenerateWorldRequest):
    # World Generation Contract Mock
    return {
        "job_id": str(uuid.uuid4()),
        "status": "completed",
        "zones": [
            {"id": "zone_1", "name": "Main Area", "zone_type": "gathering", "capacity": 10, "adjacent": ["zone_2"]},
            {"id": "zone_2", "name": "Side Path", "zone_type": "transit", "capacity": 5, "adjacent": ["zone_1"]}
        ],
        "props": [
            {"prop_id": "generic_stall", "required": True}
        ]
    }

# --- Render Endpoints ---
async def list_render_jobs():
    return {
        "jobs": [
            {"job_id": "job_1", "story": "Moonlight Seller", "status": "Completed"},
            {"job_id": "job_2", "story": "Police Interrogation", "status": "Rendering"}
        ]
    }

@app.get("/api/render/{job_id}")
async def get_render_job(job_id: str):
    return {
        "job_id": job_id,
        "status": "Rendering",
        "stages": {
            "compiling": True,
            "planning": True,
            "dialogue": True,
            "audio": True,
            "assets": True,
            "rendering": False,
            "export": False
        }
    }

@app.websocket("/api/events")
async def websocket_events(websocket: WebSocket):
    await websocket.accept()
    # Mock stream of telemetry events for the Developer Mode timeline
    try:
        events = [
            "StorySubmitted",
            "StoryCompiled",
            "BeatPlanned",
            "DialogueGenerated",
            "AudioRequested",
            "AudioGenerated",
            "AssetRequested",
            "AssetReady",
            "TimelineBuilt",
            "RenderStarted"
        ]
        for event in events:
            await asyncio.sleep(2) # Mock delay
            await websocket.send_json({"event_type": event, "timestamp": "now"})
    except Exception:
        pass

# --- Story & Template Endpoints ---

@app.get("/api/stories")
async def list_stories():
    return {"stories": [s.model_dump() for s in story_repo.list()]}

@app.get("/api/stories/{story_id}")
async def get_story(story_id: str):
    story = story_repo.get(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story.model_dump()

@app.post("/api/stories")
async def save_story(story: Story):
    story.updated_at = datetime.datetime.now().isoformat()
    story_repo.save(story)
    return {"status": "success", "id": story.id}

class GenerateSkeletonRequest(BaseModel):
    world_id: str
    characters: List[str]
    goal_id: str
    archetype_id: str

@app.post("/api/stories/generate-skeleton")
async def generate_skeleton(req: GenerateSkeletonRequest):
    script = skeleton_gen.generate(req.world_id, req.characters, req.goal_id, req.archetype_id)
    return {"script": script}

# --- Graph Endpoints ---

class GraphBuildRequest(BaseModel):
    story_id: str
    text: str
    world_id: str
    characters: List[str]

@app.post("/api/graph/build")
async def build_graph(req: GraphBuildRequest):
    graph = graph_builder.build_graph(req.story_id, req.text, req.world_id, req.characters)
    return graph.model_dump()

class GraphOverrideRequest(BaseModel):
    story_id: str
    node_id: str
    original_intent: str
    overridden_intent: str

@app.post("/api/graph/override-intent")
async def override_intent(req: GraphOverrideRequest):
    override = GraphOverride(
        story_id=req.story_id,
        node_id=req.node_id,
        original_intent=req.original_intent,
        overridden_intent=req.overridden_intent,
        timestamp=datetime.datetime.now().isoformat()
    )
    graph_repo.save_override(override)
    return {"status": "success"}

@app.get("/api/goals")
async def get_goals():
    return {"goals": [g.model_dump() for g in template_repo.list_goals()]}

@app.get("/api/archetypes")
async def get_archetypes():
    return {"archetypes": [a.model_dump() for a in template_repo.list_archetypes()]}

@app.get("/api/templates")
async def get_templates():
    return {"templates": [t.model_dump() for t in template_repo.list_templates()]}

# --- Observability Endpoints ---

@app.get("/api/observability/metrics")
async def get_metrics():
    return {
        "aggregates": [x.model_dump() for x in telemetry.get_aggregates()],
        "cache": telemetry.get_cache_metrics().model_dump(),
        "funnel": {
            "stories_created": 120,
            "previews_generated": 105,
            "renders_started": 40,
            "renders_completed": 38
        }
    }

@app.get("/api/observability/failures")
async def get_failures():
    return {
        "failures": [x.model_dump() for x in telemetry.get_failures()],
        "most_common_missing_assets": ["halku_voice_v2", "market_stall_prop", "rain_vfx"],
        "most_common_invalid_worlds": ["empty_void", "test_world"]
    }

@app.get("/api/observability/health/{story_id}")
async def get_story_health(story_id: str):
    # Mocking a health breakdown evaluation based on the requested multidimensional checks
    breakdown = StoryHealthBreakdown(
        assets_score=95,
        characters_score=100,
        world_score=90,
        timeline_score=100,
        dialogue_score=80,
        warnings=[
            "Missing required prop: 'tea_stall_bench' (-10 World)",
            "Actor 'policeman' missing voice profile (-10 Dialogue)"
        ]
    )
    breakdown.final_score = int(
        (breakdown.assets_score + breakdown.characters_score + breakdown.world_score + breakdown.timeline_score + breakdown.dialogue_score) / 5
    )
    return breakdown.model_dump()
