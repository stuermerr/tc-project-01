from app.core.orchestration import generate_questions
from app.core.dataclasses import RequestPayload


def test_generate_questions_short_circuits_on_safety(monkeypatch):
    def _fail_validation(job_description: str, cv_text: str, user_prompt: str):
        return False, "blocked"

    def _unexpected_call(*args, **kwargs):  # pragma: no cover - should not be called
        raise AssertionError("LLM should not be called when validation fails")

    monkeypatch.setattr("app.core.orchestration.validate_inputs", _fail_validation)
    monkeypatch.setattr("app.core.orchestration.generate_completion", _unexpected_call)

    payload = RequestPayload(
        job_description="bad",
        cv_text="",
        user_prompt="",
        prompt_variant_id=1,
        temperature=0.2,
    )

    ok, message = generate_questions(payload)

    assert ok is False
    assert message == "blocked"


def test_generate_questions_success_path(monkeypatch):
    def _pass_validation(job_description: str, cv_text: str, user_prompt: str):
        return True, None

    def _fake_completion(messages, temperature):
        assert messages
        assert temperature == 0.4
        return "raw-response"

    def _fake_formatter(raw_text: str, payload: RequestPayload):
        assert raw_text == "raw-response"
        return "formatted-response"

    monkeypatch.setattr("app.core.orchestration.validate_inputs", _pass_validation)
    monkeypatch.setattr("app.core.orchestration.generate_completion", _fake_completion)
    monkeypatch.setattr("app.core.orchestration.format_response", _fake_formatter)

    payload = RequestPayload(
        job_description="JD",
        cv_text="CV",
        user_prompt="Prompt",
        prompt_variant_id=1,
        temperature=0.4,
    )

    ok, message = generate_questions(payload)

    assert ok is True
    assert message == "formatted-response"
