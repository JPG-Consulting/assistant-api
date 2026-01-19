"""API endpoints for resource prewarming."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from assistant_api.app.core.prewarm import PrewarmRequest, get_prewarm_manager

router = APIRouter(prefix="/v1/audio", tags=["prewarm"])


class PrewarmPayload(BaseModel):
    """Minimal prewarm request payload from clients."""

    resource_id: str | None = None
    language: str | None = None
    voice: str | None = None


@router.post("/prewarm")
async def prewarm_audio(payload: PrewarmPayload) -> dict[str, str]:
    """Record prewarm intent for audio resources without loading models."""
    manager = get_prewarm_manager()
    request = PrewarmRequest(
        resource_id=payload.resource_id,
        language=payload.language,
        voice=payload.voice,
    )
    manager.request_optional(request)
    return {"status": "accepted"}
