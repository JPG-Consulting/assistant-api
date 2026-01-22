"""Ollama provider."""

from __future__ import annotations

from typing import Any

import requests


class OllamaError(RuntimeError):
    """Raised when the Ollama API returns an error."""


def chat(
    *,
    model: str,
    host: str,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
) -> str:
    url = f"{host.rstrip('/')}/api/chat"
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        },
    }
    try:
        response = requests.post(url, json=payload, timeout=60)
    except requests.RequestException as exc:
        raise OllamaError(f"Ollama request failed: {exc}") from exc
    if response.status_code != 200:
        raise OllamaError(
            f"Ollama request failed with status {response.status_code}: {response.text}"
        )
    try:
        data: dict[str, Any] = response.json()
    except ValueError as exc:
        raise OllamaError("Ollama response was not valid JSON.") from exc
    message = data.get("message")
    if not isinstance(message, dict):
        raise OllamaError("Ollama response missing message payload.")
    content = message.get("content")
    if not isinstance(content, str):
        raise OllamaError("Ollama response message content was invalid.")
    return content
