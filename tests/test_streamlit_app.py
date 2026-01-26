"""Tests for Streamlit entrypoint imports."""

import importlib.util
from pathlib import Path

import pytest


def test_streamlit_app_import_smoke():
    """Verify streamlit app import smoke."""
    # Skip when Streamlit isn't installed so CI stays green.
    pytest.importorskip("streamlit")
    page_path = Path(__file__).resolve().parents[1] / "app" / "ui" / "openai_chat_app.py"
    spec = importlib.util.spec_from_file_location("main_page", page_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)


def test_langchain_only_app_import_smoke():
    """Verify LangChain-only app import smoke."""
    # Skip when Streamlit isn't installed so CI stays green.
    pytest.importorskip("streamlit")

    page_path = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "ui"
        / "LangChain_Only.py"
    )
    spec = importlib.util.spec_from_file_location("langchain_only_page", page_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
