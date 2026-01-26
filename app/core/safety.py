"""Safety guardrails for user inputs."""

from __future__ import annotations

import re
import secrets
import logging
import time
from typing import Iterable

# Optional import so tests can run without the dependency installed.
try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - exercised when dependency is missing
    OpenAI = None

# Length limits keep payloads bounded for safety and cost.
MAX_JOB_DESCRIPTION_LENGTH = 6000
MAX_CV_LENGTH = 4000
MAX_USER_PROMPT_LENGTH = 2000
MAX_CHAT_USER_PROMPT_LENGTH = 30000

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
_HARMFUL_DIRECT_PATTERNS: Iterable[re.Pattern[str]] = (
    re.compile(r"\b(make|build|create|assemble)\b.*\b(bomb|explosive|pipe bomb|molotov)\b"),
    re.compile(
        r"\b(kill|murder|assassinat|poison)\b.*\b"
        r"(person|people|someone|them|him|her|myself|yourself|himself|herself)\b"
    ),
    re.compile(r"\b(kill myself|suicide|self-harm|hurt myself)\b"),
    re.compile(r"\b(hack into|bypass (?:login|authentication)|crack (?:a )?password)\b"),
    re.compile(r"\b(write|deploy|distribute|spread)\b.*\b(malware|ransomware)\b"),
    re.compile(r"\b(steal|stolen|stealing)\b.*\b(credit card|identity|money)\b"),
)
_ILLEGAL_INTENT_PATTERNS: Iterable[re.Pattern[str]] = (
    re.compile(r"\bhow to\b"),
    re.compile(r"\bhelp me\b"),
    re.compile(r"\bteach me\b"),
    re.compile(r"\bstep[- ]by[- ]step\b"),
    re.compile(r"\binstructions?\b"),
    re.compile(r"\bguide me\b"),
    re.compile(r"\bways to\b"),
    re.compile(r"\bi want to\b"),
    re.compile(r"\bi need to\b"),
    re.compile(r"\bcan you\b"),
)
_ILLEGAL_TARGET_PATTERNS: Iterable[re.Pattern[str]] = (
    re.compile(r"\bbomb\b"),
    re.compile(r"\bexplosive\b"),
    re.compile(r"\bpipe bomb\b"),
    re.compile(r"\bmolotov\b"),
    re.compile(r"\bkill\b"),
    re.compile(r"\bmurder\b"),
    re.compile(r"\bassassinat"),
    re.compile(r"\bpoison\b"),
    re.compile(r"\bsuicide\b"),
    re.compile(r"\bself[- ]harm\b"),
    re.compile(r"\bphish\b"),
    re.compile(r"\bphishing\b"),
    re.compile(r"\bransomware\b"),
    re.compile(r"\bmalware\b"),
    re.compile(r"\bhack into\b"),
    re.compile(r"\bbypass (?:login|authentication)\b"),
    re.compile(r"\bcrack (?:a )?password\b"),
    re.compile(r"\bcredit card fraud\b"),
    re.compile(r"\bidentity theft\b"),
)
_CONTROL_CHAR_PATTERN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")
_OUTPUT_FORBIDDEN_PATTERNS: Iterable[re.Pattern[str]] = (
    re.compile(r"</?user-(job|cv|prompt)-[a-f0-9]+>", re.IGNORECASE),
    re.compile(r"\bsystem prompt\b", re.IGNORECASE),
)
_SAFETY_EVENT_COUNTS: dict[str, int] = {}
_SAFETY_LOGGER = logging.getLogger(__name__)
_RATE_LIMIT_BUCKETS: dict[str, list[float]] = {}
_RATE_LIMIT_WINDOW_SECONDS = 30
_RATE_LIMIT_MAX_REQUESTS = 5
_MODERATION_MODEL = "omni-moderation-latest"


def _matches_injection(text: str) -> bool:
    # Normalize case so pattern checks are consistent.
    lowered = text.lower()
    return any(pattern.search(lowered) for pattern in _INJECTION_PATTERNS)


def _matches_illegal_or_harmful(text: str) -> bool:
    """Return True when text includes obvious illegal or harmful intent."""

    lowered = text.lower()
    if any(pattern.search(lowered) for pattern in _HARMFUL_DIRECT_PATTERNS):
        return True
    has_intent = any(pattern.search(lowered) for pattern in _ILLEGAL_INTENT_PATTERNS)
    if not has_intent:
        return False
    return any(pattern.search(lowered) for pattern in _ILLEGAL_TARGET_PATTERNS)


def _moderation_flagged(text: str) -> bool | None:
    """Return True if OpenAI moderation flags the text, False if clean, or None if skipped."""

    # Skip moderation when the client is unavailable or there is no content to review.
    if OpenAI is None:
        return None
    if not text.strip():
        return None
    try:
        client = OpenAI()
        response = client.moderations.create(model=_MODERATION_MODEL, input=text)
    except Exception:
        # Fail open so validation still works if the moderation API is unavailable.
        return None
    # OpenAI moderation responses include a flagged boolean per result.
    results = getattr(response, "results", None)
    if not results:
        return None
    flagged = getattr(results[0], "flagged", None)
    if isinstance(flagged, bool):
        return flagged
    return None


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


def _redact_details(details: dict | None) -> dict | None:
    # Drop or summarize details to avoid logging sensitive user text.
    if not details:
        return None
    redacted: dict[str, object] = {}
    for key, value in details.items():
        if isinstance(value, str):
            redacted[key] = "<redacted>"
        else:
            redacted[key] = value
    return redacted


def record_safety_event(event_type: str, details: dict | None = None) -> None:
    """Record a safety event with privacy-aware logging."""

    _SAFETY_EVENT_COUNTS[event_type] = _SAFETY_EVENT_COUNTS.get(event_type, 0) + 1
    _SAFETY_LOGGER.info(
        "safety_event",
        extra={
            "event_type": event_type,
            "details": _redact_details(details),
            "count": _SAFETY_EVENT_COUNTS[event_type],
        },
    )


def check_rate_limit(key: str, now: float | None = None) -> tuple[bool, str | None]:
    """Check whether the key has exceeded the configured request rate."""

    # Use the current wall time unless tests pass a fixed value.
    timestamp = time.time() if now is None else now
    window_start = timestamp - _RATE_LIMIT_WINDOW_SECONDS
    bucket = _RATE_LIMIT_BUCKETS.setdefault(key or "anonymous", [])
    # Trim old entries to keep memory bounded.
    bucket[:] = [entry for entry in bucket if entry >= window_start]
    if len(bucket) >= _RATE_LIMIT_MAX_REQUESTS:
        record_safety_event("rate_limited", {"key": key})
        return False, "Too many requests. Please wait a moment and try again."
    bucket.append(timestamp)
    return True, None


def validate_output(raw_text: str) -> tuple[bool, str | None]:
    """Detect unsafe model output that leaks internal details."""

    # Block outputs that include internal tags or system prompt references.
    if any(pattern.search(raw_text) for pattern in _OUTPUT_FORBIDDEN_PATTERNS):
        record_safety_event("output_blocked", {"reason": "internal_leak"})
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
    if sanitized != raw_text:
        record_safety_event("output_sanitized")
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


def _validate_inputs_with_limits(
    job_description: str,
    cv_text: str,
    user_prompt: str,
    user_prompt_limit: int,
) -> tuple[bool, str | None]:
    """Validate inputs against the provided user prompt length limit."""

    # Validate each field independently to give precise feedback.
    for label, text, limit in (
        ("Job description", job_description, MAX_JOB_DESCRIPTION_LENGTH),
        ("CV", cv_text, MAX_CV_LENGTH),
        ("User prompt", user_prompt, user_prompt_limit),
    ):
        ok, message = _check_length(label, text, limit)
        if not ok:
            record_safety_event(
                "input_length_exceeded",
                {"field": label, "length": len(text), "limit": limit},
            )
            return False, message
        ok, message = _check_control_characters(label, text)
        if not ok:
            record_safety_event(
                "input_control_characters",
                {"field": label, "length": len(text)},
            )
            return False, message

    # Check combined inputs so cross-field instructions are still caught.
    combined = "\n".join([job_description, cv_text, user_prompt])
    if _matches_injection(combined):
        record_safety_event("input_injection_detected")
        return False, (
            "Input appears to include prompt-injection instructions. "
            "Please remove them and try again."
        )

    # Reject obvious illegal or harmful requests without scanning across fields.
    for label, text in (
        ("Job description", job_description),
        ("CV", cv_text),
        ("User prompt", user_prompt),
    ):
        if _matches_illegal_or_harmful(text):
            record_safety_event("input_illegal_or_harmful", {"field": label})
            return False, (
                "Input appears to request illegal or harmful activity. "
                "Please remove it and try again."
            )

    # Use OpenAI moderation to catch harmful intent that slips past heuristics.
    moderation_flagged = _moderation_flagged(combined)
    if moderation_flagged:
        record_safety_event("input_moderation_flagged")
        return False, (
            "Input appears to request illegal or harmful activity. "
            "Please remove it and try again."
        )

    # No issues found; allow the request to proceed.
    return True, None


def validate_inputs(
    job_description: str, cv_text: str, user_prompt: str
) -> tuple[bool, str | None]:
    """Validate classic UI inputs and reject unsafe requests."""

    return _validate_inputs_with_limits(
        job_description, cv_text, user_prompt, MAX_USER_PROMPT_LENGTH
    )


def validate_chat_inputs(
    job_description: str, cv_text: str, user_prompt: str
) -> tuple[bool, str | None]:
    """Validate chat inputs with a larger user prompt limit."""

    return _validate_inputs_with_limits(
        job_description, cv_text, user_prompt, MAX_CHAT_USER_PROMPT_LENGTH
    )
