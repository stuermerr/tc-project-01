"""Typed data models for request payloads and prompt variants."""

from __future__ import annotations

from dataclasses import dataclass

from app.core.model_catalog import DEFAULT_MODEL

# Simple containers to keep cross-module interfaces explicit.


# Immutable payload container keeps request data consistent across layers.
@dataclass(frozen=True)
class RequestPayload:
    """Inputs required to generate interview questions."""

    job_description: str
    cv_text: str
    user_prompt: str
    prompt_variant_id: int
    temperature: float | None
    model_name: str = DEFAULT_MODEL
    reasoning_effort: str | None = None
    verbosity: str | None = None


# Immutable variant container avoids accidental prompt mutation.
@dataclass(frozen=True)
class PromptVariant:
    """System prompt variant metadata and content."""

    id: int
    name: str
    system_prompt: str
