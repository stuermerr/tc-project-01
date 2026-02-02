"""Controller orchestrating validation, prompt building, LLM call, and parsing."""

from __future__ import annotations

import json
import logging
import time

from app.core.dataclasses import RequestPayload
from app.core.llm.openai_client import generate_chat_completion, generate_completion
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
from app.core.structured_output import validate_structured_response

_LOGGER = logging.getLogger(__name__)

_REQUIRED_RESPONSE_KEYS = {
    "target_role_context",
    "cv_note",
    "alignments",
    "gaps_or_risk_areas",
    "interview_questions",
    "next_step_suggestions",
}


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


def _select_chat_variant(payload: RequestPayload):
    # Match the requested chat variant id, falling back to the first for safety.
    variants = get_chat_prompt_variants()
    for variant in variants:
        if variant.id == payload.prompt_variant_id:
            return variant
    # Fall back to the first variant if the requested id is missing.
    _LOGGER.warning(
        "chat_variant_fallback",
        extra={"requested_variant_id": payload.prompt_variant_id},
    )
    return variants[0]


def _has_job_and_cv(payload: RequestPayload) -> bool:
    """Return True when both JD and CV are present."""

    # Cover letters require both inputs to be meaningful.
    return bool(payload.job_description.strip()) and bool(payload.cv_text.strip())


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


def _sanitize_freeform_output(raw_text: str) -> tuple[bool, str]:
    """Sanitize free-form output before display."""

    ok, _ = validate_output(raw_text)
    if ok:
        return True, raw_text
    sanitized = sanitize_output(raw_text)
    ok, _ = validate_output(sanitized)
    if not ok:
        _LOGGER.warning("chat_output_blocked")
        return False, (
            "The model output contained unsafe content and could not be displayed. "
            "Please try again."
        )
    _LOGGER.info("chat_output_sanitized", extra={"raw_text_length": len(sanitized)})
    return True, sanitized



def _parse_structured_output(raw_text: str) -> tuple[bool, dict[str, object] | str]:
    """Parse structured JSON output and return a dict or error message."""

    # Ensure model output does not leak internal tags before parsing.
    ok, _ = validate_output(raw_text)
    if not ok:
        sanitized = sanitize_output(raw_text)
        ok, _ = validate_output(sanitized)
        if not ok:
            _LOGGER.warning("structured_output_blocked")
            return False, (
                "The model output contained unsafe content and could not be displayed. "
                "Please try again."
            )
        raw_text = sanitized
        _LOGGER.info("structured_output_sanitized", extra={"raw_text_length": len(raw_text)})

    # Parse the JSON response while avoiding raw-content logging.
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        _LOGGER.error("structured_output_parse_failed", extra={"reason": "json_decode"})
        return False, "The model returned invalid JSON. Please try again."

    if not isinstance(parsed, dict):
        _LOGGER.error("structured_output_parse_failed", extra={"reason": "not_object"})
        return False, "The model returned an unexpected JSON shape. Please try again."

    missing = _REQUIRED_RESPONSE_KEYS.difference(parsed.keys())
    if missing:
        _LOGGER.error(
            "structured_output_parse_failed",
            extra={"reason": "missing_keys", "missing_count": len(missing)},
        )
        return False, "The model response was missing required fields. Please try again."

    ok, message = validate_structured_response(parsed)
    if not ok:
        _LOGGER.error(
            "structured_output_parse_failed",
            extra={"reason": "contract_validation_failed"},
        )
        return False, message or "The model response did not match the required format."

    return True, parsed


def generate_questions(payload: RequestPayload) -> tuple[bool, dict[str, object] | str]:
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
    ok, raw_text = generate_completion(
        messages,
        payload.temperature,
        model_name=payload.model_name,
        reasoning_effort=payload.reasoning_effort,
    )
    llm_duration_ms = int((time.monotonic() - llm_start) * 1000)
    _LOGGER.info(
        "llm_response_received",
        extra={
            "duration_ms": llm_duration_ms,
            "raw_text_length": len(raw_text),
        },
    )
    if not ok:
        _LOGGER.info("llm_refusal")
        return False, raw_text

    parse_start = time.monotonic()
    ok, parsed = _parse_structured_output(raw_text)
    parse_duration_ms = int((time.monotonic() - parse_start) * 1000)
    _LOGGER.info(
        "structured_output_parsed",
        extra={"duration_ms": parse_duration_ms, "ok": ok},
    )
    if not ok:
        return False, parsed
    return True, parsed


def generate_chat_response(payload: RequestPayload) -> tuple[bool, str]:
    """Generate a free-form chat response or return a refusal message."""

    request_meta = _payload_metadata(payload)
    _LOGGER.info("chat_request_received", extra=request_meta)

    # Allow larger prompts in chat because the history is serialized.
    ok, refusal = validate_chat_inputs(
        payload.job_description, payload.cv_text, payload.user_prompt
    )
    if not ok:
        _LOGGER.info(
            "chat_request_blocked",
            extra={**request_meta, "reason": "input_validation_failed"},
        )
        return False, refusal or "Input validation failed."

    variant = _select_chat_variant(payload)
    _LOGGER.info(
        "chat_variant_selected",
        extra={"variant_id": variant.id, "variant_name": variant.name},
    )
    messages = build_messages(payload, variant)
    _LOGGER.info(
        "chat_messages_built",
        extra={
            "message_count": len(messages),
            "system_message_length": len(messages[0]["content"]),
            "user_message_length": len(messages[1]["content"]),
        },
    )
    llm_start = time.monotonic()
    ok, raw_text = generate_chat_completion(
        messages,
        payload.temperature,
        model_name=payload.model_name,
        reasoning_effort=payload.reasoning_effort,
    )
    llm_duration_ms = int((time.monotonic() - llm_start) * 1000)
    _LOGGER.info(
        "chat_llm_response_received",
        extra={
            "duration_ms": llm_duration_ms,
            "raw_text_length": len(raw_text),
        },
    )
    if not ok:
        _LOGGER.info("chat_llm_refusal")
        return False, raw_text

    ok, sanitized = _sanitize_freeform_output(raw_text)
    if not ok:
        return False, sanitized
    return True, sanitized


def generate_cover_letter_response(payload: RequestPayload) -> tuple[bool, str]:
    """Generate a German cover letter or return a refusal message."""

    request_meta = _payload_metadata(payload)
    _LOGGER.info("cover_letter_request_received", extra=request_meta)

    # Require both JD and CV before attempting cover letter generation.
    if not _has_job_and_cv(payload):
        _LOGGER.info(
            "cover_letter_request_blocked",
            extra={**request_meta, "reason": "missing_jd_or_cv"},
        )
        return False, "Please provide both a job description and a CV to generate a cover letter."

    # Validate inputs with the chat limits because history is included.
    ok, refusal = validate_chat_inputs(
        payload.job_description, payload.cv_text, payload.user_prompt
    )
    if not ok:
        _LOGGER.info(
            "cover_letter_request_blocked",
            extra={**request_meta, "reason": "input_validation_failed"},
        )
        return False, refusal or "Input validation failed."

    # Build the cover letter prompt and call the chat completion endpoint.
    variant = get_cover_letter_prompt()
    _LOGGER.info(
        "cover_letter_prompt_selected",
        extra={"variant_id": variant.id, "variant_name": variant.name},
    )
    messages = build_messages(payload, variant)
    _LOGGER.info(
        "cover_letter_messages_built",
        extra={
            "message_count": len(messages),
            "system_message_length": len(messages[0]["content"]),
            "user_message_length": len(messages[1]["content"]),
        },
    )
    llm_start = time.monotonic()
    ok, raw_text = generate_chat_completion(
        messages,
        payload.temperature,
        model_name=payload.model_name,
        reasoning_effort=payload.reasoning_effort,
    )
    llm_duration_ms = int((time.monotonic() - llm_start) * 1000)
    _LOGGER.info(
        "cover_letter_llm_response_received",
        extra={
            "duration_ms": llm_duration_ms,
            "raw_text_length": len(raw_text),
        },
    )
    if not ok:
        _LOGGER.info("cover_letter_llm_refusal")
        return False, raw_text

    ok, sanitized = _sanitize_freeform_output(raw_text)
    if not ok:
        return False, sanitized
    return True, sanitized
