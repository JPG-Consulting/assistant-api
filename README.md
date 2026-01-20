# assistant-api

assistant-api is a Python backend service for voice assistants. It currently exposes a minimal, OpenAI-compatible Text-to-Speech (TTS) API with streaming audio output, designed for Linux deployments as a systemd-managed service.

## Current behavior

- **One-shot TTS**: `POST /v1/audio/speech` streams audio for a single text payload.
- **Streaming pipeline**: text → PCM → encoder → HTTP stream.
- **Supported formats**: `mp3` (default), `opus`, `pcm`.
- **Engines**: the dummy TTS worker is always available; Piper is used when installed and configured.

## Prewarm behavior

- `POST /v1/audio/prewarm` records prewarm intent for audio resources.
- Piper prewarm is best-effort and optional; it only runs when Piper is available.

## Documentation

- User documentation: `docs/user/README.md`
- Developer documentation: `docs/developer/README.md`
- AI assistant context: `docs/ai/README.md`
- Backlog and follow-ups: `TODO.md`

## Status

The repository contains a working TTS endpoint with streaming audio output. Session-based or incremental TTS is future work; see `TODO.md` for follow-ups.
