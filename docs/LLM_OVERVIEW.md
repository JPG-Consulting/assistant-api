# LLM Overview (Planned)

This document describes the planned direction for adding Large Language Model (LLM) capabilities to assistant-api.

The LLM subsystem described here is not implemented yet.
All items in this document represent design intent only and are tracked as future work in TODO.md.

## Purpose

The long-term goal of assistant-api is to evolve from a Text-to-Speech (TTS) service into a more complete backend for voice and conversational assistants.

The planned LLM subsystem will be responsible for:
- Generating conversational responses
- Supporting multilingual interaction
- Enabling natural, human-like dialogue
- Integrating with TTS and future STT components

## High-level principles

The following principles guide the planned LLM design:
- Single evolving service:
  LLM functionality will be part of assistant-api, not a separate product.
- Explicit scope control:
  Only implemented behavior will be documented as such. Planned features remain future work.
- Low-latency focus:
  The system is intended to support real-time voice and embodied (e.g. humanoid robot) use cases.
- Multilingual by design:
  Although development and documentation are in English, the system is intended to work across multiple languages.

## Planned responsibilities

At a conceptual level, the LLM subsystem is expected to handle:
- Conversational text generation
- Short-term conversation context
- Language-aware responses
- Integration with other subsystems (e.g. TTS)

No guarantees are made about the exact architecture or APIs at this stage.

## Satellites and clients (conceptual)

The system is intended to support multiple types of clients ("satellites"), such as:
- Embedded devices
- Voice assistants
- Robots
- Future graphical interfaces

Satellites may influence how the assistant behaves (for example tone or verbosity), but not who the assistant is.
The core identity and behavior remain server-controlled.

## Persona and behavior (conceptual)

The planned LLM subsystem includes the concept of a base system persona:
- A stable identity and behavior profile
- Designed to produce consistent, human-like interaction
- Applied by default at the server level

This persona may be configurable or disabled via configuration, but such behavior is future work.

## Prompt orchestration decision (LLM endpoint)

During early LLM endpoint development, the project attempted to control assistant behavior
(language selection, response style, anti-parroting rules) by injecting multiple system prompts
from backend code. This caused unstable behavior across local models (Mistral, Llama), including:

- Input parroting
- Random language switching
- Over-generic or low-value replies
- Conflicting or contradictory system instructions

The decision is to keep prompt orchestration intentionally simple and model-agnostic:

This decision applies regardless of the specific local LLM used (for example Mistral, Llama, or future models).

- The base persona in `config/persona.txt` is the single source of truth for assistant behavior.
- Backend code must not enforce language, response style, or conversational rules.
- The backend acts as a neutral message router, not a conversational agent.
- Language handling is natural: reply in the user's language, and only translate or switch languages
  when explicitly requested.
- Over-prompting and heuristic prompt injection are avoided to improve stability across models.

Implementation outcome for the LLM endpoint:

- Only one system prompt is used for assistant behavior: the persona.
- Optional satellite-supplied system prompts may exist but must be sanitized and minimal.
- No additional system instructions (language forcing, response mode, anti-parroting) are injected
  by the backend.

## Intent detection (conceptual)

A future intent-detection layer may be introduced to:
- Classify user inputs
- Enable fast handling of simple commands
- Route requests appropriately

Any such system will be documented once implemented.

## Conversation context (conceptual)

Future versions may support limited conversation context to enable more natural dialogue.

The exact storage, retention, and lifecycle rules are not defined yet and remain future work.

## Relationship to TODO.md

All implementation tasks related to the LLM subsystem are intentionally tracked in TODO.md.

This document exists to describe direction and intent, not execution.

## Status

- Current state: LLM functionality is not implemented.
- Next steps: See TODO.md for planned work and phases.
