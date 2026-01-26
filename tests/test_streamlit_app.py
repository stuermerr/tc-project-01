import importlib

import pytest


def test_streamlit_app_import_smoke():
    # Skip when Streamlit isn't installed so CI stays green.
    pytest.importorskip("streamlit")
    # Ensure the module imports without side effects or errors.
    importlib.import_module("app.ui.Interview_Preparation_Chat")
