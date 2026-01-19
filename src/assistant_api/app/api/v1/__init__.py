"""API v1 package."""

from fastapi import APIRouter

from assistant_api.app.api.v1.prewarm import router as prewarm_router

api_router = APIRouter()
api_router.include_router(prewarm_router)

__all__ = ["api_router"]
