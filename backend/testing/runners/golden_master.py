"""Golden Master Engine for tracking and verifying JSON pipeline outputs."""

import os
import json
from pathlib import Path
from typing import Dict, Any

class GoldenMasterEngine:
    def __init__(self, goldens_dir: str = "backend/testing/goldens"):
        self.goldens_dir = Path(goldens_dir)
        self.goldens_dir.mkdir(parents=True, exist_ok=True)

    def _filter_volatile_data(self, data: Any) -> Any:
        """Removes non-deterministic fields like generated dialogue text, audio paths, UUIDs, timestamps."""
        if isinstance(data, dict):
            filtered = {}
            for k, v in data.items():
                if k in ["text", "audio_path", "duration", "event_id", "timestamp", "sequence_number", "correlation_id"]:
                    filtered[k] = "<FILTERED>"
                else:
                    filtered[k] = self._filter_volatile_data(v)
            return filtered
        elif isinstance(data, list):
            return [self._filter_volatile_data(i) for i in data]
        elif hasattr(data, "model_dump"):
            return self._filter_volatile_data(data.model_dump())
        else:
            return data

    def capture_and_compare(self, scenario_id: str, pipeline_output: Dict[str, Any], update_goldens: bool = False) -> bool:
        """
        Compares pipeline output against the golden master.
        If update_goldens is True, saves it as the new golden master.
        Returns True if matched or updated, False if mismatched.
        """
        golden_file = self.goldens_dir / f"{scenario_id}.json"
        
        # Strip volatile fields
        filtered_output = self._filter_volatile_data(pipeline_output)
        
        if update_goldens or not golden_file.exists():
            with open(golden_file, "w") as f:
                json.dump(filtered_output, f, indent=2)
            print(f"[GoldenMaster] Updated golden for {scenario_id}")
            return True
            
        with open(golden_file, "r") as f:
            golden_data = json.load(f)
            
        if golden_data != filtered_output:
            print(f"[GoldenMaster] MISMATCH detected for {scenario_id}")
            # Could implement deep diffing here for better debugging output
            return False
            
        return True
