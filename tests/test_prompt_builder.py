from app.core.dataclasses import RequestPayload
from app.core.prompt_builder import build_messages
from app.core.prompts import get_prompt_variants


def test_build_messages_role_ordering():
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
    assert messages[0]["content"] == variant.system_prompt
    assert messages[1]["role"] == "user"


def test_build_messages_missing_fields_are_consistent():
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
    assert "Job Description:\nNot provided." in content
    assert "CV / Resume:\nNot provided." in content
    assert "User Prompt:\nNot provided." in content
