"""Verification Tests for Subsystem 29 (Render Control Plane)."""

import os
import shutil
import datetime
import uuid
import time
from backend.models.render_queue import RenderJob, RenderStatus, WorkerInfo, WorkerHeartbeat
from backend.render_queue.queue import RenderQueue
from backend.render_queue.workers import WorkerRegistry
from backend.render_queue.scheduler import RenderScheduler

def test_render_queue():
    test_dir = "data/test_render_dir"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
        
    queue = RenderQueue(data_dir=test_dir)
    registry = WorkerRegistry()
    scheduler = RenderScheduler(queue, registry)
    
    # Test 1 & 8: Submission & Priority Ordering
    j1 = RenderJob(
        job_id="job_1", project_id="p1", snapshot_version=1,
        approval_status="approved", status=RenderStatus.QUEUED,
        submitted_by="u1", submitted_at=datetime.datetime.now().isoformat(),
        priority=1
    )
    time.sleep(0.01)
    j10 = RenderJob(
        job_id="job_10", project_id="p1", snapshot_version=1,
        approval_status="approved", status=RenderStatus.QUEUED,
        submitted_by="u1", submitted_at=datetime.datetime.now().isoformat(),
        priority=10
    )
    time.sleep(0.01)
    j5 = RenderJob(
        job_id="job_5", project_id="p1", snapshot_version=1,
        approval_status="approved", status=RenderStatus.QUEUED,
        submitted_by="u1", submitted_at=datetime.datetime.now().isoformat(),
        priority=5
    )
    
    queue.submit_job(j1)
    queue.submit_job(j10)
    queue.submit_job(j5)
    
    pending = queue.get_pending_jobs()
    assert pending[0].job_id == "job_10"
    assert pending[1].job_id == "job_5"
    assert pending[2].job_id == "job_1"
    print("Test 1 & 8 (Queue Submission & Priority Ordering) passed.")
    
    # Test 2 & 3: Worker Registry & Assignment
    worker = WorkerInfo(worker_id="w_001", status="idle", active_jobs=0, capabilities=["1080p"])
    registry.register_worker(worker)
    
    hb = WorkerHeartbeat(worker_id="w_001", timestamp=datetime.datetime.now().isoformat(), cpu_usage=0.1, memory_usage=0.2)
    registry.process_heartbeat(hb)
    
    scheduler.schedule_jobs()
    
    # Highest priority should be ASSIGNED
    assert queue.jobs[1].job_id == "job_10"
    assert queue.jobs[1].status == RenderStatus.ASSIGNED
    assert queue.jobs[1].worker_id == "w_001"
    
    # Ensure worker active_jobs updated
    assert worker.active_jobs == 1
    print("Test 2 & 3 (Worker Heartbeat & Job Assignment) passed.")
    
    # Test 5 & 7: Worker Failure & Retry Exhaustion
    # Simulate worker death (heartbeat old)
    hb_old = datetime.datetime.now() - datetime.timedelta(seconds=100)
    registry.last_heartbeats["w_001"] = hb_old
    
    scheduler.schedule_jobs() # Scheduler discovers dead worker, requeues job
    
    # job_10 should be back to QUEUED, retry_count = 1
    j10_updated = next(j for j in queue.jobs if j.job_id == "job_10")
    assert j10_updated.status == RenderStatus.QUEUED
    assert j10_updated.retry_count == 1
    assert j10_updated.worker_id is None
    
    # Re-assign and fail until max retries
    registry.last_heartbeats["w_001"] = datetime.datetime.now() # resurrect worker
    worker.active_jobs = 0 # reset capacity
    scheduler.schedule_jobs() # Assigned again
    
    registry.last_heartbeats["w_001"] = datetime.datetime.now() - datetime.timedelta(seconds=100) # die again
    scheduler.schedule_jobs() # Requeued, retry=2
    
    registry.last_heartbeats["w_001"] = datetime.datetime.now() # resurrect
    worker.active_jobs = 0
    scheduler.schedule_jobs() # Assigned
    
    registry.last_heartbeats["w_001"] = datetime.datetime.now() - datetime.timedelta(seconds=100) # die again
    scheduler.schedule_jobs() # Failed, retry=3
    
    j10_final = next(j for j in queue.jobs if j.job_id == "job_10")
    assert j10_final.status == RenderStatus.FAILED
    assert j10_final.retry_count == 3
    print("Test 5 & 7 (Worker Failure Recovery & Retry Exhaustion) passed.")
    
    # Test 9: Snapshot History
    hist_path = os.path.join(test_dir, "history", "job_10.jsonl")
    assert os.path.exists(hist_path)
    with open(hist_path, 'r') as f:
        lines = f.readlines()
        assert len(lines) >= 4 # Submited, assigned, failed/requeued multiple times
    print("Test 9 (Snapshot History Persistence) passed.")
    
    # Test 10: Queue Metrics
    queue.update_job_status("job_5", RenderStatus.COMPLETED) # Mock complete
    
    metrics = queue.get_metrics()
    assert metrics.queued_jobs == 1 # job_1
    assert metrics.failed_jobs == 1 # job_10
    assert metrics.completed_jobs == 1 # job_5
    assert metrics.active_jobs == 0
    print("Test 10 (Queue Metrics updated accurately) passed.")

if __name__ == "__main__":
    test_render_queue()
    print("All Render Queue tests passed!")
