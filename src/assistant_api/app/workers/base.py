"""Worker base abstractions.

Workers encapsulate CPU-intensive tasks such as TTS, STT, or LLM inference.
They are isolated from HTTP concerns and should not depend on FastAPI, request
objects, or transport-specific details. Workers also must avoid global state so
that they can be instantiated, restarted, and isolated safely.

This module intentionally avoids any execution model (threads, processes,
async). It only defines structural contracts for future worker implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseWorker(ABC):
    """Abstract base class for all worker implementations.

    Responsibilities:
        - Perform CPU-intensive or model inference tasks.
        - Provide a stable, isolated interface for the core orchestration layer.

    Must NOT:
        - Handle HTTP requests or reference web framework primitives.
        - Rely on global state or singletons for configuration or caching.
    """

    @classmethod
    @abstractmethod
    def worker_type(cls) -> str:
        """Return a unique string identifier for this worker type."""

    @abstractmethod
    def process(self, payload: Any) -> Any:
        """Process a unit of work and return a result.

        This is a placeholder for future execution models and should not embed
        scheduling, concurrency, or transport logic.
        """

    @abstractmethod
    def shutdown(self) -> None:
        """Release any resources owned by the worker instance."""
