"""Thin wrapper around the OpenAI chat completions API."""

from __future__ import annotations

import logging
from typing import Any

from app.core.model_catalog import DEFAULT_MODEL
from app.core.structured_output import STRUCTURED_OUTPUT_SCHEMA

_DOTENV_LOADED = False

# Optional import so tests can run without the dependency installed.
try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - exercised when dependency is missing
    OpenAI = None

_LOGGER = logging.getLogger(__name__)


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
    # Log once so it's clear that local env loading occurred.
    _LOGGER.info("dotenv_loaded")


def generate_completion(
    messages: list[dict[str, str]],
    temperature: float,
    model_name: str | None = None,
) -> tuple[bool, str]:
    """Generate a completion using the configured OpenAI model."""

    _load_dotenv_once()

    if OpenAI is None:
        # Defer dependency errors to runtime so tests can still run without OpenAI.
        _LOGGER.error("openai_client_missing")
        raise RuntimeError(
            "OpenAI client library is not installed. "
            "Install it with `pip install openai`."
        )

    # Fall back to the default model when no override is provided.
    selected_model = model_name or DEFAULT_MODEL

    # Build the client and forward the minimal payload we control.
    _LOGGER.info(
        "openai_request",
        extra={
            "model": selected_model,
            "temperature": temperature,
            "message_count": len(messages),
            "messages_total_length": sum(len(msg["content"]) for msg in messages),
        },
    )
    client = OpenAI()
    response: Any = client.chat.completions.create(
        model=selected_model,
        messages=messages,
        temperature=temperature,
        # Ask the model to return JSON that matches our schema instead of free-form text.
        response_format={"type": "json_schema", "json_schema": STRUCTURED_OUTPUT_SCHEMA},
    )
    # Extract the first response choice for a single-turn UI.
    message = response.choices[0].message
    refusal = getattr(message, "refusal", None)
    if refusal:
        # Surface refusal text without exposing additional content.
        _LOGGER.info("openai_refusal")
        return False, refusal
    return True, message.content or ""
