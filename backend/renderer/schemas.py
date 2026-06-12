"""Schemas for the Renderer Adapter."""

from pydantic import BaseModel
from typing import Dict, Any

class ExportSettings(BaseModel):
    resolution: str = "1920x1080"
    fps: int = 24
    output_format: str = "mp4"

class RenderPackage(BaseModel):
    render_job_id: str
    asset_manifest: Dict[str, Any]
    timeline: Dict[str, Any]
    camera_track: Dict[str, Any]
    audio_assets: Dict[str, Any]
    export_settings: ExportSettings
