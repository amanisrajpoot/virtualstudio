"""Artifact Storage Layer."""

import os
from typing import Optional
from backend.models.render_queue import RenderArtifact

class ArtifactStorage:
    def __init__(self, storage_dir: str = "data/render_queue/artifacts"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        
    def save_artifact_metadata(self, artifact: RenderArtifact):
        # V1: Just mock saving to local store. We would actually save the file data.
        pass
