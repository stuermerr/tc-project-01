"""Classic single-shot page for the interview practice app."""

from __future__ import annotations

import streamlit as st

from app.core.logging_config import setup_logging
from app.ui.classic_ui import render_classic_ui


def main() -> None:
    # Ensure standard console logging is active before any log calls.
    setup_logging()
    # Configure the page for the classic mode view.
    st.set_page_config(
        page_title="Generate Interview Questions", page_icon="🧩", layout="wide"
    )
    render_classic_ui()


if __name__ == "__main__":
    main()
