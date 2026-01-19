"""Worker registry and lookup utilities.

The manager provides a central place to register worker types without
instantiating or executing them. It is intentionally minimal and does not
schedule tasks, start workers, or manage concurrency.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Optional, Type

from .base import BaseWorker


@dataclass(slots=True)
class WorkerManager:
    """Registry for available worker types."""

    _registry: Dict[str, Type[BaseWorker]] = field(default_factory=dict)

    def register(self, worker_cls: Type[BaseWorker]) -> None:
        """Register a worker type by its declared identifier."""
        worker_type = worker_cls.worker_type()
        self._registry[worker_type] = worker_cls

    def get(self, worker_type: str) -> Optional[Type[BaseWorker]]:
        """Return the worker class registered for the given type."""
        return self._registry.get(worker_type)

    def list_types(self) -> Iterable[str]:
        """List the registered worker type identifiers."""
        return tuple(self._registry.keys())
