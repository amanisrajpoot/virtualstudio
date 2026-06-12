# Semantic World System

Subsystem: 2

Status: implemented as contracts, PostgreSQL schema, seed anchors, backend API
module, and Godot 4 runtime resolver.

## Purpose

The Semantic World System replaces authored coordinates with named anchors.

External systems should not say:

```json
{
  "x": 12,
  "z": 5
}
```

They should say:

```json
{
  "anchor": "market_center"
}
```

Actual positions are resolved inside the active Godot scene from anchor markers.
This keeps Story DSL, Runtime DSL, Director rules, and future AI outputs free of
raw coordinates.

## Architecture

```text
Scene Asset
-> Semantic World Definition
-> Scene-Specific Anchors
-> Anchor Reference
-> Backend Validation
-> Godot Marker3D Lookup
-> Transform3D / Vector3 at runtime
```

Responsibilities are split deliberately:

- PostgreSQL stores which anchors exist for each scene asset.
- Backend APIs validate and normalize anchor references.
- Godot resolves valid anchors to real transforms using scene nodes.
- Later systems consume anchors, not coordinates.

## Folder Structure

```text
backend/
  semantic_world/
    __init__.py
    api.py
    constants.py
    repository.py
    schemas.py
    validation.py
database/
  migrations/
    002_create_semantic_world.sql
  seeds/
    002_semantic_world_v1.sql
schemas/
  semantic_world/
    semantic_world.schema.json
    openapi.yaml
godot_runtime/
  addons/
    storyforge/
      semantic_world/
        semantic_anchor_marker.gd
        semantic_world_resolver.gd
docs/
  semantic-world-system.md
```

## Data Model

### `semantic_worlds`

One row per scene asset.

- `scene_asset_id TEXT PRIMARY KEY`
- `version TEXT NOT NULL`
- `metadata JSONB NOT NULL`
- `created_at TIMESTAMPTZ`
- `updated_at TIMESTAMPTZ`

`scene_asset_id` references `assets(id)` from the Asset Registry.

### `semantic_anchors`

Scene-local anchors.

- `scene_asset_id TEXT NOT NULL`
- `anchor TEXT NOT NULL`
- `display_name TEXT NOT NULL`
- `tags TEXT[] NOT NULL`
- `metadata JSONB NOT NULL`
- `created_at TIMESTAMPTZ`
- `updated_at TIMESTAMPTZ`

Primary key:

```text
(scene_asset_id, anchor)
```

This allows different scenes to reuse names like `entrance` or
`market_center` with scene-specific runtime positions.

## Seeded World

Scene:

```text
scene_village_market_v1
```

Anchors:

- `entrance`
- `market_center`
- `stall_front`
- `stall_left`
- `tree_area`
- `buffalo_area`

Seed file:

```text
database/seeds/002_semantic_world_v1.sql
```

## Anchor References

Direct reference:

```json
{
  "anchor": "market_center"
}
```

Relative reference:

```json
{
  "anchor": "halku_slot",
  "relation": "left_of",
  "relative_to": "stall_front",
  "distance": "near"
}
```

The backend can validate whether referenced anchors exist. Godot is responsible
for calculating the actual runtime transform.

Supported relations:

- `at`
- `near`
- `left_of`
- `right_of`
- `in_front_of`
- `behind`
- `facing`

Supported distances:

- `contact`
- `near`
- `medium`
- `far`

Default runtime distances in Godot:

- `contact`: `0.5`
- `near`: `1.5`
- `medium`: `3.0`
- `far`: `6.0`

## API Contracts

Full contract:

```text
schemas/semantic_world/openapi.yaml
```

Endpoints:

```text
GET  /worlds
POST /worlds
GET  /worlds/{scene_asset_id}
GET  /worlds/{scene_asset_id}/anchors
POST /worlds/{scene_asset_id}/anchors
GET  /worlds/{scene_asset_id}/anchors/{anchor}
POST /worlds/{scene_asset_id}/resolve
```

Resolve example:

```http
POST /worlds/scene_village_market_v1/resolve
```

```json
{
  "anchor": "stall_front",
  "relation": "at"
}
```

Response:

```json
{
  "scene_asset_id": "scene_village_market_v1",
  "anchor": "stall_front",
  "relation": "at",
  "relative_to": null,
  "distance": "near",
  "valid": true,
  "errors": [],
  "lookup": {
    "group": "storyforge_anchor",
    "metadata_key": "storyforge_anchor_id",
    "node_name": "stall_front"
  },
  "runtime_reference": {
    "anchor": "stall_front",
    "relation": "at",
    "relative_to": null,
    "distance": "near"
  }
}
```

No coordinates are returned.

## Backend Integration

FastAPI router factory:

```python
from backend.semantic_world.api import create_semantic_world_router
from backend.semantic_world.repository import SemanticWorldRepository

pool = ...

def repository_provider() -> SemanticWorldRepository:
    return SemanticWorldRepository(pool)

app.include_router(create_semantic_world_router(repository_provider))
```

The repository expects an `asyncpg`-compatible pool.

## Godot Implementation

Anchor marker:

```text
godot_runtime/addons/storyforge/semantic_world/semantic_anchor_marker.gd
```

Attach `StoryForgeSemanticAnchorMarker` to `Marker3D` nodes in a scene. Set:

- `anchor_id`
- `tags`

At runtime the marker joins group:

```text
storyforge_anchor
```

And sets metadata:

```text
storyforge_anchor_id
storyforge_anchor_tags
```

Resolver:

```text
godot_runtime/addons/storyforge/semantic_world/semantic_world_resolver.gd
```

Basic usage:

```gdscript
var resolver := StoryForgeSemanticWorldResolver.new()
add_child(resolver)
resolver.index_scene(get_tree().current_scene)

var transform := resolver.resolve({
    "anchor": "market_center",
    "relation": "at"
})
```

Relative usage:

```gdscript
var transform := resolver.resolve({
    "anchor": "stall_front",
    "relation": "left_of",
    "relative_to": "stall_front",
    "distance": "near"
})
```

The resolver returns:

- `Transform3D` via `resolve()`
- `Vector3` via `resolve_position()`

These runtime values are internal to Godot execution. They should not be stored
in Story DSL or backend story contracts.

## Boundary With Other Subsystems

Asset Registry owns scene asset identity.

Semantic World System owns anchor definitions per scene.

Actor System can request where an actor should stand by anchor reference.

Intent System can map intents to preferred anchors later.

Runtime DSL can carry anchor references later.

Timeline Engine can execute movement between anchors later.

Camera Director can use anchors for framing later.

Renderer can consume resolved transforms later.

No Compiler, AI, UI, Timeline, Camera Director, or Renderer behavior is
implemented in this subsystem.
