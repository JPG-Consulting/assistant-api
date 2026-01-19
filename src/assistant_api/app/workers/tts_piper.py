"""Piper TTS worker implementation."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from typing import Any, Iterable

from assistant_api.app.audio.pcm_stream import PcmBufferStream
from assistant_api.app.audio.stream import AudioStream
from assistant_api.app.audio.types import Channels, PcmSpec, SampleRate
from assistant_api.app.workers.base import BaseWorker

_MODEL_PATH_ENV = "PIPER_MODEL_PATH"
_DEFAULT_SAMPLE_RATE = SampleRate(16_000)
_PCM_SAMPLE_WIDTH_BYTES = 2
_DEFAULT_CHUNK_SIZE = 4096


class PiperTtsWorker(BaseWorker):
    """TTS worker backed by Piper."""

    def __init__(self) -> None:
        self._voice: Any | None = None
        self._pcm_spec: PcmSpec | None = None

    @classmethod
    def worker_type(cls) -> str:
        return "tts:piper"

    @classmethod
    def is_available(cls) -> bool:
        if importlib.util.find_spec("piper") is None:
            return False
        model_path = _get_model_path()
        return model_path is not None and model_path.is_file()

    @property
    def pcm_spec(self) -> PcmSpec | None:
        return self._pcm_spec

    def process(self, payload: Any) -> AudioStream:
        voice = self._load_voice()
        text = _extract_text(payload)
        stream = PcmBufferStream()
        for chunk in _synthesize_pcm_chunks(voice, text):
            if chunk:
                stream.push_pcm(chunk)
        stream.close()
        return stream

    def shutdown(self) -> None:
        """No-op shutdown for the Piper worker."""

    def preload(self) -> None:
        """Load the Piper voice model if needed."""
        self._load_voice()

    def _load_voice(self) -> Any:
        if self._voice is not None:
            return self._voice
        if importlib.util.find_spec("piper") is None:
            raise RuntimeError("Piper is not installed.")
        model_path = _get_model_path()
        if model_path is None or not model_path.is_file():
            raise RuntimeError(
                f"Piper model file not found. Set {_MODEL_PATH_ENV} to a valid path."
            )
        from piper.voice import PiperVoice

        self._voice = PiperVoice.load(str(model_path))
        self._pcm_spec = _pcm_spec_from_voice(self._voice)
        return self._voice


def _get_model_path() -> Path | None:
    model_path = os.environ.get(_MODEL_PATH_ENV)
    if not model_path:
        return None
    return Path(model_path)


def _extract_text(payload: Any) -> str:
    if isinstance(payload, dict):
        text = payload.get("text", "")
        return "" if text is None else str(text)
    if payload is None:
        return ""
    return str(payload)


def _pcm_spec_from_voice(voice: Any) -> PcmSpec:
    sample_rate = _DEFAULT_SAMPLE_RATE
    config = getattr(voice, "config", None)
    if config is not None:
        config_rate = getattr(config, "sample_rate", None)
        if isinstance(config_rate, int):
            sample_rate = SampleRate(config_rate)
    voice_rate = getattr(voice, "sample_rate", None)
    if isinstance(voice_rate, int):
        sample_rate = SampleRate(voice_rate)
    return PcmSpec(
        sample_rate=sample_rate,
        channels=Channels(1),
        sample_width_bytes=_PCM_SAMPLE_WIDTH_BYTES,
    )


def _synthesize_pcm_chunks(voice: Any, text: str) -> Iterable[bytes]:
    if hasattr(voice, "synthesize_stream_raw"):
        for chunk in voice.synthesize_stream_raw(text):
            normalized = _normalize_pcm_chunk(chunk)
            if normalized:
                yield normalized
        return
    output = voice.synthesize(text)
    pcm_bytes = _normalize_pcm_chunk(output)
    yield from _chunk_bytes(pcm_bytes, _DEFAULT_CHUNK_SIZE)


def _normalize_pcm_chunk(chunk: Any) -> bytes:
    if isinstance(chunk, (bytes, bytearray, memoryview)):
        return bytes(chunk)
    if hasattr(chunk, "tobytes"):
        return chunk.tobytes()
    if isinstance(chunk, tuple) and chunk:
        return _normalize_pcm_chunk(chunk[0])
    raise TypeError("Unexpected Piper audio payload; expected bytes-like PCM data.")


def _chunk_bytes(data: bytes, size: int) -> Iterable[bytes]:
    if not data:
        return
    for start in range(0, len(data), size):
        yield data[start : start + size]
