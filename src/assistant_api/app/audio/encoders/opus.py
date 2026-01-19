"""Opus encoder implementation."""

from __future__ import annotations

from typing import Optional

import opuslib

from assistant_api.app.audio.encoder import AudioEncoder
from assistant_api.app.audio.types import AudioFormat, PcmSpec


class OpusEncoder(AudioEncoder):
    """Streaming Opus encoder backed by opuslib.

    Notes:
        Opus encoding currently expects 16-bit PCM input and mono or stereo
        channel layouts. Other sample widths or channel counts are not
        validated here and should be handled upstream.
    """

    _FRAME_DURATION_MS = 20

    def __init__(self, pcm_spec: PcmSpec, bitrate_kbps: int = 64) -> None:
        super().__init__(pcm_spec=pcm_spec, output_format=AudioFormat.OPUS)
        self._encoder = opuslib.Encoder(
            int(pcm_spec.sample_rate),
            int(pcm_spec.channels),
            opuslib.APPLICATION_AUDIO,
        )
        self._encoder.bitrate = int(bitrate_kbps * 1000)
        self._channels = int(pcm_spec.channels)
        self._bytes_per_sample = int(pcm_spec.sample_width_bytes)
        self._frame_size = int(pcm_spec.sample_rate) * self._FRAME_DURATION_MS // 1000
        self._buffer = bytearray()

    def encode_chunk(self, chunk: bytes) -> bytes:
        if not chunk:
            return b""
        self._buffer.extend(chunk)
        return self._drain_frames()

    def flush(self) -> Optional[bytes]:
        if not self._buffer:
            return None
        output = bytearray()
        frame_bytes = self._frame_size * self._channels * self._bytes_per_sample
        output.extend(self._drain_frames())
        if self._buffer:
            padded = bytes(self._buffer) + b"\x00" * (frame_bytes - len(self._buffer))
            output.extend(self._encoder.encode(padded, self._frame_size))
            self._buffer.clear()
        return bytes(output) if output else None

    def _drain_frames(self) -> bytes:
        output = bytearray()
        frame_bytes = self._frame_size * self._channels * self._bytes_per_sample
        while len(self._buffer) >= frame_bytes:
            frame = bytes(self._buffer[:frame_bytes])
            del self._buffer[:frame_bytes]
            output.extend(self._encoder.encode(frame, self._frame_size))
        return bytes(output)
