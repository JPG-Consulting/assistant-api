"""LLM API router."""

from __future__ import annotations

import asyncio
import time
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from assistant_api.app.llm.conversation_store import conversation_store
from assistant_api.app.llm.persona import get_base_persona
from assistant_api.app.llm.prompt_builder import build_prompt
from assistant_api.app.llm.providers.ollama import OllamaError, chat
from assistant_api.app.llm.satellite_prompt import sanitize_satellite_prompt
from assistant_api.app.settings import Settings

router = APIRouter()


class ChatMessage(BaseModel):
    role: str
    content: str | None = None


class ChatCompletionRequest(BaseModel):
    messages: list[ChatMessage]
    conversation_id: str | None = None
    stream: bool | None = False


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


@router.post("/v1/chat/completions")
async def chat_completions(
    payload: ChatCompletionRequest,
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    if payload.stream:
        return JSONResponse(
            status_code=501,
            content={
                "error": {
                    "message": "Streaming not implemented yet",
                    "type": "not_implemented",
                }
            },
        )

    latest_user_message = None
    system_messages: list[str] = []
    for message in payload.messages:
        if message.role not in {"user", "system", "assistant"}:
            continue
        if message.role == "user" and message.content:
            latest_user_message = message.content
        elif message.role == "system" and message.content:
            system_messages.append(message.content)
        # Client assistant messages are intentionally ignored.

    if not latest_user_message:
        raise HTTPException(status_code=400, detail="No user message provided.")

    conversation_id = (
        payload.conversation_id or conversation_store.create_conversation_id()
    )
    # Server owns conversation history.
    history = conversation_store.get_history(conversation_id)
    base_persona = get_base_persona(settings.llm.persona)
    satellite_prompt = sanitize_satellite_prompt("\n".join(system_messages))
    # Language is enforced at the server level.
    # Satellite prompts must not override or influence response language.
    language_instruction = {
        "role": "system",
        "content": (
            f"You must reply exclusively in {settings.assistant.default_language}. "
            "Do not use any other language."
        ),
    }
    messages = build_prompt(
        language_instruction=language_instruction,
        base_persona=base_persona,
        satellite_prompt=satellite_prompt,
        history=history,
        user_message=latest_user_message,
    )

    llm_settings = settings.llm
    try:
        assistant_reply = await asyncio.to_thread(
            chat,
            model=llm_settings.model,
            host=llm_settings.host,
            messages=messages,
            temperature=llm_settings.temperature,
            max_tokens=llm_settings.max_tokens,
        )
    except OllamaError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    conversation_store.append_turn(
        conversation_id,
        latest_user_message,
        assistant_reply,
    )

    response = {
        "id": f"chatcmpl-{uuid4().hex}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": llm_settings.model,
        "conversation_id": conversation_id,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": assistant_reply},
                "finish_reason": "stop",
            }
        ],
    }
    return response
