"""Streamlit entrypoint that filters pages by implementation."""

from __future__ import annotations

import os

import streamlit as st

from app.core.logging_config import setup_logging


_IMPLEMENTATION_LABELS = {
    "langchain": "LangChain only",
    "openai": "OpenAI API only",
    "both": "LangChain + OpenAI API",
}


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
    """Choose the implementation mode from env or an optional UI toggle."""

    env_mode = _normalize_mode(os.getenv("APP_IMPL", "langchain"))
    if not _allow_impl_switch():
        return env_mode

    labels = list(_IMPLEMENTATION_LABELS.values())
    default_label = _IMPLEMENTATION_LABELS.get(env_mode, labels[0])
    selected_label = st.sidebar.selectbox(
        "Implementation view",
        options=labels,
        index=labels.index(default_label),
        help="Control which implementation pages appear in the navigation.",
    )
    for key, label in _IMPLEMENTATION_LABELS.items():
        if label == selected_label:
            return key
    return env_mode


def main() -> None:
    """Run the filtered multipage navigation."""

    # Ensure standard console logging is active before any log calls.
    setup_logging()
    # Configure the page for the filtered navigation view.
    st.set_page_config(page_title="Interview Practice App", page_icon="🧩", layout="wide")

    impl_mode = _resolve_impl_mode()

    # Build the navigation list based on the selected implementation mode.
    pages: list[st.Page] = []
    if impl_mode in {"openai", "both"}:
        pages.extend(
            [
                st.Page(
                    "app/ui/openai_chat_app.py",
                    title="Interview Preparation Chat (OpenAI API)",
                    default=(impl_mode == "openai"),
                ),
                st.Page(
                    "app/ui/pages/1_OpenAI_Questions_Generator.py",
                    title="Interview Questions Generator (OpenAI API)",
                ),
            ]
        )

    if impl_mode in {"langchain", "both"}:
        pages.extend(
            [
                st.Page(
                    "app/ui/pages/2_LangChain_Chat.py",
                    title="Interview Preparation Chat (LangChain)",
                    default=(impl_mode in {"langchain", "both"}),
                ),
                st.Page(
                    "app/ui/pages/3_LangChain_Questions_Generator.py",
                    title="Interview Questions Generator (LangChain)",
                ),
            ]
        )

    # Explicit navigation hides other pages even if they exist on disk.
    st.navigation(pages).run()


if __name__ == "__main__":
    main()
