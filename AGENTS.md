# AGENTS

This document defines the **roles, responsibilities, and boundaries** of the different
actors interacting with the `assistant-api` project.

It applies to:
- Human developers
- AI assistants (ChatGPT, Codex, similar tools)
- External client applications (“satellites”)

The goal is to avoid ambiguity, scope creep, and incorrect assumptions about what each
agent is responsible for.

---

## 1. assistant-api (this project)

### Role

`assistant-api` is a **backend service** that exposes a **minimal, OpenAI-compatible
Text-to-Speech (TTS) API** with streaming audio output.

It is responsible for:
- Receiving text input over HTTP
- Generating audio via TTS workers
- Streaming encoded audio to clients
- Managing lightweight operational concerns (logging, prewarm intent)

### Non-responsibilities

`assistant-api` does **not**:
- Orchestrate LLM calls
- Decide *what* should be spoken
- Manage conversational state
- Perform business logic
- Provide a user interface

It is intentionally narrow in scope.

---

## 2. Satellites (client applications)

### Role

A **satellite** is any external client consuming `assistant-api`, such as:
- Voice assistant frontends
- Desktop or mobile apps
- Embedded devices
- Other backend services

Satellites are responsible for:
- Interacting with end users
- Calling LLM APIs (if any)
- Deciding *when* and *what* text to send to TTS
- Playing, forwarding, or storing streamed audio

### Key rule

> The satellite controls the flow.  
> The server does not infer intent, pacing, or structure.

---

## 3. TTS Workers

### Role

Workers perform the actual text-to-speech computation.

Current workers:
- **Dummy TTS worker** (always available, deterministic)
- **Piper TTS worker** (used when installed and configured)

Workers:
- Accept text input
- Produce raw PCM audio
- Do not interact with HTTP
- Do not manage sessions or clients

Workers may evolve, but their interface must remain explicit and predictable.

---

## 4. Encoders

### Role

Encoders convert **PCM audio** into client-facing formats.

Current formats:
- `mp3` (default)
- `opus` (Ogg Opus)
- `pcm` (raw PCM)

Encoders:
- Are format-specific
- Are stream-oriented
- Do not perform TTS or text processing

---

## 5. Prewarm system

### Role

The prewarm system:
- Records *intent* to preload resources
- Optionally performs best-effort preloading (e.g. Piper model load)

Prewarm behavior is:
- Non-blocking
- Best-effort
- Not required for correctness

Failure to prewarm must never break TTS requests.

---

## 6. AI assistants (ChatGPT, Codex, etc.)

### Role

AI assistants may be used to:
- Generate code
- Update documentation
- Propose refactors
- Help debug issues

### Constraints

AI assistants **must**:
- Reflect current behavior, not planned features
- Avoid inventing APIs or capabilities
- Avoid architectural rewrites unless explicitly requested
- Prefer minimal, incremental changes

### Source of truth

When generating output, AI assistants should treat the following as authoritative:
1. The current code
2. `README.md`
3. `docs/`
4. `TODO.md`
5. This `AGENTS.md`

If something is unclear, the correct action is to **ask**, not assume.

---

## 7. Guardrails

To keep the project stable and understandable:

- No hidden orchestration
- No implicit behavior
- No “magic” defaults
- No undocumented background processes
- No claims of features that do not exist

Simplicity and correctness take priority over completeness.

---

## 8. Evolution

This file **must be updated** when:
- A new type of agent is introduced
- Responsibilities shift between components
- The scope of the project changes

If an agent’s role is unclear, it should be clarified here before code is written.

---

End of document.
