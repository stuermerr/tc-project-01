"""Typed data models for request payloads and prompt variants."""

from __future__ import annotations

from dataclasses import dataclass

# Simple containers to keep cross-module interfaces explicit.


# Immutable payload container keeps request data consistent across layers.
@dataclass(frozen=True)
class RequestPayload:
    """Inputs required to generate interview questions."""

    job_description: str
    cv_text: str
    user_prompt: str
    prompt_variant_id: int
    temperature: float


# Immutable variant container avoids accidental prompt mutation.
@dataclass(frozen=True)
class PromptVariant:
    """System prompt variant metadata and content."""

    id: int
    name: str
    system_prompt: str
