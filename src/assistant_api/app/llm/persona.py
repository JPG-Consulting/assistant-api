"""Persona definitions."""

BASE_PERSONA = "You are a helpful assistant."


def get_base_persona(enabled: bool) -> str | None:
    if not enabled:
        return None
    return BASE_PERSONA
