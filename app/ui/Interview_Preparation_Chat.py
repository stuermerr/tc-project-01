"""Streamlit entrypoint for the interview practice app."""

from __future__ import annotations

import streamlit as st

from app.core.logging_config import setup_logging
from app.ui.chat_ui import render_chat_ui


def main() -> None:
    """Streamlit entrypoint that serves the chat landing page."""

    # Ensure standard console logging is active before any log calls.
    setup_logging()
    # Configure the page once at startup to control layout and branding.
    st.set_page_config(
        page_title="Interview Preparation Chat", page_icon="🧩", layout="wide"
    )

    # Render the chat experience as the homepage for multipage navigation.
    render_chat_ui()


if __name__ == "__main__":
    # Allow `python Interview_Preparation_Chat.py` for local debugging.
    main()
