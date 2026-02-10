"""Tests for chat and response PDF export helpers."""

from app.core.chat_exports import build_chat_pdf_bytes, build_response_pdf_bytes
from app.core.chat_history import ChatMessage


def test_build_chat_pdf_bytes_returns_pdf_header():
    """Verify chat transcript export returns valid PDF bytes."""
    messages = [
        ChatMessage(role="user", content="Hello", message_type="user"),
        ChatMessage(role="assistant", content="Hi there", message_type="chat"),
    ]
    pdf_bytes = build_chat_pdf_bytes(messages)
    assert pdf_bytes.startswith(b"%PDF")


def test_build_response_pdf_bytes_returns_pdf_header():
    """Verify generic assistant response export returns valid PDF bytes."""
    markdown_text = "# Feedback\n\n- Point **one**\n- Point `two`"
    pdf_bytes = build_response_pdf_bytes(markdown_text)
    assert pdf_bytes.startswith(b"%PDF")


def test_build_chat_pdf_bytes_handles_empty_history():
    """Verify transcript export handles empty chat history."""
    pdf_bytes = build_chat_pdf_bytes([])
    assert pdf_bytes.startswith(b"%PDF")

