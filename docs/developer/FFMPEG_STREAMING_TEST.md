# FFmpeg Compressed Streaming Test (ALSA)

## Purpose
This manual test validates compressed audio streaming behavior for the `/v1/audio/speech` endpoint. It confirms that MP3 or Opus output can be decoded incrementally and played in real time via ALSA while the HTTP response is still streaming. It is not suitable for debugging raw PCM issues.

## Streaming pipeline
The script uses a streaming-only pipeline with no temporary files:

```
curl → ffmpeg → aplay
```

`curl` streams the HTTP response, `ffmpeg` decodes MP3/Opus to PCM, and `aplay` plays the PCM stream immediately. This validates streaming behavior, not TTS quality.

## Example usage

```bash
./tests/manual/play_tts_ffmpeg_alsa.sh \
  --host 127.0.0.1 \
  --port 8000 \
  default \
  mp3 \
  "Hello from the compressed streaming test"
```

To use an existing server, add `--no-server`:

```bash
./tests/manual/play_tts_ffmpeg_alsa.sh --no-server default opus "Streaming Opus test"
```

## Limitations
- Manual test only; not intended for CI.
- Requires `ffmpeg` and ALSA (`aplay`).
- Playback assumes 16-bit little-endian PCM at 22050 Hz, mono.
- Optional and complementary to the PCM-only ALSA streaming test.
