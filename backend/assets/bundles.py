"""Asset Bundles registry."""

# In a real app this is loaded from YAML/DB.
BUNDLES = {
    "market_core": [
        "market_scene",
        "market_stall",
        "market_ambient_audio"
    ],
    "police_kit": [
        "char_policeman_v1",
        "prop_baton"
    ]
}

def get_bundle_assets(bundle_id: str) -> list[str]:
    """Returns the list of assets contained in a bundle."""
    return BUNDLES.get(bundle_id, [])

def is_bundle(item_id: str) -> bool:
    return item_id in BUNDLES
