INSERT INTO semantic_worlds (scene_asset_id, version, metadata)
VALUES (
    'scene_village_market_v1',
    '1.0.0',
    '{"default_anchor":"market_center","godot_anchor_group":"storyforge_anchor"}'
)
ON CONFLICT (scene_asset_id) DO NOTHING;

INSERT INTO semantic_anchors (scene_asset_id, anchor, display_name, tags, metadata)
VALUES
    (
        'scene_village_market_v1',
        'entrance',
        'Entrance',
        ARRAY['entry', 'navigation'],
        '{"description":"Primary entry point into the village market."}'
    ),
    (
        'scene_village_market_v1',
        'market_center',
        'Market Center',
        ARRAY['center', 'staging', 'public'],
        '{"description":"Main public staging area for market scenes."}'
    ),
    (
        'scene_village_market_v1',
        'stall_front',
        'Stall Front',
        ARRAY['commerce', 'interaction', 'staging'],
        '{"description":"Customer-facing side of a market stall."}'
    ),
    (
        'scene_village_market_v1',
        'stall_left',
        'Stall Left',
        ARRAY['commerce', 'side_position'],
        '{"description":"Left side of the primary market stall."}'
    ),
    (
        'scene_village_market_v1',
        'tree_area',
        'Tree Area',
        ARRAY['background', 'nature', 'staging'],
        '{"description":"Area near the village market tree."}'
    ),
    (
        'scene_village_market_v1',
        'buffalo_area',
        'Buffalo Area',
        ARRAY['background', 'animal_area', 'staging'],
        '{"description":"Area reserved for buffalo prop or background action."}'
    )
ON CONFLICT (scene_asset_id, anchor) DO NOTHING;
