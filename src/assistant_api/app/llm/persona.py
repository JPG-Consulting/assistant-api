"""Persona definitions."""

from __future__ import annotations

from assistant_api.app.settings import PersonaSettings


def get_base_persona(settings: PersonaSettings) -> str | None:
    if not settings.enabled:
        return None
    return settings.content
