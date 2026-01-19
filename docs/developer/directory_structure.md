# Directory Structure

This document describes the directory structure of the **assistant-api** repository.
Its purpose is to clearly define the responsibility of each directory and to prevent
architectural drift as the project grows.

This document complements `architecture.md` and focuses on *where things live*, not
*how they are implemented*.

---

## 1. Repository root

```
assistant-api/
```

The repository root contains only high-level project files and top-level directories.
No application logic should live directly at the root.

Typical files at this level include:

- `README.md` — project overview
- `LICENSE` — licensing information
- `.gitignore` — Git exclusions
- `.github/` — GitHub-specific configuration
- `.vscode/` — editor configuration (optional but recommended)

---

## 2. Documentation (`docs/`)

```
docs/
├── README.md
├── user/
├── developer/
└── ai/
```

The `docs/` directory contains all project documentation and is split by audience.

### 2.1 `docs/user/`

Documentation intended for **operators and users** of the service:

- Installation instructions
- Configuration reference
- Running and monitoring the service
- Troubleshooting

This documentation must not assume knowledge of the internal code structure.

---

### 2.2 `docs/developer/`

Documentation intended for **developers and contributors**:

- Architecture overview
- Directory structure
- Concurrency and streaming models
- Coding guidelines
- Testing strategy

These documents describe *design intent* rather than implementation details.

---

### 2.3 `docs/ai/`

Documentation intended for **AI-assisted development**:

- Project context for ChatGPT / Codex-like tools
- Architectural guardrails
- Constraints and non-goals

The key file in this directory is `chatgpt_context.md`, which is designed to be
attached as a single file to new AI conversations.

---

## 3. Application source code (`src/`)

```
src/
└── assistant_api/
```

All Python application code lives under `src/assistant_api/`.

Using a `src/` layout ensures:
- Clear separation between source code and repository root
- Avoidance of accidental imports from the working directory
- Better compatibility with modern Python tooling

No application code should exist outside this directory.

---

### 3.1 `assistant_api/` package

This is the root Python package for the service.

It will eventually contain subpackages such as:

- API layer (HTTP endpoints)
- Core orchestration logic
- Worker implementations
- Audio processing utilities
- Shared helpers

The internal structure of this package is documented separately and should evolve
gradually as features are implemented.

---

## 4. Tests (`tests/`)

```
tests/
```

The `tests/` directory contains all automated tests.

General guidelines:
- Mirror the structure of `src/assistant_api/`
- Keep tests isolated and deterministic
- Avoid reliance on external services unless explicitly required

No test code should live inside the application package itself.

---

## 5. Configuration examples (`config/`)

```
config/
└── systemd/
```

The `config/` directory contains **example configuration files only**.

These files are not used directly by the running service, but serve as references
and templates for operators.

### 5.1 `config/systemd/`

Example `systemd` unit files:

- Provided for reference
- Not installed automatically
- Intended to be copied to `/etc/systemd/system/`

Actual runtime configuration lives outside the repository (e.g. `/etc/assistant-api/`).

---

## 6. Scripts (`scripts/`)

```
scripts/
```

The `scripts/` directory contains helper scripts, such as:

- Development utilities
- Installation helpers
- Benchmarking tools
- One-off maintenance scripts

Scripts should be optional and must not be required for normal operation of the service.

---

## 7. What does NOT belong in the repository

To keep the repository clean and predictable, the following must not be committed:

- Virtual environments (`venv/`)
- Runtime logs
- Generated audio files
- Model weights
- Secrets or credentials

These belong in runtime or deployment environments, not in version control.

---

## 8. Anti-patterns to avoid

- Placing application code at the repository root
- Mixing documentation and implementation
- Introducing ad-hoc directories without documentation
- Letting configuration files double as runtime state
- Creating large, ambiguous “utils” modules

When in doubt, update the documentation before adding new structure.

---

## 9. Guiding principle

**The directory structure reflects architectural intent.**

If a component does not clearly belong in an existing directory, that is a signal
that either:
- the design needs clarification, or
- a new documented directory is required

This document should be updated whenever the structure evolves.
