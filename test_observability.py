"""Verification Tests for Subsystem 23 (StoryForge Observability)."""

import os
from backend.observability.tracker import TelemetryTracker
from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)

def test_metric_aggregation_and_percentiles():
    tracker = TelemetryTracker(data_dir="data/test_telemetry")
    
    # Test 4: Metric Aggregation
    tracker.record_latency("test_latency", 10.0)
    tracker.record_latency("test_latency", 20.0)
    tracker.record_latency("test_latency", 30.0)
    
    aggs = tracker.get_aggregates()
    test_agg = next(a for a in aggs if a.metric_name == "test_latency")
    assert test_agg.avg == 20.0
    
    print("Test 4 (Metric Aggregation) passed.")
    
    # Test 5: P95 Calculation
    for i in range(1, 101): # 1 to 100
        tracker.record_latency("percentile_test", float(i))
        
    aggs = tracker.get_aggregates()
    p_agg = next(a for a in aggs if a.metric_name == "percentile_test")
    
    assert p_agg.p50 >= 50.0
    assert p_agg.p95 >= 95.0
    assert p_agg.count == 100
    
    print("Test 5 (P95 Calculation) passed.")

def test_cache_metrics():
    # Test 6: Cache Metrics Hit Rate tracking
    tracker = TelemetryTracker(data_dir="data/test_telemetry")
    
    tracker.record_cache("audio", False) # 0% hit rate
    metrics = tracker.get_cache_metrics()
    assert metrics.audio_cache_hit_rate == 0.0
    
    tracker.record_cache("audio", True) # 50% hit rate
    metrics = tracker.get_cache_metrics()
    assert metrics.audio_cache_hit_rate == 50.0
    
    tracker.record_cache("audio", True) # 66.6% hit rate
    metrics = tracker.get_cache_metrics()
    assert metrics.audio_cache_hit_rate > 66.0
    
    print("Test 6 (Cache Metrics Hit Rate) passed.")

def test_health_breakdown():
    # Test 7: Health Breakdown logic (via API mock)
    response = client.get("/api/observability/health/123")
    assert response.status_code == 200
    data = response.json()
    
    assert "assets_score" in data
    assert "world_score" in data
    assert "final_score" in data
    assert "warnings" in data
    assert len(data["warnings"]) > 0
    
    print("Test 7 (Health Breakdown Evaluation) passed.")

if __name__ == "__main__":
    os.makedirs("data/test_telemetry", exist_ok=True)
    test_metric_aggregation_and_percentiles()
    test_cache_metrics()
    test_health_breakdown()
    print("All Observability tests passed!")
