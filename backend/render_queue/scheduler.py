"""Render Scheduler."""

from typing import Optional
from backend.render_queue.queue import RenderQueue
from backend.render_queue.workers import WorkerRegistry
from backend.models.render_queue import RenderStatus

class RenderScheduler:
    def __init__(self, queue: RenderQueue, registry: WorkerRegistry):
        self.queue = queue
        self.registry = registry

    def schedule_jobs(self):
        # 1. Handle dead workers
        dead_workers = self.registry.get_dead_workers()
        for w_id in dead_workers:
            # Find any assigned jobs to this worker and trigger failure
            for job in self.queue.jobs:
                if job.worker_id == w_id and job.status not in [RenderStatus.COMPLETED, RenderStatus.FAILED]:
                    self.queue.handle_worker_failure(job.job_id)

        # 2. Assign pending jobs to active workers
        pending_jobs = self.queue.get_pending_jobs()
        active_workers = self.registry.get_active_workers()
        
        # Simple assignment: pick first worker with capacity (for mock, active_jobs == 0)
        available_workers = [w for w in active_workers if w.active_jobs == 0]
        
        for job in pending_jobs:
            if not available_workers:
                break # No more workers
            worker = available_workers.pop(0)
            self.queue.update_job_status(job.job_id, RenderStatus.ASSIGNED, worker.worker_id)
            worker.active_jobs += 1
