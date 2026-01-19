"""Core audio type definitions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import NewType

SampleRate = NewType("SampleRate", int)
Channels = NewType("Channels", int)


class AudioFormat(str, Enum):
    """Supported audio container/codec identifiers."""

    PCM = "pcm"
    MP3 = "mp3"
    OPUS = "opus"


@dataclass(frozen=True)
class PcmSpec:
    """PCM audio specification."""

    sample_rate: SampleRate
    channels: Channels
    sample_width_bytes: int = 2
