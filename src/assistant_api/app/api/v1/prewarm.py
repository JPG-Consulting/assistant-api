"""API endpoints for resource prewarming."""

from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from assistant_api.app.core.prewarm import PrewarmRequest, get_prewarm_manager
from assistant_api.app.settings import Settings
from assistant_api.app.workers.tts_piper import PiperTtsWorker

router = APIRouter(prefix="/v1/audio", tags=["prewarm"])
logger = logging.getLogger(__name__)
_PIPER_PREWARM_WORKER: PiperTtsWorker | None = None
_PIPER_PREWARM_LOCK = asyncio.Lock()


class PrewarmPayload(BaseModel):
    """Minimal prewarm request payload from clients."""

    resource_id: str | None = None
    language: str | None = None
    voice: str | None = None


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


@router.post("/prewarm")
async def prewarm_audio(
    payload: PrewarmPayload,
    settings: Settings = Depends(get_settings),
) -> dict[str, str]:
    """Record prewarm intent for audio resources without loading models."""
    manager = get_prewarm_manager()
    request = PrewarmRequest(
        resource_id=payload.resource_id,
        language=payload.language,
        voice=payload.voice,
    )
    manager.request_optional(request)
    if payload.resource_id and payload.resource_id.startswith("tts:piper"):
        if PiperTtsWorker.is_available(settings.tts):
            global _PIPER_PREWARM_WORKER
            if _PIPER_PREWARM_WORKER is None:
                async with _PIPER_PREWARM_LOCK:
                    if _PIPER_PREWARM_WORKER is None:
                        worker = PiperTtsWorker(settings.tts)
                        if await asyncio.to_thread(worker.preload):
                            _PIPER_PREWARM_WORKER = worker
                        else:
                            logger.warning("Piper prewarm skipped: preload failed")
    return {"status": "accepted"}
