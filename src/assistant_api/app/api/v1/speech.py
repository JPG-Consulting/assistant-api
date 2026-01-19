"""Speech synthesis endpoints."""

from __future__ import annotations

from collections.abc import Generator
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from assistant_api.app.audio.encoders.mp3 import Mp3Encoder
from assistant_api.app.audio.encoders.opus import OpusEncoder
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
    pcm_spec = PcmSpec(
        sample_rate=SampleRate(16_000),
        channels=Channels(1),
        sample_width_bytes=2,
    )
    if request.format is None or request.format == "mp3":
        encoder = Mp3Encoder(pcm_spec)
        media_type = "audio/mpeg"
        audio_format = "mp3"
    elif request.format == "pcm":
        encoder = PcmPassthroughEncoder(pcm_spec)
        media_type = "audio/pcm"
        audio_format = "pcm"
    elif request.format == "opus":
        encoder = OpusEncoder(pcm_spec)
        media_type = "audio/ogg; codecs=opus"
        audio_format = "opus"
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format '{request.format}'. Supported formats: mp3, pcm, opus.",
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

    response = StreamingResponse(stream_audio(), media_type=media_type)
    response.headers["x-request-id"] = str(uuid4())
    response.headers["cache-control"] = "no-store"
    response.headers["content-disposition"] = (
        f'inline; filename="speech.{audio_format}"'
    )
    response.headers["x-openai-model"] = "assistant-api-tts-dummy"
    response.headers["x-openai-audio-format"] = audio_format
    return response
