"""Thin wrapper around the OpenAI API."""

from __future__ import annotations

import logging
from typing import Any

from app.core.model_catalog import DEFAULT_MODEL, get_reasoning_effort_options, is_gpt5_model
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
    response = client.chat.completions.create(**request_payload)
    # Extract the first response choice for a single-turn UI.
    message = response.choices[0].message
    refusal = getattr(message, "refusal", None)
    if refusal:
        # Surface refusal text without exposing additional content.
        _LOGGER.info("openai_refusal")
        return False, refusal
    return True, message.content or ""


def _messages_to_responses_input(messages: list[dict[str, str]]) -> list[dict[str, str]]:
    """Convert chat messages into Responses API input format."""

    return [
        {"role": message["role"], "content": message["content"]}
        for message in messages
        if "role" in message and "content" in message
    ]


def _extract_responses_text(response: Any) -> str:
    """Extract text content from a Responses API result."""

    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str) and output_text:
        return output_text
    output = getattr(response, "output", None)
    if isinstance(output, list):
        parts: list[str] = []
        for item in output:
            content = getattr(item, "content", None)
            if isinstance(content, list):
                for part in content:
                    text = getattr(part, "text", None)
                    if isinstance(text, str):
                        parts.append(text)
        if parts:
            return "\n".join(parts)
    return ""


def _request_responses_chat(
    messages: list[dict[str, str]],
    model_name: str | None,
    reasoning_effort: str | None,
) -> tuple[bool, str]:
    """Send a Responses API request for free-form chat output."""

    _load_dotenv_once()
    if OpenAI is None:
        _LOGGER.error("openai_client_missing")
        raise RuntimeError(
            "OpenAI client library is not installed. "
            "Install it with `pip install openai`."
        )

    selected_model = model_name or DEFAULT_MODEL
    client = OpenAI()
    responses_input = _messages_to_responses_input(messages)
    payload: dict[str, Any] = {"model": selected_model, "input": responses_input}

    if reasoning_effort:
        allowed_efforts = get_reasoning_effort_options(selected_model)
        if reasoning_effort not in allowed_efforts and allowed_efforts:
            reasoning_effort = allowed_efforts[0]
        if reasoning_effort:
            payload["reasoning"] = {"effort": reasoning_effort}

    _LOGGER.info(
        "openai_responses_request",
        extra={
            "model": selected_model,
            "reasoning_effort": reasoning_effort or "default",
            "message_count": len(messages),
            "messages_total_length": sum(len(msg["content"]) for msg in messages),
        },
    )
    response = client.responses.create(**payload)
    text = _extract_responses_text(response)
    if not text:
        return False, "The model returned an empty response. Please try again."
    return True, text


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

    if model_name == "gpt-5.2-chat-latest":
        return _request_responses_chat(
            messages, model_name=model_name, reasoning_effort=reasoning_effort
        )
    return _request_completion(
        messages,
        temperature,
        model_name=model_name,
        reasoning_effort=reasoning_effort,
    )
