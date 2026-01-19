"""Dummy PCM audio stream implementation."""

from __future__ import annotations

from collections import deque
from typing import Deque, Optional

from assistant_api.app.audio.stream import AudioStream
from assistant_api.app.audio.types import AudioFormat


class DummyPcmStream(AudioStream):
    """Minimal PCM passthrough stream for validation."""

    def __init__(self) -> None:
        self._buffer: Deque[bytes] = deque()
        self._closed = False

    @property
    def output_format(self) -> AudioFormat:
        return AudioFormat.PCM

    def push_pcm(self, chunk: bytes) -> None:
        if not isinstance(chunk, (bytes, bytearray, memoryview)):
            raise TypeError("PCM chunks must be bytes-like")
        self._buffer.append(bytes(chunk))

    def close(self) -> None:
        """Mark the stream as closed to signal end-of-stream."""
        self._closed = True

    def read_encoded(self) -> Optional[bytes]:
        if not self._buffer:
            return None
        return self._buffer.popleft()
