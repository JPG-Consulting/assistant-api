"""PCM passthrough encoder implementation."""

from __future__ import annotations

from typing import Optional

from assistant_api.app.audio.encoder import AudioEncoder
from assistant_api.app.audio.types import AudioFormat, PcmSpec


class PcmPassthroughEncoder(AudioEncoder):
    """PCM encoder that returns audio unchanged."""

    def __init__(self, pcm_spec: PcmSpec) -> None:
        super().__init__(pcm_spec=pcm_spec, output_format=AudioFormat.PCM)

    def encode_chunk(self, chunk: bytes) -> bytes:
        return chunk

    def flush(self) -> Optional[bytes]:
        return None
