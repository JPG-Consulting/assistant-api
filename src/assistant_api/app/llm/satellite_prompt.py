"""Satellite prompt helpers."""

from __future__ import annotations


FORBIDDEN_PHRASES = (
    "ignore previous instructions",
    "you are now",
    "system prompt",
    "override instructions",
)


def sanitize_satellite_prompt(prompt: str | None) -> str | None:
    if not prompt:
        return None
    lowered = prompt.lower()
    if any(phrase in lowered for phrase in FORBIDDEN_PHRASES):
        return None
    sanitized = " ".join(prompt.strip().split())
    return sanitized or None
