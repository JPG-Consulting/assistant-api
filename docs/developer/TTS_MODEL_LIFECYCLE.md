# TTS Model Lifecycle (Design Contract)

## 1. Scope and intent

This document defines the **design contract** for TTS voice model lifecycle behavior in
assistant-api, including:

- how TTS models are loaded and unloaded
- what clients and AI agents may assume
- what is explicitly **not** guaranteed

This is a normative contract for behavior and assumptions. It is not an implementation
note and must be treated as authoritative by both humans and AI assistants.

## 2. Default vs non-default models

### Default model

- Defined by `tts.default_model` in config
- Must exist at startup
- Considered long-lived
- May be prewarmed
- Expected to remain available for the lifetime of the process

### Non-default (requested) models

- Requested via the `voice` field in API requests
- Optional and best-effort
- Not guaranteed to remain loaded
- May be unloaded at any time

## 3. Single-model invariant

> At any time, a Piper TTS worker maintains at most one loaded voice model.

Implications:

- Switching voices replaces the previously loaded model
- No multi-model cache exists
- This is intentional to keep memory and behavior predictable

### Piper AudioChunk PCM contract

- Piper's Python API (`piper-tts >= 1.3.0`) emits `AudioChunk` results.
- `AudioChunk.audio_int16_bytes` is already signed 16-bit little-endian PCM that
  matches the assistant-api PCM contract.
- assistant-api performs no resampling, float conversion, or normalization for
  this output.

## 4. Prewarm semantics

- Prewarm requests are **hints**, not guarantees
- Prewarm may load a model, but is not required to
- Prewarm does not imply persistence or reservation

Prewarm does not override any lifecycle rules above.

## 5. Model unloading and lifetime

- The system makes **no guarantees** about how long a non-default model remains loaded
- Models may be unloaded:
  - after a request
  - when another voice is requested
  - due to internal implementation changes

No additional guarantees (such as TTL, LRU, or other eviction policies) are implied
beyond this contract.

## 6. Explicit non-responsibilities

assistant-api:

- does **not** download models
- does **not** manage model persistence
- does **not** implement eviction policies beyond the current process
- assumes model files already exist on disk

## 7. Implications for clients and AI agents

- Clients must not assume a requested voice remains available
- Clients should treat `voice` as advisory, not stateful
- AI assistants must not introduce hidden caching or orchestration

## Cross-references

- Developer overview: `docs/developer/README.md`
- Agent responsibilities: `AGENTS.md`
