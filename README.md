# assistant-api

assistant-api is a Python backend service for voice assistants. It will provide an OpenAI-compatible API with an initial focus on Text-to-Speech (TTS) streaming output. The project targets Linux deployments and is intended to run as a systemd-managed service within a Python virtual environment.

## Goals

- Provide a clean, extensible foundation for future TTS, STT, and LLM services.
- Keep the architecture modular and easy to evolve.
- Prioritize clear, minimal documentation and predictable operations.

## Non-goals (for now)

- Implementing TTS/STT/LLM providers or business logic.
- Defining detailed API behavior beyond high-level compatibility.

## Proposed repository structure

```
assistant-api/
├── LICENSE
├── README.md
├── docs/
│   ├── README.md
│   ├── user/
│   │   └── README.md
│   ├── developer/
│   │   └── README.md
│   └── ai/
│       └── README.md
├── src/                      # Planned Python package root
│   └── assistant_api/
├── tests/                    # Planned test suite
├── config/                   # Planned service configuration
│   └── systemd/
└── scripts/                  # Planned tooling helpers
```

## Documentation

- User documentation: `docs/user/README.md`
- Developer documentation: `docs/developer/README.md`
- AI assistant context: `docs/ai/README.md`

## Status

This repository currently contains documentation scaffolding only. Application code will be added in future iterations.
