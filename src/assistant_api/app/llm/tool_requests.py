"""Utilities for parsing explicit tool request payloads.

This module defines a strict, protocol-only parser. Tool execution and orchestration
are intentionally out of scope for now.
"""

from __future__ import annotations

import json
from typing import TypedDict


class ToolRequest(TypedDict):
    name: str
    arguments: dict[str, object]


def try_parse_tool_request(text: str) -> ToolRequest | None:
    """Parse a strict tool request JSON payload.

    The parser is intentionally strict to avoid false positives. It only accepts
    a JSON object with a single top-level key named "tool_request".
    """
    if text is None:
        return None

    try:
        parsed = json.loads(text.strip())
    except json.JSONDecodeError:
        return None

    if not isinstance(parsed, dict):
        return None

    if set(parsed.keys()) != {"tool_request"}:
        return None

    tool_request = parsed.get("tool_request")
    if not isinstance(tool_request, dict):
        return None

    if set(tool_request.keys()) not in ({"name"}, {"name", "arguments"}):
        return None

    name = tool_request.get("name")
    if not isinstance(name, str) or not name.strip():
        return None

    if "arguments" in tool_request:
        arguments = tool_request.get("arguments")
        if not isinstance(arguments, dict):
            return None
    else:
        arguments = {}

    return {
        "name": name,
        "arguments": arguments,
    }
