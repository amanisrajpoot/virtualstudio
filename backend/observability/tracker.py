"""Telemetry Tracker for StoryForge Observability."""

import json
import os
import time
from typing import List, Dict, Callable
from functools import wraps
from backend.observability.schemas import MetricSample, MetricAggregate, FailureEvent, CacheMetrics

class TelemetryTracker:
    def __init__(self, data_dir: str = "data/telemetry"):
        self.data_dir = data_dir
        self.events_file = os.path.join(data_dir, "events.jsonl")
        self.aggregates_file = os.path.join(data_dir, "aggregates.json")
        self.failures_file = os.path.join(data_dir, "failures.json")
        self.cache_metrics_file = os.path.join(data_dir, "cache_metrics.json")
        
        os.makedirs(data_dir, exist_ok=True)
        
        # In-memory history for fast aggregation in V1
        self._samples: Dict[str, List[float]] = {}
        self._load_aggregates()
    
    def _load_aggregates(self):
        # We don't strictly load samples from jsonl for V1 to keep memory bounded,
        # but in a real system we would read back a sliding window.
        if os.path.exists(self.aggregates_file):
            try:
                with open(self.aggregates_file, 'r') as f:
                    data = json.load(f)
                    # mock re-hydrating some state
            except:
                pass

    def record_latency(self, metric_name: str, value_ms: float):
        timestamp = time.time()
        sample = MetricSample(metric_name=metric_name, value=value_ms, timestamp=timestamp)
        
        # 1. Append to events.jsonl
        with open(self.events_file, 'a') as f:
            f.write(sample.model_dump_json() + "\n")
            
        # 2. Update memory & aggregates.json
        if metric_name not in self._samples:
            self._samples[metric_name] = []
        self._samples[metric_name].append(value_ms)
        
        self._update_aggregates()

    def record_failure(self, error_type: str, details: str):
        failures = self.get_failures()
        found = False
        for f in failures:
            if f.error_type == error_type and f.details == details:
                f.count += 1
                found = True
                break
        if not found:
            failures.append(FailureEvent(error_type=error_type, details=details, count=1))
            
        with open(self.failures_file, 'w') as f:
            json.dump([x.model_dump() for x in failures], f, indent=2)

    def record_cache(self, cache_name: str, hit: bool):
        metrics = self.get_cache_metrics()
        
        # Load raw counts (mocking proper storage for brevity)
        counts_file = os.path.join(self.data_dir, f"{cache_name}_counts.json")
        counts = {"hits": 0, "total": 0}
        if os.path.exists(counts_file):
            try:
                with open(counts_file, 'r') as f:
                    counts = json.load(f)
            except:
                pass
                
        counts["total"] += 1
        if hit:
            counts["hits"] += 1
            
        hit_rate = (counts["hits"] / counts["total"]) * 100
        
        with open(counts_file, 'w') as f:
            json.dump(counts, f)
            
        if cache_name == "preview":
            metrics.preview_cache_hit_rate = hit_rate
        elif cache_name == "audio":
            metrics.audio_cache_hit_rate = hit_rate
            
        with open(self.cache_metrics_file, 'w') as f:
            json.dump(metrics.model_dump(), f, indent=2)

    def _update_aggregates(self):
        aggregates = []
        for metric_name, values in self._samples.items():
            if not values:
                continue
            sorted_vals = sorted(values)
            count = len(sorted_vals)
            avg = sum(sorted_vals) / count
            
            p50_idx = int(count * 0.50)
            p95_idx = int(count * 0.95)
            p99_idx = int(count * 0.99)
            
            p50 = sorted_vals[p50_idx] if p50_idx < count else sorted_vals[-1]
            p95 = sorted_vals[p95_idx] if p95_idx < count else sorted_vals[-1]
            p99 = sorted_vals[p99_idx] if p99_idx < count else sorted_vals[-1]
            
            aggregates.append(MetricAggregate(
                metric_name=metric_name,
                avg=avg,
                p50=p50,
                p95=p95,
                p99=p99,
                count=count
            ))
            
        with open(self.aggregates_file, 'w') as f:
            json.dump([x.model_dump() for x in aggregates], f, indent=2)

    def get_aggregates(self) -> List[MetricAggregate]:
        if not os.path.exists(self.aggregates_file):
            return []
        with open(self.aggregates_file, 'r') as f:
            data = json.load(f)
            return [MetricAggregate(**x) for x in data]

    def get_failures(self) -> List[FailureEvent]:
        if not os.path.exists(self.failures_file):
            return []
        with open(self.failures_file, 'r') as f:
            data = json.load(f)
            return [FailureEvent(**x) for x in data]

    def get_cache_metrics(self) -> CacheMetrics:
        if not os.path.exists(self.cache_metrics_file):
            return CacheMetrics()
        with open(self.cache_metrics_file, 'r') as f:
            data = json.load(f)
            return CacheMetrics(**data)

def track_latency(metric_name: str, tracker: TelemetryTracker):
    """Decorator to automatically track function latency."""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            duration_ms = (time.time() - start) * 1000
            tracker.record_latency(metric_name, duration_ms)
            return result
        return wrapper
    return decorator

# Global singleton
telemetry = TelemetryTracker()
