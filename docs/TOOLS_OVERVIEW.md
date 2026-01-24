# Tools Overview

This document describes how tool requests are represented in assistant-api.
It documents the current, minimal behavior only.

## What is a tool in assistant-api?

A tool is an external capability that can provide authoritative data or perform an
action outside the model's knowledge. Tools exist to reduce hallucinations by
allowing a satellite to supply verified results when needed.

assistant-api does not execute tools. The backend only parses and exposes tool
request payloads. Execution is always the responsibility of the satellite or
client.

## Why tools exist

Tools allow clients to obtain authoritative information (for example, database
queries or device state) instead of relying on model guesses. The server does not
run tools or infer intent; it only passes along tool requests as structured data.

## Tool Request Protocol

Tool requests must be emitted as a single, strict JSON object. The payload must
be the entire assistant message (no surrounding text, markdown, or partial JSON).

Exact format:

```json
{
  "tool_request": {
    "name": "<tool_name>",
    "arguments": { ... }
  }
}
```

Rules:
- The JSON object above must be the entire assistant message.
- Partial JSON or embedded text is rejected.
- The backend only parses and exposes the request.
- Tool execution is performed by the satellite/client.
- Tool result messages are only honored when a tool request is pending.

## Current behavior and boundaries

- No tool execution happens server-side (by design).
- No automatic LLM re-invocation exists yet.
- This separation is intentional and phase-based; future orchestration is
  tracked as planned work.

## Tool results (future)

Tool requests and tool results are separate concepts. Tool requests describe
what a satellite should run, while tool results describe the authoritative
output returned by that satellite. See `docs/TOOL_RESULTS.md` for the planned
message shape and boundaries.

## End-to-end example flow

This section shows a complete tool interaction lifecycle, with responsibilities
explicitly separated between assistant-api and the satellite/client.

1. **User input → satellite/client**
   - The satellite/client receives user input and sends a chat request to
     assistant-api.
   - assistant-api forwards the request to the configured LLM (no tools executed).

2. **Assistant response → tool_request**
   - The LLM responds with a tool request payload.
   - assistant-api parses the tool request and returns it to the satellite.

   Example assistant response payload (entire message must be JSON):

   ```json
   {
     "tool_request": {
       "name": "lookup_weather",
       "arguments": {
         "city": "Lisbon"
       }
     }
   }
   ```

3. **Tool execution → satellite/client**
   - The satellite executes the tool and produces a `tool_result`.
   - assistant-api does not execute tools and does not re-invoke the LLM.

4. **Follow-up request → assistant-api**
   - The satellite sends a new chat request that includes the `tool_result`
     message and the next user message (if any).
   - assistant-api accepts the `tool_result` message and passes it through to the
     LLM prompt history without interpretation.

   Example follow-up request message:

   ```json
   {
     "role": "tool_result",
     "name": "lookup_weather",
     "content": "Lisbon is 18°C and clear."
   }
   ```

5. **Final assistant response → satellite/client**
   - The LLM uses the tool result to respond.
   - The satellite delivers the response to the user.

Current boundaries:
- assistant-api does NOT execute tools.
- assistant-api does NOT re-invoke the LLM automatically.
- assistant-api does NOT orchestrate multi-step tool loops.
- Tool execution and orchestration are entirely satellite-controlled.
- Orphan tool_result messages are ignored by design.
