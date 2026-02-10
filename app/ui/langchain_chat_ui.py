"""LangChain chat UI rendering helpers."""

from __future__ import annotations

from app.core.langchain_client import (
    generate_langchain_chat_response,
    generate_langchain_chat_summary,
    generate_langchain_cover_letter_response,
)
from app.core.prompts import get_chat_prompt_variants
from app.ui.chat_ui_common import render_chat_ui


def render_langchain_chat_ui() -> None:
    """Render the LangChain chat experience without setting page config."""

    variants = get_chat_prompt_variants()
    render_chat_ui(
        page_title="Interview Preparation Chat",
        caption="Chat with the app for coaching, feedback, and practice questions.",
        prompt_variants=variants,
        prompt_label="Interview style",
        state_key_prefix="langchain_chat",
        generate_response=generate_langchain_chat_response,
        generate_cover_letter=generate_langchain_cover_letter_response,
        generate_summary=generate_langchain_chat_summary,
    )
