"""Tests for the controller orchestration layer."""

from app.core.orchestration import generate_chat_response, generate_questions
from app.core.dataclasses import RequestPayload


def test_generate_questions_short_circuits_on_safety(monkeypatch):
    """Verify generate questions short circuits on safety."""
    # Fake a safety failure to ensure the controller stops early.
    def _fail_validation(job_description: str, cv_text: str, user_prompt: str):
        return False, "blocked"

    # Guard against accidental LLM calls in the refusal path.
    def _unexpected_call(*args, **kwargs):  # pragma: no cover - should not be called
        raise AssertionError("LLM should not be called when validation fails")

    # Patch dependencies so the test only exercises controller flow.
    monkeypatch.setattr("app.core.orchestration.validate_inputs", _fail_validation)
    monkeypatch.setattr("app.core.orchestration.generate_completion", _unexpected_call)

    # Build a minimal payload that triggers the safety failure.
    payload = RequestPayload(
        job_description="bad",
        cv_text="",
        user_prompt="",
        prompt_variant_id=1,
        temperature=0.2,
    )

    # Execute the controller and capture the refusal message.
    ok, message = generate_questions(payload)

    assert ok is False
    assert message == "blocked"


def test_generate_questions_success_path(monkeypatch):
    """Verify generate questions success path."""
    # Allow validation to pass so we can test the happy path.
    def _pass_validation(job_description: str, cv_text: str, user_prompt: str):
        return True, None

    # Fake the LLM response to keep the test deterministic.
    def _fake_completion(messages, temperature, model_name=None, reasoning_effort=None):
        assert messages
        assert temperature == 0.4
        return True, (
            '{"target_role_context":["Role summary"],'
            '"cv_note":null,'
            '"alignments":["Alignment"],'
            '"gaps_or_risk_areas":["Gap"],'
            '"interview_questions":['
            '"[Technical] Question one?",'
            '"[Behavioral] Question two?",'
            '"[Role-specific] Question three?",'
            '"[Screening] Question four?",'
            '"[Onsite] Question five?"'
            '],'
            '"next_step_suggestions":["Next step","Another step"]}'
        )

    # Patch dependencies to isolate the controller behavior.
    monkeypatch.setattr("app.core.orchestration.validate_inputs", _pass_validation)
    monkeypatch.setattr("app.core.orchestration.generate_completion", _fake_completion)

    # Build a valid payload for the success path.
    payload = RequestPayload(
        job_description="JD",
        cv_text="CV",
        user_prompt="Prompt",
        prompt_variant_id=1,
        temperature=0.4,
    )

    # Execute the controller and verify the structured result.
    ok, message = generate_questions(payload)

    assert ok is True
    assert isinstance(message, dict)
    assert len(message["interview_questions"]) == 5


def test_generate_chat_response_returns_text(monkeypatch):
    """Verify generate chat response returns text."""
    # Allow validation to pass so we can test the chat path.
    def _pass_validation(job_description: str, cv_text: str, user_prompt: str):
        return True, None

    # Fake the chat completion to keep the test deterministic.
    def _fake_chat_completion(messages, temperature, model_name=None, reasoning_effort=None):
        assert messages
        assert temperature == 0.3
        return True, "Coach reply"

    # Guard against structured parsing in the chat path.
    def _unexpected_parse(*args, **kwargs):  # pragma: no cover - should not be called
        raise AssertionError("Structured output parsing should be skipped for chat")

    monkeypatch.setattr("app.core.orchestration.validate_inputs", _pass_validation)
    monkeypatch.setattr(
        "app.core.orchestration.generate_chat_completion", _fake_chat_completion
    )
    monkeypatch.setattr(
        "app.core.orchestration._parse_structured_output", _unexpected_parse
    )

    payload = RequestPayload(
        job_description="JD",
        cv_text="CV",
        user_prompt="Prompt",
        prompt_variant_id=101,
        temperature=0.3,
    )

    ok, message = generate_chat_response(payload)

    assert ok is True
    assert message == "Coach reply"
