"""Abstract base class for threat stream ingestion providers."""
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any


class ThreatStreamProvider(ABC):
    """Interface for stream providers (Telegram TDLib, Telethon, or Mock)."""

    @abstractmethod
    async def start(self) -> None:
        """Initialize and connect the stream provider."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Disconnect and cleanup the stream provider."""
        pass

    @abstractmethod
    async def stream_raw_messages(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Asynchronously yield raw message dicts containing 'text', 'channel', and 'timestamp'."""
        pass
