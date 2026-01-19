# Architecture Overview

This document describes the architecture of **assistant-api**.
Its purpose is to explain *how the system is structured*, *why certain design decisions were made*, and *how the different parts fit together*.

This is not an implementation guide. It intentionally focuses on concepts, boundaries, and responsibilities.

---

## 1. Problem statement

assistant-api is a backend service designed to support voice assistants.

The core requirements are:

- High concurrency
- Low-latency audio streaming
- Incremental speech synthesis
- Clear separation of concerns
- Long-running, stable operation as a Linux system service

The system must be able to serve multiple independent clients (“satellites”) simultaneously, without blocking or global contention.

---

## 2. High-level architecture

assistant-api follows a **layered architecture**:

```
API layer  →  Core orchestration  →  Workers  →  Engines
```

Each layer has a clearly defined responsibility and must not leak concerns into adjacent layers.

---

## 3. API layer

### Responsibilities

The API layer is responsible for:

- Exposing an HTTP interface (FastAPI)
- Request validation
- Session lifecycle endpoints
- Streaming responses to clients
- Error handling at the HTTP boundary

### Constraints

- The API layer must be **fully asynchronous**
- It must **never perform CPU-heavy work**
- It must remain responsive while other requests are streaming audio
- It must not contain TTS, STT, or encoding logic

The API layer acts as an orchestrator and transport mechanism, not a processing engine.

---

## 4. Core orchestration layer

### Responsibilities

The core layer coordinates the system without being tied to HTTP.

Typical responsibilities include:

- Session management (creation, lookup, cleanup)
- Stream abstractions (e.g. audio streams)
- Routing jobs to workers
- Scheduling and resource limits
- Shared lifecycle logic

### Design intent

This layer exists to keep **business logic and orchestration separate from transport**.

Because it is HTTP-agnostic, it can be reused for:

- HTTP streaming
- WebSockets
- Other transport mechanisms in the future

---

## 5. Worker layer

### Responsibilities

Workers are responsible for:

- CPU-intensive tasks
- Model inference (TTS, future STT / LLM)
- Audio generation and encoding
- Managing model caches and pre-warm behavior

### Process model

- Workers run in **separate processes**
- They must not block the asyncio event loop
- Each worker handles multiple jobs sequentially or via internal task scheduling

### Constraints

- Workers must **never access HTTP primitives**
- Workers must communicate via explicit data structures or streams
- Workers must be restartable and isolated

---

## 6. Engine layer

### Responsibilities

Engines are the lowest-level components:

- Wrappers around concrete models (e.g. Piper)
- Direct interaction with inference libraries
- Raw data generation (e.g. PCM audio)

Engines do not know about:

- Sessions
- Streaming
- Clients
- HTTP
- Encoding formats

They are intentionally narrow in scope.

---

## 7. Concurrency model

assistant-api is designed to handle concurrency at multiple levels:

### 7.1 HTTP concurrency

- Multiple clients may have active streaming responses
- New requests must be accepted while others are streaming
- Backpressure must be handled gracefully

### 7.2 Worker concurrency

- Workers run in separate processes
- The number of workers is configurable
- Each worker may handle multiple sessions over time

### 7.3 Stream concurrency

- Each request or session owns its own audio stream
- Streams are independent and isolated
- Producers and consumers are decoupled via async queues

---

## 8. Streaming and sessions

### One-shot TTS

For simple use cases:

- A single request produces a single audio stream
- Audio is streamed as it is generated
- The request completes when the stream ends

### Incremental TTS (sessions)

For low-latency conversational use cases:

- A session is created explicitly
- The client appends text incrementally
- Audio is streamed continuously
- The session is explicitly closed or cancelled

The server does not infer conversational structure.
The satellite controls pacing and segmentation.

---

## 9. Audio pipeline

The audio pipeline is strictly defined:

```
Text
  ↓
TTS engine
  ↓
PCM audio chunks
  ↓
Encoder (MP3 / Opus / PCM / WAV)
  ↓
Client stream
```

### Key principles

- TTS engines always output PCM
- Encoding is a separate concern
- Encoding should support streaming
- The default output format is MP3 (OpenAI-compatible)

This separation allows:

- Easy addition of new formats
- Reuse of encoders across services
- Cleaner testing and debugging

---

## 10. Configuration and deployment

### Configuration

- Configuration is YAML-based
- Default system path: `/etc/assistant-api/config.yaml`
- All configuration values must have safe defaults

### Logging

- Log directory is configurable via YAML
- Fallback directory: `/var/log/assistant-api`
- Logging must be centralized and consistent

### Deployment

- The service runs as a Linux system service
- Managed by `systemd`
- Executed inside a Python virtual environment

---

## 11. Extensibility

The architecture is designed to support future services:

### Speech-to-Text (STT)

- Reuse worker and streaming patterns
- Different engine implementations
- Same session abstractions

### LLM routing

- Gateway-style endpoints
- Stateless request handling
- Optional streaming responses

No architectural changes should be required to add these services.

---

## 12. Guiding principles

- Explicit over implicit
- Clear boundaries over clever abstractions
- Isolation over shared state
- Streaming over buffering
- Predictable behavior over hidden magic

This document defines the architectural intent of assistant-api.
Implementation details must follow these principles.
