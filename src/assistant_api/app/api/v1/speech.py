"""Speech synthesis endpoints."""

from __future__ import annotations

from collections.abc import Generator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from assistant_api.app.audio.encoders.pcm import PcmPassthroughEncoder
from assistant_api.app.audio.types import Channels, PcmSpec, SampleRate
from assistant_api.app.workers.tts_dummy import DummyTtsWorker

router = APIRouter(prefix="/v1/audio", tags=["speech"])


class SpeechRequest(BaseModel):
    """Minimal speech synthesis payload."""

    text: str
    voice: str | None = None
    format: str | None = None


@router.post("/speech")
def synthesize_speech(request: SpeechRequest) -> StreamingResponse:
    """Stream dummy PCM audio for the requested text."""
    worker = DummyTtsWorker()
    stream = worker.process(
        {"text": request.text, "voice": request.voice, "format": request.format}
    )
    encoder = PcmPassthroughEncoder(
        PcmSpec(
            sample_rate=SampleRate(16_000),
            channels=Channels(1),
            sample_width_bytes=2,
        )
    )

    def stream_audio() -> Generator[bytes, None, None]:
        while True:
            chunk = stream.read_encoded()
            if chunk is None:
                break
            yield encoder.encode_chunk(chunk)
        flush_chunk = encoder.flush()
        if flush_chunk:
            yield flush_chunk

    return StreamingResponse(stream_audio(), media_type="audio/pcm")
