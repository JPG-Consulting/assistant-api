"""MP3 encoder implementation."""

from __future__ import annotations

from typing import Optional

import lameenc

from assistant_api.app.audio.encoder import AudioEncoder
from assistant_api.app.audio.types import AudioFormat, PcmSpec


class Mp3Encoder(AudioEncoder):
    """Streaming MP3 encoder backed by lameenc."""

    def __init__(self, pcm_spec: PcmSpec, bitrate_kbps: int = 128) -> None:
        # MP3 encoding currently expects 16-bit PCM input; other widths must be
        # handled upstream until additional sample formats are supported.
        super().__init__(pcm_spec=pcm_spec, output_format=AudioFormat.MP3)
        self._encoder = lameenc.Encoder()
        self._encoder.set_bit_rate(bitrate_kbps)
        self._encoder.set_in_sample_rate(int(pcm_spec.sample_rate))
        self._encoder.set_channels(int(pcm_spec.channels))
        self._encoder.set_quality(2)

    def encode_chunk(self, chunk: bytes) -> bytes:
        if not chunk:
            return b""
        return self._encoder.encode(chunk)

    def flush(self) -> Optional[bytes]:
        flushed = self._encoder.flush()
        return flushed or None
