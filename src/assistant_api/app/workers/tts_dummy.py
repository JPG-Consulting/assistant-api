"""Deterministic dummy TTS worker that emits fake PCM audio."""

from __future__ import annotations

from typing import Any, Iterable

from assistant_api.app.audio.dummy import DummyPcmStream
from assistant_api.app.audio.stream import AudioStream
from assistant_api.app.workers.base import BaseWorker

_PCM_SAMPLE_WIDTH_BYTES = 2
_SAMPLES_PER_CHAR = 160
# Implicit fake PCM format: 16-bit samples, mono, ~16kHz-equivalent chunk pacing.


class DummyTtsWorker(BaseWorker):
    """Fake TTS worker that generates deterministic PCM bytes."""

    @classmethod
    def worker_type(cls) -> str:
        return "tts:dummy"

    def process(self, payload: Any) -> AudioStream:
        text = _extract_text(payload)
        stream = DummyPcmStream()
        chunks = _pcm_chunks_for_text(text)
        for chunk in chunks:
            stream.push_pcm(chunk)
        stream.close()
        return stream

    def shutdown(self) -> None:
        """No-op shutdown for the dummy worker."""


def _extract_text(payload: Any) -> str:
    if isinstance(payload, dict):
        text = payload.get("text", "")
        return "" if text is None else str(text)
    if payload is None:
        return ""
    return str(payload)


def _pcm_chunks_for_text(text: str) -> Iterable[bytes]:
    if not text:
        yield _silence_chunk()
        return
    for char in text:
        yield _pcm_chunk_for_char(char)


def _pcm_chunk_for_char(char: str) -> bytes:
    seed = ord(char)
    buffer = bytearray()
    for index in range(_SAMPLES_PER_CHAR):
        value = ((index + seed) % 256) - 128
        sample = value * 256
        buffer.extend(sample.to_bytes(_PCM_SAMPLE_WIDTH_BYTES, "little", signed=True))
    return bytes(buffer)


def _silence_chunk() -> bytes:
    return b"\x00" * (_PCM_SAMPLE_WIDTH_BYTES * _SAMPLES_PER_CHAR)
