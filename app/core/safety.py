"""Safety guardrails for user inputs."""

from __future__ import annotations

import re
import secrets
from typing import Iterable

# Length limits keep payloads bounded for safety and cost.
MAX_JOB_DESCRIPTION_LENGTH = 3000
MAX_CV_LENGTH = 3000
MAX_USER_PROMPT_LENGTH = 2000

# Heuristic patterns for common prompt-injection attempts.
_INJECTION_PATTERNS: Iterable[re.Pattern[str]] = (
    re.compile(r"\bignore (all|previous|prior) instructions\b"),
    re.compile(r"\bdisregard (all|previous|prior) instructions\b"),
    re.compile(r"\boverride (all|previous|prior) instructions\b"),
    re.compile(r"\bforget (all|previous|prior) instructions\b"),
    re.compile(r"\byou are now\b"),
    re.compile(r"\bact as\b"),
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
_CONTROL_CHAR_PATTERN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")
_OUTPUT_FORBIDDEN_PATTERNS: Iterable[re.Pattern[str]] = (
    re.compile(r"</?user-(job|cv|prompt)-[a-f0-9]+>", re.IGNORECASE),
    re.compile(r"\bsystem prompt\b", re.IGNORECASE),
)


def _matches_injection(text: str) -> bool:
    # Normalize case so pattern checks are consistent.
    lowered = text.lower()
    return any(pattern.search(lowered) for pattern in _INJECTION_PATTERNS)


def _check_length(label: str, text: str, limit: int) -> tuple[bool, str | None]:
    # Fail early on oversized inputs so the UI can show a clear message.
    if len(text) > limit:
        return False, (
            f"{label} is too long ({len(text)} chars). Max allowed is {limit}."
        )
    return True, None


def _check_control_characters(label: str, text: str) -> tuple[bool, str | None]:
    # Reject invisible control characters while allowing common whitespace.
    if _CONTROL_CHAR_PATTERN.search(text):
        return False, (
            f"{label} contains non-printable characters. "
            "Please remove them and try again."
        )
    return True, None


def validate_output(raw_text: str) -> tuple[bool, str | None]:
    """Detect unsafe model output that leaks internal details."""

    # Block outputs that include internal tags or system prompt references.
    if any(pattern.search(raw_text) for pattern in _OUTPUT_FORBIDDEN_PATTERNS):
        return False, (
            "The model output contained internal instructions or tags and was blocked."
        )
    return True, None


def sanitize_output(raw_text: str) -> str:
    """Remove internal tags or system prompt references from model output."""

    sanitized = raw_text
    # Strip salted tags while preserving surrounding content.
    sanitized = re.sub(
        r"</?user-(job|cv|prompt)-[a-f0-9]+>", "", sanitized, flags=re.IGNORECASE
    )
    # Redact explicit mentions of the system prompt.
    sanitized = re.sub(r"(?i)\bsystem prompt\b", "[redacted]", sanitized)
    return sanitized


def generate_salt(num_bytes: int = 6) -> str:
    """Return a random hex salt for per-request tag names."""

    # Use cryptographic randomness so tag names are not guessable.
    return secrets.token_hex(num_bytes)


def build_salted_tag_names(salt: str) -> dict[str, str]:
    """Build per-request tag names for untrusted user input."""

    return {
        "job_description": f"user-job-{salt}",
        "cv_text": f"user-cv-{salt}",
        "user_prompt": f"user-prompt-{salt}",
    }


def _is_high_confidence(result: object) -> bool:
    # Normalize common ML detector outputs into a high-confidence decision.
    if isinstance(result, bool):
        return result
    if isinstance(result, (int, float)):
        return result >= 0.8
    if isinstance(result, dict):
        for key in ("score", "confidence", "probability"):
            value = result.get(key)
            if isinstance(value, (int, float)) and value >= 0.8:
                return True
    return False


def _ml_injection_check(text: str) -> bool:
    # Attempt ML-based injection detection when the optional dependency exists.
    try:
        import pytector
    except Exception:
        return False

    try:
        if hasattr(pytector, "detect") and callable(pytector.detect):
            score = pytector.detect(text)
        elif hasattr(pytector, "Pytector"):
            detector = pytector.Pytector()
            score = detector.detect(text)
        else:
            return False
    except Exception:
        return False

    return _is_high_confidence(score)


def validate_inputs(
    job_description: str, cv_text: str, user_prompt: str
) -> tuple[bool, str | None]:
    """Validate user inputs and reject unsafe requests."""

    # Validate each field independently to give precise feedback.
    for label, text, limit in (
        ("Job description", job_description, MAX_JOB_DESCRIPTION_LENGTH),
        ("CV", cv_text, MAX_CV_LENGTH),
        ("User prompt", user_prompt, MAX_USER_PROMPT_LENGTH),
    ):
        ok, message = _check_length(label, text, limit)
        if not ok:
            return False, message
        ok, message = _check_control_characters(label, text)
        if not ok:
            return False, message

    # Check combined inputs so cross-field instructions are still caught.
    combined = "\n".join([job_description, cv_text, user_prompt])
    if _matches_injection(combined):
        return False, (
            "Input appears to include prompt-injection instructions. "
            "Please remove them and try again."
        )

    # Run optional ML-based detection and fail closed on high-confidence hits.
    if _ml_injection_check(combined):
        return False, (
            "Input appears to be a prompt-injection attempt. "
            "Please remove it and try again."
        )

    # No issues found; allow the request to proceed.
    return True, None
