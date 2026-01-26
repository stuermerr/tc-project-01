"""Tests for the chat UI module import."""

import importlib

import pytest


def test_chat_ui_import_smoke():
    """Verify chat ui import smoke."""
    # Skip when Streamlit isn't installed so CI stays green.
    pytest.importorskip("streamlit")
    # Ensure the module imports without side effects or errors.
    importlib.import_module("app.ui.openai_chat_ui")
