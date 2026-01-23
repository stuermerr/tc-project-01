"""Prompt assembly for OpenAI chat messages."""

from __future__ import annotations

from app.core.dataclasses import PromptVariant, RequestPayload


def _normalize_field(text: str) -> str:
    # Normalize whitespace so empty fields are handled consistently.
    stripped = text.strip()
    # Use a consistent placeholder so the LLM knows the field is intentionally empty.
    return stripped if stripped else "Not provided."


def build_messages(
    payload: RequestPayload, variant: PromptVariant
) -> list[dict[str, str]]:
    """Build system and user messages from the request payload."""

    # Keep the user message structure stable for easier testing and formatting.
    user_content = (
        "Job Description:\n"
        f"{_normalize_field(payload.job_description)}\n\n"
        "CV / Resume:\n"
        f"{_normalize_field(payload.cv_text)}\n\n"
        "User Prompt:\n"
        f"{_normalize_field(payload.user_prompt)}"
    )

    # Return messages in the order expected by the chat API.
    return [
        {"role": "system", "content": variant.system_prompt},
        {"role": "user", "content": user_content},
    ]
