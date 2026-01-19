"""Thin wrapper around the OpenAI chat completions API."""

from __future__ import annotations

from typing import Any

DEFAULT_MODEL = "gpt-4o-mini"

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - exercised when dependency is missing
    OpenAI = None


def generate_completion(messages: list[dict[str, str]], temperature: float) -> str:
    """Generate a completion using the configured OpenAI model."""

    if OpenAI is None:
        raise RuntimeError(
            "OpenAI client library is not installed. "
            "Install it with `pip install openai`."
        )

    client = OpenAI()
    response: Any = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content or ""
