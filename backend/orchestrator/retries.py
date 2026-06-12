"""Retry Manager for isolated subsystem replays."""

from typing import Dict

class RetryManager:
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        # correlation_id -> retry_count
        self.retry_counts: Dict[str, int] = {}

    def should_retry(self, correlation_id: str) -> bool:
        """Returns True if the subsystem can be retried, and increments the count."""
        count = self.retry_counts.get(correlation_id, 0)
        if count < self.max_retries:
            self.retry_counts[correlation_id] = count + 1
            return True
        return False

    def get_retry_count(self, correlation_id: str) -> int:
        return self.retry_counts.get(correlation_id, 0)

    def reset(self, correlation_id: str):
        if correlation_id in self.retry_counts:
            del self.retry_counts[correlation_id]
