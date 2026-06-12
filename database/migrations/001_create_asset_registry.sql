BEGIN;

DO $$
BEGIN
    CREATE TYPE asset_type AS ENUM (
        'character',
        'scene',
        'prop',
        'animation',
        'voice',
        'camera',
        'intent'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS assets (
    id TEXT PRIMARY KEY,
    type asset_type NOT NULL,
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    path TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT assets_id_format_chk
        CHECK (id ~ '^[a-z][a-z0-9_]*_v[0-9]+$'),
    CONSTRAINT assets_version_format_chk
        CHECK (version ~ '^[0-9]+\.[0-9]+\.[0-9]+$'),
    CONSTRAINT assets_name_not_blank_chk
        CHECK (length(trim(name)) > 0),
    CONSTRAINT assets_metadata_object_chk
        CHECK (jsonb_typeof(metadata) = 'object'),
    CONSTRAINT assets_versioned_identity_uniq
        UNIQUE (type, name, version)
);

CREATE INDEX IF NOT EXISTS assets_type_idx ON assets (type);
CREATE INDEX IF NOT EXISTS assets_name_idx ON assets (name);
CREATE INDEX IF NOT EXISTS assets_metadata_gin_idx ON assets USING GIN (metadata);

CREATE OR REPLACE FUNCTION set_assets_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS assets_set_updated_at ON assets;
CREATE TRIGGER assets_set_updated_at
BEFORE UPDATE ON assets
FOR EACH ROW
EXECUTE FUNCTION set_assets_updated_at();

COMMIT;
