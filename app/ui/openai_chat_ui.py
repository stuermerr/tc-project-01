"""Chat UI rendering helpers for the multipage Streamlit app."""

from __future__ import annotations

from app.core.orchestration import (
    generate_chat_response,
    generate_chat_summary_response,
    generate_cover_letter_response,
)
from app.core.prompts import get_chat_prompt_variants
from app.ui.chat_ui_common import render_chat_ui as render_chat_ui_common


def render_chat_ui() -> None:
    """Render the chat experience without setting page config."""

    variants = get_chat_prompt_variants()
    render_chat_ui_common(
        page_title="Interview Preparation Chat",
        caption="Chat with the app for coaching, feedback, and practice questions.",
        prompt_variants=variants,
        prompt_label="Interview style",
        state_key_prefix="openai_chat",
        generate_response=generate_chat_response,
        generate_cover_letter=generate_cover_letter_response,
        generate_summary=generate_chat_summary_response,
    )
