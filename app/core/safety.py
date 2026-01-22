"""Safety guardrails for user inputs."""

from __future__ import annotations

import re
from typing import Iterable

MAX_JOB_DESCRIPTION_LENGTH = 3000
MAX_CV_LENGTH = 3000
MAX_USER_PROMPT_LENGTH = 2000

# Heuristic patterns for common prompt-injection attempts.
_INJECTION_PATTERNS: Iterable[re.Pattern[str]] = (
    re.compile(r"\bignore (all|previous|prior) instructions\b"),
    re.compile(r"\bdisregard (all|previous|prior) instructions\b"),
    re.compile(r"\boverride (all|previous|prior) instructions\b"),
    re.compile(r"\b(system|developer|assistant) prompt\b"),
    re.compile(r"\breveal (the )?system prompt\b"),
    re.compile(r"\bshow (the )?system prompt\b"),
    re.compile(r"\bprompt injection\b"),
    re.compile(r"\bjailbreak\b"),
    re.compile(r"\bdo anything now\b"),
    re.compile(r"\bDAN\b"),
    re.compile(r"\bpolicy bypass\b"),
    re.compile(r"\binternal instructions\b"),
    re.compile(r"\bchain[- ]of[- ]thought\b"),
)


def _matches_injection(text: str) -> bool:
    lowered = text.lower()
    return any(pattern.search(lowered) for pattern in _INJECTION_PATTERNS)


def _check_length(label: str, text: str, limit: int) -> tuple[bool, str | None]:
    if len(text) > limit:
        return False, (
            f"{label} is too long ({len(text)} chars). Max allowed is {limit}."
        )
    return True, None


def validate_inputs(
    job_description: str, cv_text: str, user_prompt: str
) -> tuple[bool, str | None]:
    """Validate user inputs and reject unsafe requests."""

    for label, text, limit in (
        ("Job description", job_description, MAX_JOB_DESCRIPTION_LENGTH),
        ("CV", cv_text, MAX_CV_LENGTH),
        ("User prompt", user_prompt, MAX_USER_PROMPT_LENGTH),
    ):
        ok, message = _check_length(label, text, limit)
        if not ok:
            return False, message

    # Check combined inputs so cross-field instructions are still caught.
    combined = "\n".join([job_description, cv_text, user_prompt])
    if _matches_injection(combined):
        return False, (
            "Input appears to include prompt-injection instructions. "
            "Please remove them and try again."
        )

    return True, None
