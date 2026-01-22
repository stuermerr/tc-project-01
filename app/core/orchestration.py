"""Controller orchestrating validation, prompt building, LLM call, and formatting."""

from __future__ import annotations

from app.core.dataclasses import RequestPayload
from app.core.llm.openai_client import generate_completion
from app.core.prompt_builder import build_messages
from app.core.prompts import get_prompt_variants
from app.core.response_formatter import format_response
from app.core.safety import validate_inputs


def _select_variant(payload: RequestPayload):
    variants = get_prompt_variants()
    for variant in variants:
        if variant.id == payload.prompt_variant_id:
            return variant
    # Fall back to the first variant if the requested id is missing.
    return variants[0]


def generate_questions(payload: RequestPayload) -> tuple[bool, str]:
    """Generate interview questions or return a refusal message."""

    ok, refusal = validate_inputs(
        payload.job_description, payload.cv_text, payload.user_prompt
    )
    if not ok:
        return False, refusal or "Input validation failed."

    variant = _select_variant(payload)
    messages = build_messages(payload, variant)
    raw_text = generate_completion(messages, payload.temperature)
    formatted = format_response(raw_text, payload)
    return True, formatted
