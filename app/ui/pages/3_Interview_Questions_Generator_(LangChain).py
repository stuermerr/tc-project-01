"""LangChain single-shot page for the interview practice app."""

from __future__ import annotations

import streamlit as st

from app.core.logging_config import setup_logging
from app.ui.langchain_ui import render_langchain_ui


def main() -> None:
    """Run the LangChain interview questions page."""
    # Ensure standard console logging is active before any log calls.
    setup_logging()
    # Configure the page for the LangChain mode view.
    st.set_page_config(
        page_title="Interview Questions Generator (LangChain)",
        page_icon="🧩",
        layout="wide",
    )
    render_langchain_ui()


if __name__ == "__main__":
    main()
