"""Event Store persists events to disk."""

import os
import json
from pathlib import Path
from typing import List
from .schemas import EventEnvelope

class EventStore:
    def __init__(self, base_dir: str = "data/events"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_correlation_dir(self, correlation_id: str) -> Path:
        corr_dir = self.base_dir / correlation_id
        corr_dir.mkdir(parents=True, exist_ok=True)
        return corr_dir

    def get_next_sequence_number(self, correlation_id: str) -> int:
        """Returns the next sequence number for a given correlation ID."""
        corr_dir = self._get_correlation_dir(correlation_id)
        existing_files = list(corr_dir.glob("*.json"))
        if not existing_files:
            return 1
            
        # Parse integers from filenames like "000001.json"
        seqs = []
        for f in existing_files:
            try:
                seqs.append(int(f.stem))
            except ValueError:
                pass
                
        return max(seqs) + 1 if seqs else 1

    def save_event(self, event: EventEnvelope) -> None:
        """Persists an event to disk."""
        corr_dir = self._get_correlation_dir(event.correlation_id)
        
        # E.g., 000001.json
        filename = f"{event.sequence_number:06d}.json"
        filepath = corr_dir / filename
        
        # model_dump_json handles datetime serialization
        with open(filepath, "w") as f:
            f.write(event.model_dump_json(indent=2))

    def load_events(self, correlation_id: str) -> List[EventEnvelope]:
        """Loads all events for a correlation ID, sorted by sequence number."""
        corr_dir = self.base_dir / correlation_id
        if not corr_dir.exists():
            return []
            
        files = list(corr_dir.glob("*.json"))
        # Sort files by sequence number
        files.sort(key=lambda x: int(x.stem))
        
        events = []
        for f in files:
            with open(f, "r") as file:
                data = json.load(file)
                events.append(EventEnvelope(**data))
                
        return events
