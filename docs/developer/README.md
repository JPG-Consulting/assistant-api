# Developer Documentation

This section describes the current architecture and developer workflow for assistant-api.

## Topics

- Architecture overview: `architecture.md`
- Repository layout: `directory_structure.md`
- Known gaps and follow-ups: `../../TODO.md`
- AI-assisted changes must follow `../../AGENTS.md`
- Manual ALSA streaming tests: `ALSA_STREAMING_TEST.md`, `FFMPEG_STREAMING_TEST.md`

Session-based or incremental TTS is future work; documentation should reflect current behavior.

## Run locally (development)

- **Python**: 3.10 or newer.
- **Virtual environment**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```
- **Install dependencies**:
  ```bash
  pip install -r requirements.txt
  ```
- **Install the project (editable)**: required so the `assistant_api` package is importable when running the server (`uvicorn assistant_api.app.main:app`) and for manual tests that start the server automatically.
  ```bash
  pip install -e .
  ```
- **Run the server**:
  ```bash
  uvicorn assistant_api.app.main:app --reload
  ```
