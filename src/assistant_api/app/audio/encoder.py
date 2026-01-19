"""Audio encoder abstractions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from assistant_api.app.audio.types import AudioFormat, PcmSpec


class AudioEncoder(ABC):
    """Streaming-friendly audio encoder contract."""

    def __init__(self, pcm_spec: PcmSpec, output_format: AudioFormat) -> None:
        self._pcm_spec = pcm_spec
        self._output_format = output_format

    @property
    def pcm_spec(self) -> PcmSpec:
        """Return the PCM specification expected by the encoder."""

        return self._pcm_spec

    @property
    def output_format(self) -> AudioFormat:
        """Return the output format produced by the encoder."""

        return self._output_format

    @abstractmethod
    def encode_chunk(self, chunk: bytes) -> bytes:
        """Encode a chunk of PCM audio and return encoded bytes."""

    @abstractmethod
    def flush(self) -> Optional[bytes]:
        """Flush any buffered data and return final encoded bytes, if any."""
