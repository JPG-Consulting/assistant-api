"""Audio stream abstractions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from assistant_api.app.audio.types import AudioFormat


class AudioStream(ABC):
    """Bidirectional audio stream contract.

    Producers push PCM chunks into the stream, and consumers read encoded chunks
    out of it. Implementations can decide buffering and concurrency strategy.
    """

    @property
    @abstractmethod
    def output_format(self) -> AudioFormat:
        """Return the encoded output format produced by the stream."""

    @abstractmethod
    def push_pcm(self, chunk: bytes) -> None:
        """Accept a PCM audio chunk from a producer."""

    @abstractmethod
    def read_encoded(self) -> Optional[bytes]:
        """Read the next encoded audio chunk if available.

        Returns None when no more data is available or the stream is closed.
        """
