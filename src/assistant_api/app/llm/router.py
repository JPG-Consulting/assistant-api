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
from assistant_api.app.llm.tool_requests import try_parse_tool_request
from assistant_api.app.settings import Settings

router = APIRouter()


class ChatMessage(BaseModel):
    role: str  # user | system | assistant | tool_result
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
    tool_result_messages: list[dict[str, str]] = []
    for message in payload.messages:
        if message.role not in {"user", "system", "assistant", "tool_result"}:
            continue
        if message.role == "user" and message.content:
            latest_user_message = message.content
        elif message.role == "system" and message.content:
            system_messages.append(message.content)
        elif message.role == "tool_result" and message.content is not None:
            tool_result_messages.append(
                {"role": message.role, "content": message.content}
            )
        # Client assistant messages are intentionally ignored.

    if not latest_user_message:
        raise HTTPException(status_code=400, detail="No user message provided.")

    conversation_id = (
        payload.conversation_id or conversation_store.create_conversation_id()
    )
    # Server owns conversation history.
    history = conversation_store.get_history(conversation_id)
    # tool_result messages are passed through verbatim; orchestration is future work.
    if conversation_store.is_tool_request_pending(conversation_id):
        prompt_history = [*history, *tool_result_messages]
        if tool_result_messages:
            conversation_store.set_tool_request_pending(conversation_id, False)
    else:
        prompt_history = history
    base_persona = get_base_persona(settings.llm.persona)
    satellite_prompt = sanitize_satellite_prompt("\n".join(system_messages))
    messages = build_prompt(
        base_persona=base_persona,
        satellite_prompt=satellite_prompt,
        history=prompt_history,
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

    tool_request = try_parse_tool_request(assistant_reply)
    assistant_content = "" if tool_request else assistant_reply

    conversation_store.set_tool_request_pending(conversation_id, bool(tool_request))
    if not tool_request:
        conversation_store.append_turn(
            conversation_id,
            latest_user_message,
            assistant_content,
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
                "message": {"role": "assistant", "content": assistant_content},
                "finish_reason": "stop",
            }
        ],
    }
    if tool_request:
        response["tool_request"] = tool_request
    return response
