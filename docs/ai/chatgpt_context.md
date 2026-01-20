# assistant-api — AI Project Context

This document provides context for assisting with the **assistant-api** project.

---

## 1. What this project is

**assistant-api** is a self-hosted Python backend service for voice assistants.

It provides a **minimal, OpenAI-compatible Text-to-Speech (TTS) API** with streaming audio output. The service is designed to run on Linux as a long-running service managed by `systemd`, inside a Python virtual environment.

---

## 2. Role of the satellite

The satellite is responsible for:

- Interacting with the user
- Calling LLM APIs and receiving streamed LLM output
- Sending text to the TTS endpoint
- Playing or forwarding the streamed audio output

The assistant-api server **does not orchestrate LLM → TTS internally**. The satellite explicitly controls when and how text is sent to TTS.

---

## 3. Current scope

### Implemented / in focus

- One-shot TTS via `POST /v1/audio/speech`
- Streaming audio output (chunked response)
- Audio pipeline: text → PCM → encoder → HTTP stream
- Output formats: `mp3` (default), `opus`, `pcm`
- Dummy TTS always available; Piper used when installed and configured
- Prewarm intent recording via `POST /v1/audio/prewarm`

### Future work

- Session-based / incremental TTS
- STT endpoints
- Expanded configuration and observability

---

## 4. Current architecture (high level)

- **FastAPI API layer** handles HTTP requests and streaming responses.
- **Worker implementations** run in-process and produce PCM data (dummy or Piper).
- **Encoders** convert PCM to the requested output format before streaming.

There is no separate worker process pool yet; current workers execute in the request path.

---

## 5. Streaming model

- PCM data is buffered in memory and read in chunks.
- Encoders stream audio as data becomes available.
- The HTTP response is a streaming response; it does not buffer full audio payloads.

---

## 6. API surface (current)

### TTS

- `POST /v1/audio/speech` — one-shot TTS, returns streaming audio

### Utilities

- `POST /v1/audio/prewarm` — records prewarm intent; Piper prewarm is best-effort

Session-based / incremental endpoints are not implemented yet.

---

## 7. Configuration model

- Configuration is YAML-based.
- System default path: `/etc/assistant-api/config.yaml`.
- Logging configuration currently supports a log directory override.

---

## 8. Repository conventions

- Python package lives under `src/assistant_api/`.
- Documentation lives under `docs/` (user, developer, and AI context).
- See `TODO.md` for current follow-ups.

---

## 9. Guardrails for AI-generated output

When generating code or documentation:

- Keep documentation aligned with current behavior.
- Avoid introducing feature claims that are not implemented.
- Prefer explicit, readable designs over clever abstractions.
