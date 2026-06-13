"""Project Runtime Repository."""

import json
import os
from typing import List, Optional
from backend.models.project import ProjectManifest, ProjectSnapshot

class ProjectRepository:
    def __init__(self, data_dir: str = "data/projects"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

    def _get_project_dir(self, project_id: str) -> str:
        return os.path.join(self.data_dir, project_id)

    def _get_manifest_path(self, project_id: str) -> str:
        return os.path.join(self._get_project_dir(project_id), "manifest.json")
        
    def _get_snapshot_dir(self, project_id: str) -> str:
        return os.path.join(self._get_project_dir(project_id), "snapshots")

    def save_manifest(self, manifest: ProjectManifest):
        pdir = self._get_project_dir(manifest.project_id)
        os.makedirs(pdir, exist_ok=True)
        os.makedirs(self._get_snapshot_dir(manifest.project_id), exist_ok=True)
        
        with open(self._get_manifest_path(manifest.project_id), 'w') as f:
            json.dump(manifest.model_dump(), f, indent=2)

    def get_manifest(self, project_id: str) -> Optional[ProjectManifest]:
        path = self._get_manifest_path(project_id)
        if not os.path.exists(path):
            return None
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                return ProjectManifest(**data)
        except Exception:
            return None

    def list_manifests(self) -> List[ProjectManifest]:
        manifests = []
        if not os.path.exists(self.data_dir):
            return manifests
            
        for d in os.listdir(self.data_dir):
            pdir = os.path.join(self.data_dir, d)
            if os.path.isdir(pdir):
                m = self.get_manifest(d)
                if m:
                    manifests.append(m)
        return manifests

    def save_snapshot(self, snapshot: ProjectSnapshot):
        sdir = self._get_snapshot_dir(snapshot.project_id)
        os.makedirs(sdir, exist_ok=True)
        path = os.path.join(sdir, f"v{snapshot.graph_version}.json")
        with open(path, 'w') as f:
            json.dump(snapshot.model_dump(), f, indent=2)

    def get_snapshot(self, project_id: str, version: int) -> Optional[ProjectSnapshot]:
        path = os.path.join(self._get_snapshot_dir(project_id), f"v{version}.json")
        if not os.path.exists(path):
            return None
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                return ProjectSnapshot(**data)
        except Exception:
            return None
