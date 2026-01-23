"""Controller orchestrating validation, prompt building, LLM call, and formatting."""

from __future__ import annotations

import logging
import time

from app.core.dataclasses import RequestPayload
from app.core.llm.openai_client import generate_completion
from app.core.prompt_builder import build_messages
from app.core.prompts import get_prompt_variants
from app.core.response_formatter import format_response
from app.core.safety import validate_inputs

_LOGGER = logging.getLogger(__name__)


def _select_variant(payload: RequestPayload):
    # Match the requested variant id, falling back to the first for safety.
    variants = get_prompt_variants()
    for variant in variants:
        if variant.id == payload.prompt_variant_id:
            return variant
    # Fall back to the first variant if the requested id is missing.
    _LOGGER.warning(
        "variant_fallback",
        extra={"requested_variant_id": payload.prompt_variant_id},
    )
    return variants[0]


def _payload_metadata(payload: RequestPayload) -> dict[str, int | float]:
    """Summarize payload sizes without logging raw user text."""

    # Length-only metadata keeps logs useful without exposing sensitive content.
    return {
        "job_description_length": len(payload.job_description),
        "cv_text_length": len(payload.cv_text),
        "user_prompt_length": len(payload.user_prompt),
        "prompt_variant_id": payload.prompt_variant_id,
        "temperature": payload.temperature,
    }


def generate_questions(payload: RequestPayload) -> tuple[bool, str]:
    """Generate interview questions or return a refusal message."""

    # Log request metadata at the entry point for traceability.
    request_meta = _payload_metadata(payload)
    _LOGGER.info("request_received", extra=request_meta)

    # Validate inputs before any model call.
    ok, refusal = validate_inputs(
        payload.job_description, payload.cv_text, payload.user_prompt
    )
    if not ok:
        # Record the refusal path without logging raw inputs.
        _LOGGER.info(
            "request_blocked",
            extra={**request_meta, "reason": "input_validation_failed"},
        )
        return False, refusal or "Input validation failed."

    # Assemble prompts, call the model, and enforce the response contract.
    variant = _select_variant(payload)
    _LOGGER.info(
        "variant_selected",
        extra={"variant_id": variant.id, "variant_name": variant.name},
    )
    messages = build_messages(payload, variant)
    _LOGGER.info(
        "messages_built",
        extra={
            "message_count": len(messages),
            "system_message_length": len(messages[0]["content"]),
            "user_message_length": len(messages[1]["content"]),
        },
    )
    llm_start = time.monotonic()
    raw_text = generate_completion(messages, payload.temperature)
    llm_duration_ms = int((time.monotonic() - llm_start) * 1000)
    _LOGGER.info(
        "llm_response_received",
        extra={"duration_ms": llm_duration_ms, "raw_text_length": len(raw_text)},
    )
    format_start = time.monotonic()
    formatted = format_response(raw_text, payload)
    format_duration_ms = int((time.monotonic() - format_start) * 1000)
    _LOGGER.info(
        "response_formatted",
        extra={
            "duration_ms": format_duration_ms,
            "formatted_length": len(formatted),
        },
    )
    return True, formatted
