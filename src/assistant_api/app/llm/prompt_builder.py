"""Prompt builder for LLM requests."""

from __future__ import annotations

from collections.abc import Iterable

Message = dict[str, str]


def build_prompt(
    *,
    base_persona: str | None,
    satellite_prompt: str | None,
    history: Iterable[Message],
    user_message: str,
) -> list[Message]:
    messages: list[Message] = []

    if base_persona:
        messages.append({"role": "system", "content": base_persona})
    if satellite_prompt:
        messages.append({"role": "system", "content": satellite_prompt})

    for message in history:
        content = message.get("content")
        role = message.get("role")
        if not content or not role:
            continue
        messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": user_message})
    return messages
