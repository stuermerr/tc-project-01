"""Tests for chat history helpers."""

from app.core.chat_history import (
    ChatMessage,
    append_chat_message,
    init_chat_history,
    trim_chat_history,
)


def test_init_chat_history_creates_list():
    """Verify init chat history creates list."""
    # Start with an empty state to verify initialization.
    state: dict = {}

    # Initialize and capture the stored list.
    messages = init_chat_history(state)

    assert messages == []
    assert state["chat_history"] is messages


def test_append_chat_message_preserves_order():
    """Verify append chat message preserves order."""
    # Begin with an empty message list.
    messages: list[ChatMessage] = []

    # Append messages in a known order.
    append_chat_message(messages, role="user", content="First")
    append_chat_message(messages, role="assistant", content="Second")

    assert [message.role for message in messages] == ["user", "assistant"]
    assert [message.content for message in messages] == ["First", "Second"]


def test_trim_chat_history_enforces_max_chars():
    """Verify trim chat history enforces max chars."""
    # Build a short history that exceeds the max length.
    messages = [
        ChatMessage(role="user", content="12345"),
        ChatMessage(role="assistant", content="67890"),
        ChatMessage(role="user", content="abc"),
    ]

    # Trim to a size that forces the oldest entry out.
    trim_chat_history(messages, max_chars=10)

    assert [message.content for message in messages] == ["67890", "abc"]
    assert sum(len(message.content) for message in messages) <= 10
