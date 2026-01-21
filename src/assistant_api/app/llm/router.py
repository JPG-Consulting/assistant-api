"""LLM API router."""

from fastapi import APIRouter

router = APIRouter()


@router.post("/v1/chat/completions")
async def chat_completions() -> dict[str, dict[str, str]]:
    return {
        "error": {
            "message": "LLM endpoint not implemented yet",
            "type": "not_implemented",
        }
    }
