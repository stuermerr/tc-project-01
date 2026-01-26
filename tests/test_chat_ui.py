import importlib

import pytest


def test_chat_ui_import_smoke():
    # Skip when Streamlit isn't installed so CI stays green.
    pytest.importorskip("streamlit")
    # Ensure the module imports without side effects or errors.
    importlib.import_module("app.ui.chat_ui")
