"""Streamlit entrypoint that shows the LangChain pages only."""

from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

# Load .env so APP_IMPL/ALLOW_IMPL_SWITCH can be configured locally.
try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency
    load_dotenv = None

from app.core.logging_config import setup_logging


_IMPLEMENTATION_LABELS = {
    "langchain": "LangChain only",
    "openai": "OpenAI API only",
    "both": "LangChain + OpenAI API",
}

_BASE_DIR = Path(__file__).resolve().parent


def _normalize_mode(value: str | None) -> str:
    """Normalize the implementation mode to a supported value."""

    if not value:
        return "langchain"
    lowered = value.strip().lower()
    if lowered in _IMPLEMENTATION_LABELS:
        return lowered
    return "langchain"


def _allow_impl_switch() -> bool:
    """Return True when the UI toggle should be shown."""

    return os.getenv("ALLOW_IMPL_SWITCH", "").strip().lower() in {"1", "true", "yes"}


def _resolve_impl_mode() -> str:
    """Return the fixed implementation mode for the app."""

    # Always return the LangChain mode so only the LangChain pages are visible.
    return "langchain"


def main() -> None:
    """Run the filtered multipage navigation."""

    # Ensure standard console logging is active before any log calls.
    setup_logging()
    if load_dotenv is not None:
        load_dotenv()
    # Configure the page for the filtered navigation view.
    st.set_page_config(page_title="Interview Practice App", page_icon="🧩", layout="wide")

    impl_mode = _resolve_impl_mode()

    # Build the navigation list for the LangChain-only experience.
    pages: list[st.Page] = []
    if impl_mode == "langchain":
        pages.extend(
            [
                st.Page(
                    str(_BASE_DIR / "pages" / "2_LangChain_Chat.py"),
                    title="Interview Preparation Chat",
                    default=True,
                ),
                st.Page(
                    str(_BASE_DIR / "pages" / "3_LangChain_Questions_Generator.py"),
                    title="Interview Questions Generator",
                ),
            ]
        )

    # Explicit navigation hides other pages even if they exist on disk.
    st.navigation(pages).run()


if __name__ == "__main__":
    main()
