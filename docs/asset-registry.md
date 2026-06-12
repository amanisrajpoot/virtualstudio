# Asset Registry

Subsystem: 1

Status: implemented as contracts, database schema, backend module, seed data,
and Godot 4 integration helper.

## Purpose

The Asset Registry is the single source of truth for StoryForge assets.

It stores:

- Characters.
- Scenes.
- Props.
- Animations.
- Voices.
- Camera presets.
- Intent definitions.

This subsystem does not compile stories, choose cameras, run timelines, render
video, or provide UI. Later subsystems consume registry records.

## Folder Structure

```text
backend/
  asset_registry/
    __init__.py
    api.py
    constants.py
    repository.py
    schemas.py
    validation.py
database/
  migrations/
    001_create_asset_registry.sql
  seeds/
    001_asset_registry_v1.sql
schemas/
  asset_registry/
    asset.schema.json
    openapi.yaml
godot_runtime/
  addons/
    storyforge/
      asset_registry/
        asset_registry_client.gd
docs/
  asset-registry.md
```

## Database Schema

Canonical table: `assets`.

Columns:

- `id TEXT PRIMARY KEY`
- `type asset_type NOT NULL`
- `name TEXT NOT NULL`
- `version TEXT NOT NULL`
- `path TEXT`
- `metadata JSONB NOT NULL DEFAULT '{}'::jsonb`
- `created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`
- `updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`

Asset enum values:

- `character`
- `scene`
- `prop`
- `animation`
- `voice`
- `camera`
- `intent`

Database guarantees:

- IDs are lowercase snake_case and end in `_vN`.
- Versions use semantic format such as `1.0.0`.
- Metadata is always a JSON object.
- `(type, name, version)` is unique.
- `updated_at` is maintained by trigger.
- Metadata has a GIN index for discovery queries.

Migration:

```text
database/migrations/001_create_asset_registry.sql
```

Seed data:

```text
database/seeds/001_asset_registry_v1.sql
```

## Versioning Rules

Each registered asset row is immutable in identity:

- `id`
- `type`
- `version`

For a new asset version, create a new row with a new ID suffix and semantic
version, for example:

```text
char_halku_v1 -> 1.0.0
char_halku_v2 -> 2.0.0
```

Mutable fields:

- `name`
- `path`
- `metadata`

## ID Conventions

IDs must match:

```text
^[a-z][a-z0-9_]*_v[0-9]+$
```

Type prefixes:

| Type | Prefix | Example |
| --- | --- | --- |
| character | `char` | `char_halku_v1` |
| scene | `scene` | `scene_village_market_v1` |
| prop | `prop` | `prop_bottle_v1` |
| animation | `anim` | `anim_idle_v1` |
| voice | `voice` | `voice_stern_male_v1` |
| camera | `cam` | `cam_dialogue_v1` |
| intent | `intent` | `intent_question_v1` |

## Validation Rules

Backend validation enforces:

- Known asset type.
- ID format.
- ID prefix matching the asset type.
- ID version suffix matching semantic version major.
- Semantic version format.
- Non-empty name.
- Metadata object.
- Required path for resource-backed assets.
- Required metadata keys for logical assets.

Resource-backed types:

- `character`
- `scene`
- `prop`
- `animation`
- `voice`

Logical types:

- `camera`
- `intent`

Required logical metadata:

- Camera assets require `metadata.preset`.
- Intent assets require `metadata.description`.

## API Contracts

Full OpenAPI contract:

```text
schemas/asset_registry/openapi.yaml
```

Endpoints:

```text
GET    /assets
GET    /assets/{asset_id}
POST   /assets/validate
POST   /assets
PATCH  /assets/{asset_id}
DELETE /assets/{asset_id}
```

Discovery:

```http
GET /assets?type=character&q=halku&limit=100&offset=0
```

Register:

```json
{
  "id": "char_halku_v1",
  "type": "character",
  "name": "Halku",
  "version": "1.0.0",
  "path": "res://assets/characters/halku/halku.tscn",
  "metadata": {
    "role": "seller",
    "voice": "voice_cheerful_male_v1"
  }
}
```

Validate without persisting:

```http
POST /assets/validate
```

## Backend Integration

The FastAPI router is exposed as a factory:

```python
from backend.asset_registry.api import create_asset_registry_router
from backend.asset_registry.repository import AssetRepository

pool = ...

def repository_provider() -> AssetRepository:
    return AssetRepository(pool)

app.include_router(create_asset_registry_router(repository_provider))
```

The repository expects an `asyncpg`-compatible pool with `acquire()`, `fetch()`,
`fetchrow()`, and `execute()` methods.

## Godot 4 Integration

Godot client:

```text
godot_runtime/addons/storyforge/asset_registry/asset_registry_client.gd
```

The client uses `HTTPRequest` and exposes:

- `list_assets(asset_type, query, limit, offset)`
- `get_asset(asset_id)`
- `validate_asset(asset)`

Signals:

- `assets_listed(assets)`
- `asset_loaded(asset)`
- `asset_validated(result)`
- `request_failed(message, status_code)`

Example Godot usage:

```gdscript
var registry := StoryForgeAssetRegistryClient.new()
add_child(registry)
registry.base_url = "http://127.0.0.1:8000"
registry.assets_listed.connect(_on_assets_listed)
registry.list_assets("character", "halku")
```

The Godot helper is intentionally UI-free. Plugin UI comes later.

## Asset Discovery

Discovery is supported through:

- Type filtering.
- ID/name text search.
- Limit and offset pagination.
- Metadata JSONB indexing for later backend query extensions.

The current public API does not expose arbitrary metadata filtering yet. That
can be added once consuming subsystems define concrete discovery needs.

## Boundary With Future Subsystems

Semantic World System can attach anchors to scene metadata later, but this
subsystem does not define anchor behavior.

Intent System can expand intent metadata later, but this subsystem only stores
and validates intent definitions.

Camera Director can consume camera preset assets later, but this subsystem does
not choose cameras.

Renderer can resolve `res://` paths later, but this subsystem does not load or
render Godot resources.
