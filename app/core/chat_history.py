"""Helpers for managing chat history in Streamlit session state."""

from __future__ import annotations

from dataclasses import dataclass

# Key used to store chat history in Streamlit session state.
_STATE_KEY = "chat_history"


@dataclass
class ChatMessage:
    """Single chat message with a role and text content."""

    role: str
    content: str


def init_chat_history(state: dict) -> list[ChatMessage]:
    """Ensure a chat history list exists in session state and return it."""

    # Initialize an empty history when the key is missing or malformed.
    if _STATE_KEY not in state or not isinstance(state[_STATE_KEY], list):
        state[_STATE_KEY] = []
    # Return the shared list so callers can append in place.
    return state[_STATE_KEY]


def append_chat_message(messages: list[ChatMessage], role: str, content: str) -> None:
    """Append a new chat message while preserving order."""

    # Keep order stable by always appending to the end of the list.
    messages.append(ChatMessage(role=role, content=content))


def trim_chat_history(messages: list[ChatMessage], max_chars: int) -> None:
    """Trim oldest messages until the total content length is within max_chars."""

    # Treat negative limits as zero to avoid confusing behavior.
    if max_chars < 0:
        max_chars = 0

    # Count total content length so we know if trimming is required.
    total_chars = sum(len(message.content) for message in messages)
    if total_chars <= max_chars:
        return

    # Remove oldest messages until we are under the allowed character budget.
    while messages and total_chars > max_chars:
        total_chars -= len(messages[0].content)
        messages.pop(0)
