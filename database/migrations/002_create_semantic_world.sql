BEGIN;

CREATE TABLE IF NOT EXISTS semantic_worlds (
    scene_asset_id TEXT PRIMARY KEY REFERENCES assets(id) ON DELETE CASCADE,
    version TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT semantic_worlds_scene_asset_id_chk
        CHECK (scene_asset_id LIKE 'scene_%'),
    CONSTRAINT semantic_worlds_version_format_chk
        CHECK (version ~ '^[0-9]+\.[0-9]+\.[0-9]+$'),
    CONSTRAINT semantic_worlds_metadata_object_chk
        CHECK (jsonb_typeof(metadata) = 'object')
);

CREATE TABLE IF NOT EXISTS semantic_anchors (
    scene_asset_id TEXT NOT NULL REFERENCES semantic_worlds(scene_asset_id) ON DELETE CASCADE,
    anchor TEXT NOT NULL,
    display_name TEXT NOT NULL,
    tags TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (scene_asset_id, anchor),

    CONSTRAINT semantic_anchors_anchor_format_chk
        CHECK (anchor ~ '^[a-z][a-z0-9_]*$'),
    CONSTRAINT semantic_anchors_display_name_not_blank_chk
        CHECK (length(trim(display_name)) > 0),
    CONSTRAINT semantic_anchors_metadata_object_chk
        CHECK (jsonb_typeof(metadata) = 'object')
);

CREATE INDEX IF NOT EXISTS semantic_anchors_scene_asset_id_idx
    ON semantic_anchors (scene_asset_id);

CREATE INDEX IF NOT EXISTS semantic_anchors_tags_gin_idx
    ON semantic_anchors USING GIN (tags);

CREATE INDEX IF NOT EXISTS semantic_anchors_metadata_gin_idx
    ON semantic_anchors USING GIN (metadata);

CREATE OR REPLACE FUNCTION set_semantic_worlds_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION set_semantic_anchors_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS semantic_worlds_set_updated_at ON semantic_worlds;
CREATE TRIGGER semantic_worlds_set_updated_at
BEFORE UPDATE ON semantic_worlds
FOR EACH ROW
EXECUTE FUNCTION set_semantic_worlds_updated_at();

DROP TRIGGER IF EXISTS semantic_anchors_set_updated_at ON semantic_anchors;
CREATE TRIGGER semantic_anchors_set_updated_at
BEFORE UPDATE ON semantic_anchors
FOR EACH ROW
EXECUTE FUNCTION set_semantic_anchors_updated_at();

COMMIT;
