# Tool Results (Planned)

This document describes the planned shape and handling of tool results.
It is documentation-only and does not describe implemented behavior.

## What is a tool_result?

A `tool_result` is a structured message produced by a satellite/client after it
executes a tool request. It carries authoritative output that can be provided to
a future LLM request.

assistant-api does not execute tools and does not produce tool results. The
satellite is responsible for running tools and emitting `tool_result` messages.

## Conceptual message shape

Tool results are expressed as explicit JSON messages. Example structure:

```json
{
  "role": "tool_result",
  "name": "<tool_name>",
  "content": "<authoritative result string or structured JSON>"
}
```

## Current boundaries

- No server-side tool execution.
- No automatic LLM re-invocation using tool results.
- No streaming interaction with tools yet.
- Tool results must be passed explicitly by satellites/clients.

## Planned use

A future LLM request may include tool result messages so the model can respond
with authoritative data. This orchestration is future work and is not implemented
in assistant-api today.
