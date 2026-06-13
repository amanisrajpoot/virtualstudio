"""Render Queue Repository."""

import os
import json
import datetime
from typing import List, Optional
from backend.models.render_queue import RenderJob, RenderJobSnapshot, RenderStatus, QueueMetrics

class RenderQueue:
    def __init__(self, data_dir: str = "data/render_queue"):
        self.data_dir = data_dir
        self.history_dir = os.path.join(data_dir, "history")
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.history_dir, exist_ok=True)
        self.jobs: List[RenderJob] = []
        self._load_jobs()

    def _get_jobs_path(self) -> str:
        return os.path.join(self.data_dir, "jobs.json")

    def _load_jobs(self):
        path = self._get_jobs_path()
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    self.jobs = [RenderJob(**x) for x in data]
            except Exception:
                self.jobs = []

    def _save_jobs(self):
        with open(self._get_jobs_path(), 'w') as f:
            json.dump([j.model_dump() for j in self.jobs], f, indent=2)

    def _save_snapshot(self, job: RenderJob):
        snap = RenderJobSnapshot(
            job_id=job.job_id,
            status=job.status,
            worker_id=job.worker_id,
            timestamp=datetime.datetime.now().isoformat()
        )
        # Append to job's history file
        hist_path = os.path.join(self.history_dir, f"{job.job_id}.jsonl")
        with open(hist_path, 'a') as f:
            f.write(json.dumps(snap.model_dump()) + "\n")

    def submit_job(self, job: RenderJob):
        self.jobs.append(job)
        self._save_jobs()
        self._save_snapshot(job)

    def update_job_status(self, job_id: str, status: RenderStatus, worker_id: Optional[str] = None):
        for j in self.jobs:
            if j.job_id == job_id:
                j.status = status
                if worker_id is not None:
                    j.worker_id = worker_id
                self._save_jobs()
                self._save_snapshot(j)
                return True
        return False
        
    def handle_worker_failure(self, job_id: str):
        for j in self.jobs:
            if j.job_id == job_id:
                j.retry_count += 1
                j.worker_id = None
                if j.retry_count >= j.max_retries:
                    j.status = RenderStatus.FAILED
                else:
                    j.status = RenderStatus.QUEUED
                self._save_jobs()
                self._save_snapshot(j)
                return True
        return False

    def get_pending_jobs(self) -> List[RenderJob]:
        # Priority DESC, submitted_at ASC
        pending = [j for j in self.jobs if j.status == RenderStatus.QUEUED]
        pending.sort(key=lambda j: (-j.priority, j.submitted_at))
        return pending

    def get_all_jobs(self) -> List[RenderJob]:
        return sorted(self.jobs, key=lambda j: (-j.priority, j.submitted_at))

    def get_metrics(self) -> QueueMetrics:
        queued = sum(1 for j in self.jobs if j.status == RenderStatus.QUEUED)
        active = sum(1 for j in self.jobs if j.status in [RenderStatus.ASSIGNED, RenderStatus.DOWNLOADING_ASSETS, RenderStatus.RENDERING, RenderStatus.UPLOADING])
        completed = sum(1 for j in self.jobs if j.status == RenderStatus.COMPLETED)
        failed = sum(1 for j in self.jobs if j.status == RenderStatus.FAILED)
        
        # average_render_ms mock for now
        return QueueMetrics(
            queued_jobs=queued,
            active_jobs=active,
            completed_jobs=completed,
            failed_jobs=failed,
            average_render_ms=0.0
        )
