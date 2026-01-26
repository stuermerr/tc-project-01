"""Chat UI rendering helpers for the multipage Streamlit app."""

from __future__ import annotations

from app.core.orchestration import generate_chat_response
from app.core.prompts import get_chat_prompt_variants
from app.ui.chat_ui_common import render_chat_ui as render_chat_ui_common


def render_chat_ui() -> None:
    """Render the chat experience without setting page config."""

    variants = get_chat_prompt_variants()
    render_chat_ui_common(
        page_title="Interview Preparation Chat",
        caption="Chat with the app for coaching, feedback, and practice questions.",
        prompt_variants=variants,
        prompt_label="Prompt variant",
        generate_response=generate_chat_response,
    )
