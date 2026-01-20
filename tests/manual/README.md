# Manual Audio Streaming Tests

This directory contains **manual, developer-facing integration tests** for the
`assistant-api` service.

These tests are **not unit tests** and are **not executed in CI**.
They are intended to validate real-world behavior involving:

- Streaming audio responses
- Real audio devices (ALSA)
- End-to-end request pipelines

They assume a Linux environment.

---

## Overview

The primary goal of these tests is to verify that the Text-to-Speech API:

- Starts correctly as a service
- Streams audio incrementally over HTTP
- Produces audio that can be consumed in real time
- Works with actual ALSA output devices

All tests in this directory are **best-effort tools** for local development.

---

## Available Tests

### play_tts_alsa.py

Plays streamed TTS audio directly to an ALSA device while the audio is still
being generated.

This test launches the API service locally, sends a TTS request, and pipes
the streaming audio output directly into `aplay` via stdin.

#### Purpose

This test validates:

- Service startup
- `/v1/audio/speech` streaming behavior
- Low-latency audio delivery
- ALSA playback compatibility
- End-to-end correctness

---

### play_tts_ffmpeg_alsa.sh

Plays streamed compressed TTS audio (MP3 or Opus) by decoding with `ffmpeg` and
sending PCM output to ALSA in real time.

#### Purpose

This test validates:

- `/v1/audio/speech` streaming behavior for compressed formats
- Incremental decoding with `ffmpeg`
- ALSA playback compatibility using PCM output

---

## Requirements

- Linux
- ALSA installed (`aplay` available in PATH)
- Python 3.10+
- Local checkout of `assistant-api`

Optional:

- Piper installed and configured (otherwise the dummy TTS worker is used)

---

## Usage

```bash
python tests/manual/play_tts_alsa.py \
  -D default \
  --format pcm \
  --model tts \
  --voice default \
  "Hello, this is a streaming text to speech test"
```

---

## Arguments

### Positional Arguments

| Argument | Description |
|---|---|
| `text` | The text to be spoken. Must be quoted if it contains spaces. |

---

### Options

#### `-D`, `--device`

ALSA output device passed directly to `aplay`.

Examples:

- `default`
- `hw:0,0`
- `plughw:1,0`

Example:

```bash
-D default
```

This argument is **required**.

---

#### `--format`

Audio format requested from the API.

Supported values:

- `pcm` (recommended)
- `mp3`
- `opus`

Default: `pcm`

Example:

```bash
--format pcm
```

---

#### `--model`

Model identifier forwarded directly to the API request.

This parameter is passed as-is and is not validated by the test.

Example:

```bash
--model tts
```

Optional.

---

#### `--voice`

Voice identifier forwarded directly to the API request.

Example:

```bash
--voice default
```

Optional.

---

#### `--host`

Host where the service will be started.

Default: `127.0.0.1`

---

#### `--port`

Port where the service will listen.

Default: `8000`

---

## Behavior Notes

- The service is launched as a subprocess by the test script
- The test waits until the HTTP endpoint becomes reachable
- Audio playback begins **as soon as audio chunks arrive**
- No temporary audio files are created
- On exit, the service is terminated cleanly

---

## Limitations

- This is a **manual test**, not suitable for CI
- Requires real audio hardware or a virtual ALSA device
- PCM playback assumes signed 16-bit little-endian samples
- Sample rate and channel count must match the server configuration

---

## Troubleshooting

- To list available ALSA devices:

```bash
aplay -L
```

- If Piper is unavailable, the dummy TTS worker will be used automatically
- Use `--format pcm` for the lowest latency and simplest debugging

---

## Design Philosophy

These tests intentionally prioritize:

- Real-world behavior
- Streaming correctness
- Minimal abstraction
- Transparency over automation

They exist to help developers **hear and verify** the system, not to simulate it.
