# Directory Structure

This document describes the **current** directory structure of the assistant-api repository.

---

## 1. Repository root

```
assistant-api/
```

Top-level files and directories:

- `README.md` — project overview
- `TODO.md` — backlog and follow-ups
- `LICENSE` — licensing information
- `config/` — example configuration files
- `docs/` — project documentation
- `src/` — application source code

---

## 2. Documentation (`docs/`)

```
docs/
├── README.md
├── user/
├── developer/
└── ai/
```

The `docs/` directory contains documentation for different audiences:

- **User docs** (`docs/user/`): operational guidance (still minimal).
- **Developer docs** (`docs/developer/`): architecture and repo structure.
- **AI context** (`docs/ai/`): context for AI-assisted contributions.

---

## 3. Application source code (`src/`)

```
src/
└── assistant_api/
```

All Python application code lives under `src/assistant_api/`.

Within the package, the main areas are:

- `app/api/` — HTTP endpoints and routing
- `app/audio/` — PCM buffering and encoders
- `app/workers/` — TTS workers (dummy and Piper)
- `app/core/` — lightweight shared infrastructure (e.g., prewarm manager)

---

## 4. Not yet present

Directories such as `tests/` and `scripts/` are not part of the repository yet. If added later, they should be documented here with their intended responsibilities.
