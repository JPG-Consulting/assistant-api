# assistant-api — ChatGPT Project Context

This document provides the complete context for assisting with the **assistant-api** project.

It is intended to be attached as a single file when starting a new ChatGPT (or Codex-like) conversation, so the assistant can understand the project goals, architecture, constraints, and conventions without additional explanation.

---

## 1. What this project is

**assistant-api** is a self-hosted Python backend service for voice assistants.

It provides an **OpenAI-compatible API**, with the current focus on **Text-to-Speech (TTS)**. The system is designed to run on Linux as a long-running service managed by `systemd`, inside a Python virtual environment.

The service is meant to be consumed by multiple independent clients (“satellites”), such as voice assistant frontends.

---

## 2. Role of the satellite

The satellite is responsible for:

- Interacting with the user
- Calling LLM APIs and receiving streamed LLM output
- Sending text (optionally incrementally) to the TTS endpoints
- Playing or forwarding the streamed audio output

The assistant-api server **does not orchestrate LLM → TTS internally**. The satellite explicitly controls when and how text is sent to TTS.

---

## 3. Current scope

### Implemented / in focus

- Text-to-Speech (TTS)
- Streaming audio output (chunked responses)
- Incremental speech synthesis via sessions
- OpenAI-compatible audio output formats
- Model pre-warm support

### Planned (future)

- Speech-to-Text (STT)
- LLM routing / gateway endpoints
- Shared session and streaming patterns across services

### Explicit non-goals (for now)

- Business logic or assistant behavior
- Internal LLM orchestration
- UI or frontend components

---

## 4. Core architectural principles

These rules are **non-negotiable** and must be respected by all code and documentation.

### 4.1 Layered architecture

The system is strictly layered:

```
API layer  →  Core orchestration  →  Workers  →  Engines
```

- **API layer**
  - FastAPI
  - Async and non-blocking
  - Handles HTTP, validation, and streaming responses only

- **Core**
  - Session management
  - Routing and scheduling
  - Stream abstractions
  - No HTTP-specific logic

- **Workers**
  - Run in separate processes
  - Perform CPU-heavy tasks (TTS, encoding, future STT/LLM)
  - Never interact with HTTP directly

- **Engines**
  - Model wrappers (e.g. Piper)
  - Low-level audio generation

### 4.2 Concurrency model

- The API must remain responsive under high concurrency.
- Multiple clients must be able to stream audio simultaneously.
- New requests must be accepted while other requests are actively streaming audio.
- Worker processes must not block the asyncio event loop.

### 4.3 Streaming model

- Audio is streamed using async queues (producer/consumer model).
- Each request or session owns its own audio stream.
- Backpressure must be handled safely.
- No request should require buffering the entire audio output in memory.

---

## 5. Text-to-Speech model

### 5.1 Audio pipeline

The audio pipeline is always:

```
Text → TTS engine → PCM chunks → Encoder → Client stream
```

Key rules:

- TTS engines always produce **PCM audio**
- Encoding (MP3 / Opus / etc.) is a separate step
- Encoding should be stream-oriented when possible

### 5.2 Output formats (OpenAI-compatible)

Supported formats:

- **mp3** (default)
- **opus** (in Ogg container)
- **pcm16** (raw signed 16-bit little-endian PCM)
- **wav**

The default output format is **MP3**.

### 5.3 Incremental speech synthesis

Incremental speech is session-based:

- A session is created first
- The satellite appends text chunks as they arrive from the LLM
- Audio is streamed continuously from the session
- The session is explicitly closed or cancelled

The server does not infer sentence boundaries on its own; the satellite controls when text is flushed.

---

## 6. API surface (high-level)

### TTS

- `POST /v1/audio/speech`  
  One-shot TTS, returns streaming audio

### Incremental TTS

- `POST /v1/audio/speech/sessions`
- `GET  /v1/audio/speech/sessions/{session_id}/audio`
- `POST /v1/audio/speech/sessions/{session_id}/append`
- `POST /v1/audio/speech/sessions/{session_id}/close`
- `POST /v1/audio/speech/sessions/{session_id}/cancel`

### Utilities

- `POST /v1/audio/prewarm`

Exact request/response schemas are defined elsewhere; this document describes intent, not wire details.

---

## 7. Configuration model

- Configuration is YAML-based.
- System default path: `/etc/assistant-api/config.yaml`
- Reasonable defaults must exist for all settings.

Logging:

- Log directory is configurable in YAML
- Fallback log directory: `/var/log/assistant-api`

---

## 8. Repository conventions

- Python package lives under `src/assistant_api/`
- Tests live under `tests/`
- Example systemd files live under `config/systemd/`
- Documentation is split into:
  - `docs/user/`
  - `docs/developer/`
  - `docs/ai/`

---

## 9. Guardrails for AI-generated output

When generating code or documentation:

- Respect the layered architecture.
- Do not introduce blocking operations in the API layer.
- Do not merge worker logic into HTTP routes.
- Avoid global mutable state.
- Prefer explicit, readable designs over clever abstractions.
- Do not invent features or requirements not described here.

If a design choice is unclear, ask for clarification rather than guessing.

---

## 10. How to use this document

This file is meant to be:

- Attached to a new ChatGPT conversation
- Used as the single source of truth for project context
- Updated when architectural decisions change

End of context.
