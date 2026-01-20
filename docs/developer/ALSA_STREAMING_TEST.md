# ALSA Streaming Test

## Purpose
The ALSA streaming test is a manual developer workflow for validating streamed text-to-speech audio playback through ALSA. It exercises the streaming endpoint and pipes the response directly into `aplay` so developers can confirm audio output on a target device.

## Real-time streaming validation
The script posts text to the TTS endpoint with streaming enabled and forwards each audio chunk to ALSA as it arrives. This verifies that the server streams audio in real time and that the ALSA device accepts continuous PCM input without buffering issues or format mismatches.

## `--no-server` mode
By default, the script starts the API server as a subprocess, waits until it is reachable, and terminates it when the script exits. Use `--no-server` to skip server management entirely; in that mode the script assumes the API server is already running at the specified host and port.

## Explicit PCM assumptions
Playback is PCM-only with explicit parameters passed to `aplay`:

- Sample rate: `22050` by default (`--sample-rate` can override).
- Channels: `1` by default (`--channels` can override).
- Format: `S16_LE` (fixed).

## Manual test scope
This is a manual test intended for developer verification. It is not designed for CI, and only PCM playback is supported.
