"""Thin wrapper around the OpenAI chat completions API."""

from __future__ import annotations

import logging
from typing import Any

from app.core.model_catalog import DEFAULT_MODEL, get_reasoning_effort_options, is_gpt5_model
from app.core.structured_output import STRUCTURED_OUTPUT_SCHEMA

_DOTENV_LOADED = False

# Optional import so tests can run without the dependency installed.
try:
    from openai import BadRequestError, OpenAI
except ImportError:  # pragma: no cover - exercised when dependency is missing
    OpenAI = None
    BadRequestError = None

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


def _request_completion(
    messages: list[dict[str, str]],
    temperature: float | None,
    model_name: str | None = None,
    response_format: dict[str, object] | None = None,
    reasoning_effort: str | None = None,
) -> tuple[bool, str]:
    """Send a chat completion request with optional response formatting."""

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
            "temperature": temperature if temperature is not None else "default",
            "reasoning_effort": reasoning_effort or "default",
            "message_count": len(messages),
            "messages_total_length": sum(len(msg["content"]) for msg in messages),
            "response_format": "json_schema" if response_format else "text",
        },
    )
    client = OpenAI()
    request_payload: dict[str, Any] = {
        "model": selected_model,
        "messages": messages,
    }
    if temperature is not None and not is_gpt5_model(selected_model):
        request_payload["temperature"] = temperature
    if response_format:
        request_payload["response_format"] = response_format
    if reasoning_effort and is_gpt5_model(selected_model):
        allowed_efforts = get_reasoning_effort_options(selected_model)
        if reasoning_effort not in allowed_efforts and allowed_efforts:
            reasoning_effort = allowed_efforts[0]
        if reasoning_effort:
            request_payload["reasoning_effort"] = reasoning_effort
    try:
        response = client.chat.completions.create(**request_payload)
    except Exception as exc:  # pragma: no cover - network error handling
        if (
            BadRequestError is not None
            and isinstance(exc, BadRequestError)
            and selected_model == "gpt-5.2-chat-latest"
            and "reasoning_effort" in str(exc)
        ):
            # Fall back to verbosity when reasoning_effort is rejected for chat-latest.
            fallback_payload = dict(request_payload)
            effort = fallback_payload.pop("reasoning_effort", None)
            verbosity_map = {
                "minimal": "low",
                "low": "low",
                "medium": "medium",
                "high": "high",
                "none": "low",
            }
            verbosity = verbosity_map.get(effort)
            if verbosity:
                fallback_payload["verbosity"] = verbosity
            _LOGGER.info(
                "openai_reasoning_effort_fallback",
                extra={"model": selected_model, "verbosity": verbosity or "default"},
            )
            response = client.chat.completions.create(**fallback_payload)
        else:
            raise
    # Extract the first response choice for a single-turn UI.
    message = response.choices[0].message
    refusal = getattr(message, "refusal", None)
    if refusal:
        # Surface refusal text without exposing additional content.
        _LOGGER.info("openai_refusal")
        return False, refusal
    return True, message.content or ""


def generate_completion(
    messages: list[dict[str, str]],
    temperature: float | None,
    model_name: str | None = None,
    reasoning_effort: str | None = None,
) -> tuple[bool, str]:
    """Generate a structured completion using the configured OpenAI model."""

    return _request_completion(
        messages,
        temperature,
        model_name=model_name,
        response_format={"type": "json_schema", "json_schema": STRUCTURED_OUTPUT_SCHEMA},
        reasoning_effort=reasoning_effort,
    )


def generate_chat_completion(
    messages: list[dict[str, str]],
    temperature: float | None,
    model_name: str | None = None,
    reasoning_effort: str | None = None,
) -> tuple[bool, str]:
    """Generate a free-form chat completion using the configured OpenAI model."""

    return _request_completion(
        messages,
        temperature,
        model_name=model_name,
        reasoning_effort=reasoning_effort,
    )
