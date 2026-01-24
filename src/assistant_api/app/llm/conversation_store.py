"""In-memory conversation store."""

from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock
from uuid import uuid4


Message = dict[str, str]


@dataclass
class ConversationStore:
    """Simple in-memory store with a rolling turn window."""

    max_turns: int = 10
    _conversations: dict[str, list[Message]] = field(default_factory=dict)
    _tool_request_pending: dict[str, bool] = field(default_factory=dict)
    _lock: Lock = field(default_factory=Lock)

    def create_conversation_id(self) -> str:
        conversation_id = str(uuid4())
        with self._lock:
            self._conversations.setdefault(conversation_id, [])
            self._tool_request_pending.setdefault(conversation_id, False)
        return conversation_id

    def get_history(self, conversation_id: str) -> list[Message]:
        with self._lock:
            return list(self._conversations.get(conversation_id, []))

    def append_message(self, conversation_id: str, role: str, content: str) -> None:
        message = {"role": role, "content": content}
        with self._lock:
            history = self._conversations.setdefault(conversation_id, [])
            history.append(message)
            max_messages = self.max_turns * 2
            if len(history) > max_messages:
                self._conversations[conversation_id] = history[-max_messages:]

    def append_turn(
        self,
        conversation_id: str,
        user_message: str,
        assistant_message: str,
    ) -> None:
        self.append_message(conversation_id, "user", user_message)
        self.append_message(conversation_id, "assistant", assistant_message)

    def is_tool_request_pending(self, conversation_id: str) -> bool:
        with self._lock:
            return self._tool_request_pending.get(conversation_id, False)

    def set_tool_request_pending(self, conversation_id: str, pending: bool) -> None:
        with self._lock:
            self._tool_request_pending[conversation_id] = pending


conversation_store = ConversationStore()
