"""Tests for prompt builder message assembly."""

import re

from app.core.dataclasses import RequestPayload
from app.core.prompt_builder import build_messages
from app.core.prompts import get_prompt_variants


def _extract_tag(content: str, label: str) -> str | None:
    # Pull the salted tag name out of the message content.
    match = re.search(rf"<(user-{label}-[a-f0-9]+)>", content)
    return match.group(1) if match else None


def test_build_messages_role_ordering():
    """Verify build messages role ordering."""
    # Use the first variant to keep the test stable.
    variant = get_prompt_variants()[0]
    # Build a payload with all fields filled to test full output.
    payload = RequestPayload(
        job_description="Backend engineer role.",
        cv_text="Experience with Python and APIs.",
        user_prompt="Focus on backend systems.",
        prompt_variant_id=variant.id,
        temperature=0.3,
    )

    # Build the message list that will be sent to the LLM.
    messages = build_messages(payload, variant)

    # Validate role ordering and system prompt usage.
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert variant.system_prompt in messages[0]["content"]
    assert messages[1]["role"] == "user"
    assert _extract_tag(messages[1]["content"], "job") is not None
    assert _extract_tag(messages[1]["content"], "cv") is not None
    assert _extract_tag(messages[1]["content"], "prompt") is not None


def test_build_messages_missing_fields_are_consistent():
    """Verify build messages missing fields are consistent."""
    # Use a minimal payload to verify placeholder behavior.
    variant = get_prompt_variants()[0]
    payload = RequestPayload(
        job_description="",
        cv_text="",
        user_prompt="",
        prompt_variant_id=variant.id,
        temperature=0.2,
    )

    # Build messages and inspect the user content.
    messages = build_messages(payload, variant)
    content = messages[1]["content"]

    # Ensure placeholders are consistent across missing fields.
    assert "Not provided." in content
    assert content.count("Not provided.") == 3


def test_build_messages_generate_unique_salts():
    """Verify build messages generate unique salts."""
    # Different calls should yield distinct salted tags.
    variant = get_prompt_variants()[0]
    payload = RequestPayload(
        job_description="Role.",
        cv_text="CV.",
        user_prompt="Prompt.",
        prompt_variant_id=variant.id,
        temperature=0.2,
    )

    first = build_messages(payload, variant)[1]["content"]
    second = build_messages(payload, variant)[1]["content"]

    assert _extract_tag(first, "job") != _extract_tag(second, "job")
