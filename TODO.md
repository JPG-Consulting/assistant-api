# TODO

Concrete follow-ups based on the current codebase.

## TTS

- Add a worker pool or background process manager so Piper inference runs outside
  the request handler and can be reused across requests.
- Implement voice/model selection so the `voice` field maps to specific Piper
  model files (currently `PIPER_MODEL_PATH` is the only model source).
- Expose structured error reporting for Piper load failures instead of silently
  falling back to dummy audio.

## Audio

- Add WAV output support and document how sample rate/channels are encoded.
- Replace the in-memory PCM buffer stream with a backpressure-aware async queue
  to avoid busy looping when no PCM chunks are available.
- Add configuration for MP3/Opus encoder settings (bitrate, frame size).

## API parity

- Align `/v1/audio/speech` request fields with OpenAI TTS (e.g., `model`, `input`,
  and explicit `voice` validation) while preserving current minimal payload.
- Return richer response metadata (timings, selected model) in headers or JSON
  envelopes to match OpenAI-style responses.
- Document and implement consistent error codes/messages for unsupported formats
  and unavailable models.

## Ops/Config

- Move default prewarm resource IDs into configuration instead of hardcoding in
  `main.py`.
- Add configuration entries for Piper model paths and per-voice overrides.
- Expand logging configuration (rotation, levels per module) via settings.

## Testing

- Add unit tests for dummy and Piper workers, including PCM spec detection.
- Add encoder tests that validate streaming behavior for mp3/pcm/opus outputs.
- Add API tests that cover `/v1/audio/speech` and `/v1/audio/prewarm` responses.
