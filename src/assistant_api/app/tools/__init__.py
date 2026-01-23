"""Tooling infrastructure for authoritative data providers.

Tools provide deterministic, authoritative data to avoid LLM
hallucinations. The registry here is synchronous and minimal; wiring
tools into LLM requests is future work and intentionally not implemented
in this module.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable


ToolHandler = Callable[..., str]


@dataclass(frozen=True, slots=True)
class Tool:
    """Describe a synchronous tool that returns an authoritative string."""

    name: str
    description: str
    input_schema: dict
    handler: ToolHandler


@dataclass(slots=True)
class ToolRegistry:
    """Registry for tool definitions without automatic invocation."""

    _registry: dict[str, Tool] = field(default_factory=dict)

    def register(self, tool: Tool) -> None:
        """Register a tool by its name."""
        self._registry[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        """Return the tool registered for the given name."""
        return self._registry.get(name)

    def list_tools(self) -> tuple[Tool, ...]:
        """List the registered tools."""
        return tuple(self._registry.values())

    def run(self, name: str, **kwargs: object) -> str:
        """Execute a tool handler directly without any orchestration."""
        tool = self._registry[name]
        return tool.handler(**kwargs)


def get_current_time() -> str:
    """Return the current time in UTC as HH:MM:SSZ."""
    now = datetime.now(timezone.utc)
    return now.strftime("%H:%M:%SZ")


def get_current_date() -> str:
    """Return the current date in UTC as YYYY-MM-DD."""
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%d")


GET_CURRENT_TIME_TOOL = Tool(
    name="get_current_time",
    description="Return the current time in UTC as HH:MM:SSZ.",
    input_schema={},
    handler=get_current_time,
)

GET_CURRENT_DATE_TOOL = Tool(
    name="get_current_date",
    description="Return the current date in UTC as YYYY-MM-DD.",
    input_schema={},
    handler=get_current_date,
)


def build_tool_registry() -> ToolRegistry:
    """Create a registry populated with the default example tools."""
    registry = ToolRegistry()
    registry.register(GET_CURRENT_TIME_TOOL)
    registry.register(GET_CURRENT_DATE_TOOL)
    return registry


_TOOL_REGISTRY = build_tool_registry()


def get_tool_registry() -> ToolRegistry:
    """Return the shared tool registry instance."""
    return _TOOL_REGISTRY
