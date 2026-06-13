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
from backend.models.project import ProjectManifest, ProjectSnapshot, ProjectRevision
from backend.repositories.projects import ProjectRepository
from backend.models.collaboration import ProjectComment, CommentAnchorType
from backend.repositories.collaboration import CollaborationRepository
from backend.repositories.templates import TemplateRepository
from backend.render_queue.queue import RenderQueue
from backend.render_queue.workers import WorkerRegistry
from backend.render_queue.scheduler import RenderScheduler
from backend.models.render_queue import RenderJob, RenderStatus, WorkerHeartbeat, WorkerInfo
from backend.repositories.marketplace import MarketplaceRepository
from backend.templates.skeleton_generator import SkeletonGenerator
from backend.models.story_graph import GraphOverride
from backend.repositories.graph_overrides import GraphOverrideRepository
from backend.incremental.compiler import SemanticCompiler
from backend.incremental.cache import SemanticCache
from backend.preview.builder import PreviewCache, PreviewBuilder
from backend.observability.tracker import telemetry
from backend.observability.schemas import StoryHealthBreakdown
import datetime

app = FastAPI(title="StoryForge API")
char_repo = CharacterRepository()
world_repo = WorldRepository()
story_repo = StoryRepository()
project_repo = ProjectRepository()
collab_repo = CollaborationRepository()
template_repo = TemplateRepository()

render_queue = RenderQueue()
worker_registry = WorkerRegistry()
render_scheduler = RenderScheduler(render_queue, worker_registry)
marketplace_repo = MarketplaceRepository()
skeleton_gen = SkeletonGenerator()
preview_cache = PreviewCache()
preview_builder = PreviewBuilder(preview_cache)
graph_repo = GraphOverrideRepository()
sem_cache = SemanticCache()
graph_compiler = SemanticCompiler(preview_builder, sem_cache, graph_repo)

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
    graph = graph_compiler.compile(req.story_id, req.text, req.world_id, req.characters)
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

# --- Project Endpoints ---

@app.get("/api/projects")
async def list_projects():
    return {"projects": [p.model_dump() for p in project_repo.list_manifests()]}

@app.post("/api/projects")
async def create_project(req: ProjectManifest):
    req.updated_at = datetime.datetime.now().isoformat()
    req.created_at = req.updated_at
    project_repo.save_manifest(req)
    return {"status": "success", "id": req.project_id}

@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    p = project_repo.get_manifest(project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return p.model_dump()

class SnapshotRequest(BaseModel):
    project_id: str
    summary: str
    semantic_graph: dict
    overrides: list
    preview_state: dict

@app.post("/api/projects/{project_id}/snapshot")
async def create_snapshot(project_id: str, req: SnapshotRequest):
    p = project_repo.get_manifest(project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
        
    p.graph_version += 1
    p.active_snapshot_version = p.graph_version
    
    rev = ProjectRevision(
        revision_id=f"rev_{p.graph_version}",
        graph_version=p.graph_version,
        summary=req.summary,
        timestamp=datetime.datetime.now().isoformat()
    )
    p.revisions.append(rev)
    p.updated_at = datetime.datetime.now().isoformat()
    
    snapshot = ProjectSnapshot(
        project_id=project_id,
        graph_version=p.graph_version,
        semantic_graph=req.semantic_graph,
        overrides=req.overrides,
        preview_state=req.preview_state
    )
    
    project_repo.save_snapshot(snapshot)
    project_repo.save_manifest(p)
    
    return {"status": "success", "version": p.graph_version}

# --- Collaboration Endpoints ---

@app.get("/api/auth/users")
async def get_users():
    return {"users": [u.model_dump() for u in collab_repo.get_mock_users()]}

@app.get("/api/projects/{project_id}/comments")
async def get_comments(project_id: str):
    return {"comments": [c.model_dump() for c in collab_repo.get_comments(project_id)]}

class CreateCommentRequest(BaseModel):
    parent_comment_id: Optional[str] = None
    anchor_type: CommentAnchorType
    anchor_id: str
    author_id: str
    text: str

@app.post("/api/projects/{project_id}/comments")
async def add_comment(project_id: str, req: CreateCommentRequest):
    import uuid
    comment = ProjectComment(
        comment_id=str(uuid.uuid4()),
        project_id=project_id,
        parent_comment_id=req.parent_comment_id,
        anchor_type=req.anchor_type,
        anchor_id=req.anchor_id,
        author_id=req.author_id,
        text=req.text,
        created_at=datetime.datetime.now().isoformat()
    )
    collab_repo.add_comment(project_id, comment)
    telemetry.track_event("COMMENT_CREATED", {"project_id": project_id, "comment_id": comment.comment_id, "anchor_id": req.anchor_id})
    return comment.model_dump()

class ResolveCommentRequest(BaseModel):
    user_id: str

@app.post("/api/projects/{project_id}/comments/{comment_id}/resolve")
async def resolve_comment(project_id: str, comment_id: str, req: ResolveCommentRequest):
    success = collab_repo.resolve_comment(project_id, comment_id, req.user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Comment not found")
    telemetry.track_event("COMMENT_RESOLVED", {"project_id": project_id, "comment_id": comment_id, "resolved_by": req.user_id})
    return {"status": "success"}

class ApproveRevisionRequest(BaseModel):
    user_id: str

@app.post("/api/projects/{project_id}/revisions/{revision_id}/approve")
async def approve_revision(project_id: str, revision_id: str, req: ApproveRevisionRequest):
    p = project_repo.get_manifest(project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
        
    success = collab_repo.process_approval(p, revision_id, req.user_id)
    if not success:
        raise HTTPException(status_code=403, detail="User does not have permission to approve")
        
    project_repo.save_manifest(p)
    telemetry.track_event("REVISION_APPROVED", {"project_id": project_id, "revision_id": revision_id, "approved_by": req.user_id})
    return {"status": "success"}

# --- Render Control Plane Endpoints ---

class RenderJobRequest(BaseModel):
    project_id: str
    snapshot_version: int
    submitted_by: str
    priority: int = 1

@app.post("/api/render/jobs")
async def submit_render_job(req: RenderJobRequest):
    import uuid
    p = project_repo.get_manifest(req.project_id)
    approval_status = "not_approved"
    if p:
        for app in p.approvals:
            if app.get("revision_id") == f"rev_{req.snapshot_version}":
                approval_status = app.get("status", "not_approved")
                break

    job = RenderJob(
        job_id=str(uuid.uuid4()),
        project_id=req.project_id,
        snapshot_version=req.snapshot_version,
        approval_status=approval_status,
        status=RenderStatus.QUEUED,
        submitted_by=req.submitted_by,
        submitted_at=datetime.datetime.now().isoformat(),
        priority=req.priority
    )
    render_queue.submit_job(job)
    render_scheduler.schedule_jobs()
    telemetry.track_event("RENDER_JOB_CREATED", {"job_id": job.job_id, "project_id": job.project_id})
    return job.model_dump()

@app.get("/api/render/jobs")
async def get_render_jobs():
    return {"jobs": [j.model_dump() for j in render_queue.get_all_jobs()]}

@app.get("/api/render/metrics")
async def get_render_metrics():
    return render_queue.get_metrics().model_dump()

@app.post("/api/render/workers/heartbeat")
async def worker_heartbeat(hb: WorkerHeartbeat):
    worker_registry.process_heartbeat(hb)
    render_scheduler.schedule_jobs()
    return {"status": "ok"}

@app.post("/api/render/workers/register")
async def register_worker(info: WorkerInfo):
    worker_registry.register_worker(info)
    render_scheduler.schedule_jobs()
    return {"status": "ok"}

# --- Marketplace Endpoints ---

@app.get("/api/marketplace/assets")
async def get_marketplace_assets(
    type: Optional[str] = None,
    goal: Optional[str] = None,
    tag: Optional[str] = None,
    featured: bool = False
):
    assets = marketplace_repo.get_assets(type_filter=type, goal_filter=goal, tag_filter=tag, featured_only=featured)
    return {"assets": [a.model_dump() for a in assets]}

@app.get("/api/marketplace/assets/{asset_id}")
async def get_marketplace_asset(asset_id: str):
    asset = marketplace_repo.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset.model_dump()

class PublishRequest(BaseModel):
    author_id: str
    asset_data: dict

@app.post("/api/marketplace/publish")
async def publish_marketplace_asset(req: PublishRequest):
    asset = marketplace_repo.publish_asset(req.asset_data, req.author_id)
    telemetry.track_event("ASSET_PUBLISHED", {"asset_id": asset.asset_id, "author_id": req.author_id})
    return asset.model_dump()

class ForkRequest(BaseModel):
    asset_id: str
    author_id: str

@app.post("/api/marketplace/fork")
async def fork_marketplace_asset(req: ForkRequest):
    asset = marketplace_repo.fork_asset(req.asset_id, req.author_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Parent asset not found")
    telemetry.track_event("ASSET_FORKED", {"asset_id": asset.asset_id, "parent_id": req.asset_id, "author_id": req.author_id})
    return asset.model_dump()

class RateRequest(BaseModel):
    user_id: str
    score: int

@app.post("/api/marketplace/assets/{asset_id}/rate")
async def rate_marketplace_asset(asset_id: str, req: RateRequest):
    asset = marketplace_repo.rate_asset(asset_id, req.user_id, req.score)
    if not asset:
        raise HTTPException(status_code=400, detail="Invalid rating or asset not found")
    telemetry.track_event("ASSET_RATED", {"asset_id": asset_id, "score": req.score})
    return asset.model_dump()

@app.post("/api/marketplace/assets/{asset_id}/download")
async def download_marketplace_asset(asset_id: str):
    success = marketplace_repo.record_download(asset_id)
    if not success:
        raise HTTPException(status_code=404, detail="Asset not found")
    telemetry.track_event("ASSET_DOWNLOADED", {"asset_id": asset_id})
    return {"status": "success"}

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
