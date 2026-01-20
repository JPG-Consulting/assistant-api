"""Speech synthesis endpoints."""

from __future__ import annotations

from collections.abc import Generator
from uuid import uuid4

import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, root_validator

from assistant_api.app.audio.encoders.mp3 import Mp3Encoder
from assistant_api.app.audio.encoders.opus import OpusEncoder
from assistant_api.app.audio.encoders.pcm import PcmPassthroughEncoder
from assistant_api.app.audio.types import Channels, PcmSpec, SampleRate
from assistant_api.app.settings import Settings
from assistant_api.app.workers.tts_dummy import DummyTtsWorker
from assistant_api.app.workers.tts_piper import PiperTtsWorker

router = APIRouter(prefix="/v1/audio", tags=["speech"])
logger = logging.getLogger(__name__)


class SpeechRequest(BaseModel):
    """Minimal speech synthesis payload."""

    input: str | None = None
    text: str | None = None
    voice: str | None = None
    format: str | None = None

    @root_validator(pre=True)
    def require_input_or_text(cls, values: dict[str, object]) -> dict[str, object]:
        if values.get("input") is None and values.get("text") is None:
            raise ValueError("Request must include either 'input' (preferred) or 'text'.")
        return values


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


@router.post("/speech")
def synthesize_speech(
    request: SpeechRequest,
    settings: Settings = Depends(get_settings),
) -> StreamingResponse:
    """Stream PCM audio for the requested text."""
    text = request.input if request.input is not None else request.text
    payload = {"text": text, "voice": request.voice, "format": request.format}
    default_pcm_spec = PcmSpec(
        sample_rate=SampleRate(16_000),
        channels=Channels(1),
        sample_width_bytes=2,
    )
    pcm_spec = default_pcm_spec
    model_name = "assistant-api-tts-dummy"
    if settings.tts.engine == "piper":
        worker = PiperTtsWorker(settings.tts)
        try:
            stream = worker.process(payload)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:
            logger.exception("Piper TTS failed.")
            raise HTTPException(
                status_code=500,
                detail="Piper TTS failed to synthesize speech.",
            ) from exc
        pcm_spec = worker.pcm_spec or default_pcm_spec
        model_name = "assistant-api-tts-piper"
    else:
        worker = DummyTtsWorker()
        stream = worker.process(payload)
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
    response.headers["x-openai-model"] = model_name
    response.headers["x-openai-audio-format"] = audio_format
    return response
