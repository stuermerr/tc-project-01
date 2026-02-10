"""Allowed OpenAI model names for the app."""

from __future__ import annotations

# Centralize model choices so UI and client stay consistent.
ALLOWED_MODELS: list[str] = [
    "gpt-4o-mini",
    "gpt-5-nano",
    "gpt-5.2-chat-latest",
]

# Default to GPT-5.2 chat for the landing-page experience.
DEFAULT_MODEL = "gpt-5.2-chat-latest"
GPT5_MODELS = {"gpt-5-nano", "gpt-5.2-chat-latest"}
_REASONING_EFFORT_BY_MODEL = {
    "gpt-5-nano": ["minimal", "low", "medium", "high"],
}
DEFAULT_REASONING_EFFORT = "medium"


def get_allowed_models() -> list[str]:
    """Return a copy of the supported model list in display order."""

    # Return a shallow copy so callers cannot mutate the global list.
    return list(ALLOWED_MODELS)


def is_gpt5_model(model_name: str) -> bool:
    """Return True when the model uses GPT-5 reasoning controls."""

    return model_name in GPT5_MODELS


def get_reasoning_effort_options(model_name: str) -> list[str]:
    """Return the allowed reasoning effort values for the given model."""

    if model_name in _REASONING_EFFORT_BY_MODEL:
        return list(_REASONING_EFFORT_BY_MODEL[model_name])
    return []
