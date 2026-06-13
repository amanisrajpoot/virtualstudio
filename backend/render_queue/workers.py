"""Worker Registry and Heartbeat tracking."""

from typing import List, Dict
import datetime
from backend.models.render_queue import WorkerInfo, WorkerHeartbeat

class WorkerRegistry:
    def __init__(self):
        self.workers: Dict[str, WorkerInfo] = {}
        self.last_heartbeats: Dict[str, datetime.datetime] = {}
        
    def register_worker(self, worker_info: WorkerInfo):
        self.workers[worker_info.worker_id] = worker_info
        self.last_heartbeats[worker_info.worker_id] = datetime.datetime.now()
        
    def process_heartbeat(self, hb: WorkerHeartbeat):
        if hb.worker_id in self.workers:
            self.last_heartbeats[hb.worker_id] = datetime.datetime.fromisoformat(hb.timestamp)
            
    def get_active_workers(self, timeout_seconds: int = 60) -> List[WorkerInfo]:
        active = []
        now = datetime.datetime.now()
        for w_id, w_info in self.workers.items():
            last_hb = self.last_heartbeats.get(w_id)
            if last_hb and (now - last_hb).total_seconds() <= timeout_seconds:
                active.append(w_info)
        return active
        
    def get_dead_workers(self, timeout_seconds: int = 60) -> List[str]:
        dead = []
        now = datetime.datetime.now()
        for w_id in self.workers.keys():
            last_hb = self.last_heartbeats.get(w_id)
            if last_hb and (now - last_hb).total_seconds() > timeout_seconds:
                dead.append(w_id)
        return dead
