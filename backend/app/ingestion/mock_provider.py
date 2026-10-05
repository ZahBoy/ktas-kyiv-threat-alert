"""Mock Stream Provider for testing, demo, and evaluation in Agentic AI School."""
import json
import asyncio
from pathlib import Path
from typing import AsyncGenerator, Dict, Any, List, Optional
from .base import ThreatStreamProvider


class MockStreamProvider(ThreatStreamProvider):
    """Feeds synthetic or recorded Telegram messages with configurable playback delay."""

    def __init__(self, dataset_path: Optional[str] = None, interval_seconds: float = 0.5):
        self.interval_seconds = interval_seconds
        self.is_running = False
        
        if dataset_path:
            self.dataset_path = Path(dataset_path)
        else:
            # Look in standard simulator directory
            self.dataset_path = Path(__file__).resolve().parent.parent.parent.parent / "simulator" / "test_dataset.json"

    def load_dataset(self) -> List[Dict[str, Any]]:
        """Load messages from JSON dataset file."""
        if self.dataset_path.exists():
            with open(self.dataset_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    async def start(self) -> None:
        self.is_running = True

    async def stop(self) -> None:
        self.is_running = False

    async def stream_raw_messages(self) -> AsyncGenerator[Dict[str, Any], None]:
        dataset = self.load_dataset()
        for item in dataset:
            if not self.is_running:
                break
            if self.interval_seconds > 0:
                await asyncio.sleep(self.interval_seconds)
            yield {
                "text": item.get("text", ""),
                "channel": item.get("channel", "@mock_monitor"),
                "timestamp": item.get("timestamp_utc", 0),
                "expected_threat_type": item.get("expected_threat_type")
            }
