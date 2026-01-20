"""Piper TTS worker implementation."""

from __future__ import annotations

import importlib.util
import logging
from pathlib import Path
from typing import Any, Iterable

from assistant_api.app.audio.pcm_stream import PcmBufferStream
from assistant_api.app.audio.stream import AudioStream
from assistant_api.app.audio.types import Channels, PcmSpec, SampleRate
from assistant_api.app.settings import TtsSettings
from assistant_api.app.workers.base import BaseWorker

_DEFAULT_SAMPLE_RATE = SampleRate(16_000)
_PCM_SAMPLE_WIDTH_BYTES = 2
_DEFAULT_CHUNK_SIZE = 4096
logger = logging.getLogger(__name__)


class PiperTtsWorker(BaseWorker):
    """TTS worker backed by the Python `piper` module (not the CLI binary)."""

    def __init__(self, settings: TtsSettings) -> None:
        self._settings = settings
        self._voice: Any | None = None
        self._voice_id: str | None = None
        self._pcm_spec: PcmSpec | None = None

    @classmethod
    def worker_type(cls) -> str:
        return "tts:piper"

    @classmethod
    def is_available(cls, settings: TtsSettings) -> bool:
        if settings.engine != "piper":
            logger.info("PiperTtsWorker: availability = False (engine=%s)", settings.engine)
            return False
        if importlib.util.find_spec("piper") is None:
            logger.warning("PiperTtsWorker: availability = False (reason: module missing)")
            return False
        return True

    @property
    def pcm_spec(self) -> PcmSpec | None:
        return self._pcm_spec

    def process(self, payload: Any) -> AudioStream:
        voice_id = _extract_voice(payload, self._settings.default_model)
        logger.info("PiperTtsWorker: using voice model %s", voice_id)
        voice = self._load_voice(voice_id)
        text = _extract_text(payload)
        stream = PcmBufferStream()
        for chunk in _synthesize_pcm_chunks(voice, text):
            if chunk:
                stream.push_pcm(chunk)
        stream.close()
        return stream

    def shutdown(self) -> None:
        """No-op shutdown for the Piper worker."""

    def preload(self) -> bool:
        """Load the Piper voice model if needed."""
        try:
            voice_id = _extract_voice({}, self._settings.default_model)
            self._load_voice(voice_id)
        except Exception as exc:
            logger.warning("Piper preload failed: %s", exc)
            return False
        return True

    def _load_voice(self, voice_id: str) -> Any:
        if self._voice is not None and self._voice_id == voice_id:
            logger.info("PiperTtsWorker: reusing cached voice model %s", voice_id)
            return self._voice
        if self._voice is not None and self._voice_id != voice_id:
            logger.info(
                "PiperTtsWorker: switching voice from %s to %s",
                self._voice_id,
                voice_id,
            )
        if importlib.util.find_spec("piper") is None:
            logger.error(
                "PiperTtsWorker: Piper module missing; external binary is not used."
            )
            raise RuntimeError("Piper is not installed.")
        model_path = self._resolve_model_path(voice_id)
        if not model_path.is_file():
            logger.error(
                "PiperTtsWorker: model file missing at %s",
                model_path,
            )
            raise FileNotFoundError(f"Piper model file not found: {model_path}")
        from piper.voice import PiperVoice

        logger.info(
            "PiperTtsWorker: loading Piper voice from model path: %s", model_path
        )
        self._voice = PiperVoice.load(str(model_path))
        self._voice_id = voice_id
        self._pcm_spec = _pcm_spec_from_voice(self._voice)
        return self._voice

    def _resolve_model_path(self, voice_id: str) -> Path:
        # Model paths are resolved only via TtsSettings.models_path; environment
        # variables are not treated as primary configuration for Piper models.
        if not self._settings.models_path:
            raise RuntimeError("Piper models_path is not configured.")
        return self._settings.models_path / f"{voice_id}.onnx"


def _extract_text(payload: Any) -> str:
    if isinstance(payload, dict):
        text = payload.get("text", "")
        return "" if text is None else str(text)
    if payload is None:
        return ""
    return str(payload)


def _extract_voice(payload: Any, default_model: str | None) -> str:
    if isinstance(payload, dict):
        voice = payload.get("voice")
        if voice:
            return str(voice)
    if default_model:
        return default_model
    raise ValueError("No Piper voice specified and no default_model configured.")


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
