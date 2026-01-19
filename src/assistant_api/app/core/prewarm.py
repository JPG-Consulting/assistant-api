"""Prewarm infrastructure for resource initialization.

This module defines lightweight request and registry structures used to
record prewarm intents without performing any real model loading. The
intent is to provide a consistent API surface so future implementations
can plug in actual resource initialization logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class PrewarmRequest:
    """Describe a prewarm request for optional resources.

    The request is intentionally minimal so the shape can evolve as the
    prewarm pipeline matures.
    """

    resource_id: str | None = None
    language: str | None = None
    voice: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)


class PrewarmManager:
    """Registry for default and optional prewarm requests.

    This process-local manager records intent only and performs no
    loading; it stays intentionally simple for now.

    Default resources are intended to be loaded at application startup in
    the future, while optional resources are registered on demand.
    """

    def __init__(self, default_resources: Iterable[str] | None = None) -> None:
        self._default_resources = set(default_resources or [])
        self._optional_requests: list[PrewarmRequest] = []

    def register_default_resource(self, resource_id: str) -> None:
        """Register a resource intended for future startup prewarming."""
        self._default_resources.add(resource_id)

    def list_default_resources(self) -> tuple[str, ...]:
        """Return registered default resource identifiers."""
        return tuple(sorted(self._default_resources))

    def request_optional(self, request: PrewarmRequest) -> None:
        """Record an optional prewarm request without performing work."""
        self._optional_requests.append(request)

    def list_optional_requests(self) -> tuple[PrewarmRequest, ...]:
        """Return the recorded optional prewarm requests."""
        return tuple(self._optional_requests)


_PREWARM_MANAGER = PrewarmManager()


def get_prewarm_manager() -> PrewarmManager:
    """Return the shared prewarm manager instance."""
    return _PREWARM_MANAGER
