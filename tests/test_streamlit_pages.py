"""Tests for Streamlit multipage wiring."""

import importlib.util
from pathlib import Path

import pytest


def test_streamlit_classic_page_import_smoke():
    """Verify streamlit classic page import smoke."""
    # Skip when Streamlit isn't installed so CI stays green.
    pytest.importorskip("streamlit")

    page_path = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "ui"
        / "pages"
        / "1_Generate_Interview_Questions.py"
    )
    spec = importlib.util.spec_from_file_location("classic_page", page_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
