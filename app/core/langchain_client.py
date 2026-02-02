"""LangChain wrapper for LLM completions."""

from __future__ import annotations

import logging
import time

from app.core.dataclasses import RequestPayload
from app.core.model_catalog import (
    DEFAULT_MODEL,
    get_reasoning_effort_options,
    is_gpt5_model,
)
from app.core.orchestration import _parse_structured_output as parse_structured_output
from app.core.prompt_builder import build_messages
from app.core.prompts import (
    get_chat_prompt_variants,
    get_cover_letter_prompt,
    get_prompt_variants,
)
from app.core.safety import (
    sanitize_output,
    validate_chat_inputs,
    validate_inputs,
    validate_output,
)

_DOTENV_LOADED = False

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    try:
        from langchain.chat_models import ChatOpenAI
    except ImportError:  # pragma: no cover - exercised when dependency is missing
        ChatOpenAI = None

try:
    from langchain_core.messages import HumanMessage, SystemMessage
except ImportError:  # pragma: no cover - exercised when dependency is missing
    HumanMessage = None
    SystemMessage = None

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


def _payload_metadata(payload: RequestPayload) -> dict[str, int | float | str]:
    """Summarize payload sizes without logging raw user text."""

    # Length-only metadata keeps logs useful without exposing sensitive content.
    return {
        "job_description_length": len(payload.job_description),
        "cv_text_length": len(payload.cv_text),
        "user_prompt_length": len(payload.user_prompt),
        "prompt_variant_id": payload.prompt_variant_id,
        "temperature": payload.temperature if payload.temperature is not None else "default",
        "reasoning_effort": payload.reasoning_effort or "default",
        "model_name": payload.model_name,
    }


def _select_variant(prompt_variant_id: int):
    # Match the requested variant id, falling back to the first for safety.
    variants = get_prompt_variants()
    for variant in variants:
        if variant.id == prompt_variant_id:
            return variant
    # Fall back to the first variant if the requested id is missing.
    _LOGGER.warning(
        "langchain_variant_fallback",
        extra={"requested_variant_id": prompt_variant_id},
    )
    return variants[0]


def _resolve_reasoning_effort(
    selected_model: str, requested: str | None
) -> str | None:
    # Skip reasoning effort unless the model supports it.
    if not requested or not is_gpt5_model(selected_model):
        return None
    if selected_model == "gpt-5.2-chat-latest":
        return None
    allowed = get_reasoning_effort_options(selected_model)
    if allowed and requested not in allowed:
        return allowed[0]
    return requested


def _select_chat_variant(prompt_variant_id: int):
    # Match the requested chat variant id, falling back to the first for safety.
    variants = get_chat_prompt_variants()
    for variant in variants:
        if variant.id == prompt_variant_id:
            return variant
    # Fall back to the first chat variant if the requested id is missing.
    _LOGGER.warning(
        "langchain_chat_variant_fallback",
        extra={"requested_variant_id": prompt_variant_id},
    )
    return variants[0]


def _has_job_and_cv(payload: RequestPayload) -> bool:
    """Return True when both JD and CV are present."""

    # Cover letters require both inputs to be meaningful.
    return bool(payload.job_description.strip()) and bool(payload.cv_text.strip())


def _build_langchain_messages(messages: list[dict[str, str]]) -> list[object]:
    """Convert message dicts into LangChain message objects when available."""

    # Fall back to raw dicts when LangChain message classes are unavailable.
    if SystemMessage is None or HumanMessage is None:
        return messages
    if len(messages) < 2:
        return messages
    return [
        SystemMessage(content=messages[0]["content"]),
        HumanMessage(content=messages[1]["content"]),
    ]


def _build_llm_kwargs(payload: RequestPayload, selected_model: str) -> dict[str, object]:
    """Build initialization kwargs for the LangChain chat model."""

    llm_kwargs: dict[str, object] = {"model": selected_model}
    if payload.temperature is not None and not is_gpt5_model(selected_model):
        llm_kwargs["temperature"] = payload.temperature
    reasoning_effort = _resolve_reasoning_effort(selected_model, payload.reasoning_effort)
    if reasoning_effort:
        llm_kwargs["model_kwargs"] = {"reasoning_effort": reasoning_effort}
    return llm_kwargs


def _extract_response_text(response: object) -> str:
    """Extract response text from a LangChain response object."""

    if isinstance(response, str):
        return response
    content = getattr(response, "content", None)
    if isinstance(content, str):
        return content
    return ""


def _sanitize_freeform_output(raw_text: str) -> tuple[bool, str]:
    """Sanitize free-form output before display."""

    # Accept clean output immediately to avoid extra processing.
    ok, _ = validate_output(raw_text)
    if ok:
        return True, raw_text
    # Attempt to redact internal tags and retry validation.
    sanitized = sanitize_output(raw_text)
    ok, _ = validate_output(sanitized)
    if not ok:
        _LOGGER.warning("langchain_chat_output_blocked")
        return False, (
            "The model output contained unsafe content and could not be displayed. "
            "Please try again."
        )
    _LOGGER.info("langchain_chat_output_sanitized", extra={"raw_text_length": len(sanitized)})
    return True, sanitized


def generate_langchain_completion(payload: RequestPayload) -> tuple[bool, str]:
    """Generate a LangChain completion or return a refusal message."""

    request_meta = _payload_metadata(payload)
    _LOGGER.info("langchain_request_received", extra=request_meta)

    # Validate inputs before calling the model.
    ok, refusal = validate_inputs(
        payload.job_description, payload.cv_text, payload.user_prompt
    )
    if not ok:
        _LOGGER.info(
            "langchain_request_blocked",
            extra={**request_meta, "reason": "input_validation_failed"},
        )
        return False, refusal or "Input validation failed."

    # Select the prompt variant and build messages.
    variant = _select_variant(payload.prompt_variant_id)
    _LOGGER.info(
        "langchain_variant_selected",
        extra={"variant_id": variant.id, "variant_name": variant.name},
    )
    messages = build_messages(payload, variant)
    _LOGGER.info(
        "langchain_messages_built",
        extra={
            "message_count": len(messages),
            "system_message_length": len(messages[0]["content"]),
            "user_message_length": len(messages[1]["content"]),
        },
    )

    _load_dotenv_once()

    if ChatOpenAI is None:
        # Defer dependency errors to runtime so tests can still run without LangChain.
        _LOGGER.error("langchain_client_missing")
        raise RuntimeError(
            "LangChain OpenAI client is not installed. "
            "Install it with `pip install langchain-openai`."
        )

    # Build the LangChain client with the same model selection logic as the classic app.
    selected_model = payload.model_name or DEFAULT_MODEL
    llm_kwargs = _build_llm_kwargs(payload, selected_model)
    _LOGGER.info(
        "langchain_request",
        extra={
            "model": selected_model,
            "temperature": payload.temperature if payload.temperature is not None else "default",
            "reasoning_effort": payload.reasoning_effort or "default",
            "message_count": len(messages),
            "messages_total_length": sum(len(msg["content"]) for msg in messages),
        },
    )
    llm = ChatOpenAI(**llm_kwargs)

    # Invoke the model and return the raw text.
    response = llm.invoke(_build_langchain_messages(messages))
    return True, _extract_response_text(response)


def generate_langchain_questions(
    payload: RequestPayload,
) -> tuple[bool, dict[str, object] | str]:
    """Generate structured interview questions via LangChain."""

    # Start from the same LangChain completion path used in the wrapper.
    llm_start = time.monotonic()
    ok, raw_text = generate_langchain_completion(payload)
    llm_duration_ms = int((time.monotonic() - llm_start) * 1000)
    _LOGGER.info(
        "langchain_response_received",
        extra={
            "duration_ms": llm_duration_ms,
            "raw_text_length": len(raw_text),
            "ok": ok,
        },
    )
    if not ok:
        return False, raw_text

    # Parse the structured JSON output using the existing contract checker.
    parse_start = time.monotonic()
    ok, parsed = parse_structured_output(raw_text)
    parse_duration_ms = int((time.monotonic() - parse_start) * 1000)
    _LOGGER.info(
        "langchain_structured_output_parsed",
        extra={"duration_ms": parse_duration_ms, "ok": ok},
    )
    if not ok:
        return False, parsed
    return True, parsed


def generate_langchain_chat_response(payload: RequestPayload) -> tuple[bool, str]:
    """Generate a free-form chat response via LangChain."""

    request_meta = _payload_metadata(payload)
    _LOGGER.info("langchain_chat_request_received", extra=request_meta)

    # Allow larger prompts in chat because the history is serialized.
    ok, refusal = validate_chat_inputs(
        payload.job_description, payload.cv_text, payload.user_prompt
    )
    if not ok:
        _LOGGER.info(
            "langchain_chat_request_blocked",
            extra={**request_meta, "reason": "input_validation_failed"},
        )
        return False, refusal or "Input validation failed."

    # Select the chat prompt variant and build messages.
    variant = _select_chat_variant(payload.prompt_variant_id)
    _LOGGER.info(
        "langchain_chat_variant_selected",
        extra={"variant_id": variant.id, "variant_name": variant.name},
    )
    messages = build_messages(payload, variant)
    _LOGGER.info(
        "langchain_chat_messages_built",
        extra={
            "message_count": len(messages),
            "system_message_length": len(messages[0]["content"]),
            "user_message_length": len(messages[1]["content"]),
        },
    )

    _load_dotenv_once()

    if ChatOpenAI is None:
        # Defer dependency errors to runtime so tests can still run without LangChain.
        _LOGGER.error("langchain_client_missing")
        raise RuntimeError(
            "LangChain OpenAI client is not installed. "
            "Install it with `pip install langchain-openai`."
        )

    # Build the LangChain client with the same model selection logic as the classic app.
    selected_model = payload.model_name or DEFAULT_MODEL
    llm_kwargs = _build_llm_kwargs(payload, selected_model)
    _LOGGER.info(
        "langchain_chat_request",
        extra={
            "model": selected_model,
            "temperature": payload.temperature if payload.temperature is not None else "default",
            "reasoning_effort": payload.reasoning_effort or "default",
            "message_count": len(messages),
            "messages_total_length": sum(len(msg["content"]) for msg in messages),
        },
    )
    llm = ChatOpenAI(**llm_kwargs)

    # Invoke the model and sanitize the free-form response.
    response = llm.invoke(_build_langchain_messages(messages))
    raw_text = _extract_response_text(response)
    ok, sanitized = _sanitize_freeform_output(raw_text)
    if not ok:
        return False, sanitized
    return True, sanitized


def generate_langchain_cover_letter_response(payload: RequestPayload) -> tuple[bool, str]:
    """Generate a German cover letter via LangChain."""

    request_meta = _payload_metadata(payload)
    _LOGGER.info("langchain_cover_letter_request_received", extra=request_meta)

    # Require both JD and CV before attempting cover letter generation.
    if not _has_job_and_cv(payload):
        _LOGGER.info(
            "langchain_cover_letter_request_blocked",
            extra={**request_meta, "reason": "missing_jd_or_cv"},
        )
        return False, "Please provide both a job description and a CV to generate a cover letter."

    # Validate inputs with the chat limits because history is included.
    ok, refusal = validate_chat_inputs(
        payload.job_description, payload.cv_text, payload.user_prompt
    )
    if not ok:
        _LOGGER.info(
            "langchain_cover_letter_request_blocked",
            extra={**request_meta, "reason": "input_validation_failed"},
        )
        return False, refusal or "Input validation failed."

    # Build the cover letter prompt and call the LangChain chat endpoint.
    variant = get_cover_letter_prompt()
    _LOGGER.info(
        "langchain_cover_letter_prompt_selected",
        extra={"variant_id": variant.id, "variant_name": variant.name},
    )
    messages = build_messages(payload, variant)
    _LOGGER.info(
        "langchain_cover_letter_messages_built",
        extra={
            "message_count": len(messages),
            "system_message_length": len(messages[0]["content"]),
            "user_message_length": len(messages[1]["content"]),
        },
    )

    _load_dotenv_once()

    if ChatOpenAI is None:
        # Defer dependency errors to runtime so tests can still run without LangChain.
        _LOGGER.error("langchain_client_missing")
        raise RuntimeError(
            "LangChain OpenAI client is not installed. "
            "Install it with `pip install langchain-openai`."
        )

    # Build the LangChain client with the same model selection logic as the chat app.
    selected_model = payload.model_name or DEFAULT_MODEL
    llm_kwargs = _build_llm_kwargs(payload, selected_model)
    _LOGGER.info(
        "langchain_cover_letter_request",
        extra={
            "model": selected_model,
            "temperature": payload.temperature if payload.temperature is not None else "default",
            "reasoning_effort": payload.reasoning_effort or "default",
            "message_count": len(messages),
            "messages_total_length": sum(len(msg["content"]) for msg in messages),
        },
    )
    llm = ChatOpenAI(**llm_kwargs)

    # Invoke the model and sanitize the free-form response.
    response = llm.invoke(_build_langchain_messages(messages))
    raw_text = _extract_response_text(response)
    ok, sanitized = _sanitize_freeform_output(raw_text)
    if not ok:
        return False, sanitized
    return True, sanitized
