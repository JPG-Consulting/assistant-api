# Architecture Overview

This document describes the **current** architecture of assistant-api. It focuses on what exists today, not planned features.

---

## 1. Problem statement

assistant-api provides a minimal, OpenAI-compatible Text-to-Speech (TTS) API with streaming audio output. The current implementation prioritizes simple, predictable behavior over advanced orchestration.

---

## 2. High-level architecture (current)

The service is a single FastAPI application that handles HTTP requests and streams audio responses. TTS processing happens in-process via worker classes.

Key components:

- **API layer**: FastAPI routes under `/v1/audio/`.
- **Workers**: in-process TTS workers (dummy or Piper) that emit PCM data.
- **Encoders**: streaming encoders for `mp3`, `opus`, and `pcm` output.
- **Prewarm manager**: records optional prewarm intent for future use.

---

## 3. TTS endpoint flow

`POST /v1/audio/speech` executes the following steps:

1. Select a worker: Piper when available and configured, otherwise the dummy worker.
2. Generate PCM data from text.
3. Encode PCM to the requested format (`mp3` default, `opus`, or `pcm`).
4. Stream encoded chunks as the HTTP response.

The pipeline is:

```
Text → PCM → Encoder → HTTP stream
```

---

## 4. Streaming behavior

- PCM data is buffered in memory and read in chunks.
- Encoders stream output as PCM becomes available.
- Responses are streaming HTTP responses; full audio payloads are not buffered.

There is no worker pool or background process manager yet; workers execute within the request lifecycle.

---

## 5. Prewarm behavior

- `POST /v1/audio/prewarm` records a prewarm request in memory.
- Piper prewarm is best-effort and optional; it runs only when Piper is installed and configured.
- Default resource identifiers are registered at application startup.

---

## 6. Future work (not implemented)

The following are intentionally out of scope for current documentation and are not yet implemented:

- Session-based / incremental TTS
- Background worker pools or dedicated process management
- Expanded API parity beyond the current minimal TTS endpoints

Refer to `TODO.md` for the current backlog.
