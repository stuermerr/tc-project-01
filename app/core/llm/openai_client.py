"""Thin wrapper around the OpenAI chat completions API."""

from __future__ import annotations

from typing import Any

_DOTENV_LOADED = False

# Default model for Sprint 1; can be swapped later if needed.
DEFAULT_MODEL = "gpt-4o-mini"

# Optional import so tests can run without the dependency installed.
try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - exercised when dependency is missing
    OpenAI = None


def _load_dotenv_once() -> None:
    """Load local .env into the environment once for dev convenience."""

    global _DOTENV_LOADED
    if _DOTENV_LOADED:
        return
    _DOTENV_LOADED = True
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv()


def generate_completion(messages: list[dict[str, str]], temperature: float) -> str:
    """Generate a completion using the configured OpenAI model."""

    _load_dotenv_once()

    if OpenAI is None:
        # Defer dependency errors to runtime so tests can still run without OpenAI.
        raise RuntimeError(
            "OpenAI client library is not installed. "
            "Install it with `pip install openai`."
        )

    # Build the client and forward the minimal payload we control.
    client = OpenAI()
    response: Any = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=messages,
        temperature=temperature,
    )
    # Extract the first response choice for a single-turn UI.
    return response.choices[0].message.content or ""
