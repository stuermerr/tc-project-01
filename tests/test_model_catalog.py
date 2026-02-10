"""Tests for model catalog helpers."""

from app.core.model_catalog import DEFAULT_MODEL, get_allowed_models, get_reasoning_effort_options


def test_get_allowed_models_returns_expected_list():
    """Verify get allowed models returns expected list."""
    # Ensure the catalog exposes the supported models in order.
    models = get_allowed_models()
    assert models == ["gpt-4o-mini", "gpt-5-nano", "gpt-5.2-chat-latest"]


def test_default_model_is_in_catalog():
    """Verify default model is in catalog."""
    # Confirm the default model is the intended GPT-5.2 option and is selectable.
    assert DEFAULT_MODEL == "gpt-5.2-chat-latest"
    assert DEFAULT_MODEL in get_allowed_models()


def test_get_reasoning_effort_options_for_gpt5():
    """Verify get reasoning effort options for gpt5."""
    # GPT-5 nano exposes reasoning effort controls.
    assert get_reasoning_effort_options("gpt-5-nano") == [
        "minimal",
        "low",
        "medium",
        "high",
    ]
    assert get_reasoning_effort_options("gpt-5.2-chat-latest") == []
