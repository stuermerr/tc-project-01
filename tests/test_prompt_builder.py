from app.core.dataclasses import RequestPayload
from app.core.prompt_builder import build_messages
from app.core.prompts import get_prompt_variants


def test_build_messages_role_ordering():
    variant = get_prompt_variants()[0]
    payload = RequestPayload(
        job_description="Backend engineer role.",
        cv_text="Experience with Python and APIs.",
        user_prompt="Focus on backend systems.",
        prompt_variant_id=variant.id,
        temperature=0.3,
    )

    messages = build_messages(payload, variant)

    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == variant.system_prompt
    assert messages[1]["role"] == "user"


def test_build_messages_missing_fields_are_consistent():
    variant = get_prompt_variants()[0]
    payload = RequestPayload(
        job_description="",
        cv_text="",
        user_prompt="",
        prompt_variant_id=variant.id,
        temperature=0.2,
    )

    messages = build_messages(payload, variant)
    content = messages[1]["content"]

    assert "Job Description:\nNot provided." in content
    assert "CV / Resume:\nNot provided." in content
    assert "User Prompt:\nNot provided." in content
