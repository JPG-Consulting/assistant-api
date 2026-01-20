# ALSA Streaming Test

## Purpose of ALSA streaming tests
These scripts are manual diagnostic tools used to validate end-to-end TTS audio output. They are especially useful when debugging raw PCM playback and are not automated tests.

## Real-time streaming validation
The script posts text to the TTS endpoint with streaming enabled and forwards each audio chunk to ALSA as it arrives. This verifies that the server streams audio in real time and that the ALSA device accepts continuous PCM input without buffering issues or format mismatches.

## `--no-server` mode
By default, the script starts the API server as a subprocess, waits until it is reachable, and terminates it when the script exits. Use `--no-server` to skip server management entirely; in that mode the script assumes the API server is already running at the specified host and port.

## Explicit PCM assumptions
Playback is PCM-only with explicit parameters passed to `aplay`:

- Sample rate: `16000` by default (`--sample-rate` can override).
- Channels: `1` by default (`--channels` can override).
- Format: `S16_LE` (fixed).

## Manual test scope
This is a manual test intended for developer verification. It is not designed for CI, and only PCM playback is supported.

## Regression note: Piper PCM output
Piper TTS (piper-tts >= 1.3.0) emits `AudioChunk` objects. `AudioChunk.audio_int16_bytes` already contains signed 16-bit little-endian PCM, and assistant-api streams these bytes without resampling or normalization. ALSA playback must use a 16000 Hz sample rate, mono (1 channel), and `S16_LE` format; incorrect parameters can cause fast, slow, or noisy playback.

## Related manual test
For compressed audio streaming validation (MP3 or Opus via FFmpeg), see `FFMPEG_STREAMING_TEST.md`.
