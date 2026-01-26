"""Streamlit entrypoint that exposes only LangChain pages."""

from __future__ import annotations

import streamlit as st

from app.core.logging_config import setup_logging


def main() -> None:
    """Run the LangChain-only multipage navigation."""

    # Ensure standard console logging is active before any log calls.
    setup_logging()
    # Configure the page for the LangChain-only navigation view.
    st.set_page_config(
        page_title="Interview Practice (LangChain Only)",
        page_icon="🧩",
        layout="wide",
    )

    pages = [
        st.Page(
            "app/ui/pages/2_Interview_Preparation_Chat_(LangChain).py",
            title="Interview Preparation Chat (LangChain)",
            default=True,
        ),
        st.Page(
            "app/ui/pages/3_Interview_Questions_Generator_(LangChain).py",
            title="Interview Questions Generator (LangChain)",
        ),
    ]

    # Explicit navigation hides other pages even if they exist on disk.
    st.navigation(pages).run()


if __name__ == "__main__":
    main()
