"""LangChain chat page for the interview practice app."""

from __future__ import annotations

import streamlit as st

from app.core.logging_config import setup_logging
from app.ui.langchain_chat_ui import render_langchain_chat_ui


def main() -> None:
    """Run the LangChain chat page."""
    # Ensure standard console logging is active before any log calls.
    setup_logging()
    # Configure the page for the LangChain chat view.
    st.set_page_config(
        page_title="LangChain Interview Chat", page_icon="🧩", layout="wide"
    )
    render_langchain_chat_ui()


if __name__ == "__main__":
    main()
