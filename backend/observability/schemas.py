"""Observability schemas for StoryForge."""

from pydantic import BaseModel
from typing import List, Dict

class MetricSample(BaseModel):
    metric_name: str
    value: float
    timestamp: float

class MetricAggregate(BaseModel):
    metric_name: str
    avg: float = 0.0
    p50: float = 0.0
    p95: float = 0.0
    p99: float = 0.0
    count: int = 0

class StoryHealthBreakdown(BaseModel):
    assets_score: int = 100
    characters_score: int = 100
    world_score: int = 100
    timeline_score: int = 100
    dialogue_score: int = 100
    final_score: int = 100
    warnings: List[str] = []

class StoryTraceSummary(BaseModel):
    story_id: str
    total_time_ms: float
    slowest_stage: str
    failure_count: int

class CacheMetrics(BaseModel):
    preview_cache_hit_rate: float = 0.0
    audio_cache_hit_rate: float = 0.0

class FailureEvent(BaseModel):
    error_type: str
    details: str
    count: int = 1
