"""API v1 package."""

from fastapi import APIRouter

from assistant_api.app.api.v1.prewarm import router as prewarm_router
from assistant_api.app.api.v1.speech import router as speech_router

api_router = APIRouter()
api_router.include_router(prewarm_router)
api_router.include_router(speech_router)

__all__ = ["api_router"]
