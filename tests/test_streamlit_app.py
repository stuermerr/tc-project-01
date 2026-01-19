import importlib

import pytest


def test_streamlit_app_import_smoke():
    pytest.importorskip("streamlit")
    importlib.import_module("app.ui.streamlit_app")
