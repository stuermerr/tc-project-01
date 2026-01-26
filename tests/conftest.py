"""Pytest configuration and shared test setup."""

import sys
from pathlib import Path

import pytest

# Ensure the repo root is on sys.path so `app` imports work in tests.
project_root = Path(__file__).parent.parent
# Prepend to sys.path so local modules resolve before site-packages.
sys.path.insert(0, str(project_root))


@pytest.fixture(autouse=True)
def _disable_openai_moderation(monkeypatch):
    """Avoid network calls by disabling OpenAI moderation in tests."""

    monkeypatch.setattr("app.core.safety._moderation_flagged", lambda _text: None)
