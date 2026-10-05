"""Ingestion providers for threat stream."""
from .base import ThreatStreamProvider
from .mock_provider import MockStreamProvider

__all__ = ["ThreatStreamProvider", "MockStreamProvider"]
