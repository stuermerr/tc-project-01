from app.core.model_catalog import (
    DEFAULT_MODEL,
    get_allowed_models,
    get_reasoning_effort_options,
    get_verbosity_options,
)


def test_get_allowed_models_returns_expected_list():
    # Ensure the catalog exposes the supported models in order.
    models = get_allowed_models()
    assert models == ["gpt-4o-mini", "gpt-5-nano", "gpt-5.2-chat-latest"]


def test_default_model_is_in_catalog():
    # Confirm the default model remains part of the allowed list.
    assert DEFAULT_MODEL in get_allowed_models()


def test_get_reasoning_effort_options_for_gpt5():
    # GPT-5 nano exposes reasoning effort controls.
    assert get_reasoning_effort_options("gpt-5-nano") == [
        "minimal",
        "low",
        "medium",
        "high",
    ]
    assert get_reasoning_effort_options("gpt-5.2-chat-latest") == []


def test_get_verbosity_options_for_chat_latest():
    # GPT-5.2 chat-latest exposes verbosity controls.
    assert get_verbosity_options("gpt-5.2-chat-latest") == [
        "low",
        "medium",
        "high",
    ]
