import logging

from app.core.dataclasses import RequestPayload
from app.core.logging_config import setup_logging
from app.core.llm import openai_client
from app.core.orchestration import generate_questions


class _DummyMessage:
    # Minimal message wrapper used by the dummy OpenAI response.
    def __init__(self, content: str) -> None:
        self.content = content


class _DummyChoice:
    # Match the structure returned by the OpenAI client.
    def __init__(self, content: str) -> None:
        self.message = _DummyMessage(content)


class _DummyResponse:
    # Provide a choices list compatible with the wrapper.
    def __init__(self, content: str) -> None:
        self.choices = [_DummyChoice(content)]


class _DummyCompletions:
    # Store kwargs for potential inspection if needed.
    def create(self, **kwargs):
        return _DummyResponse("mocked-response")


class _DummyChat:
    # Expose the completions attribute expected by the wrapper.
    def __init__(self) -> None:
        self.completions = _DummyCompletions()


class _DummyOpenAI:
    # Minimal OpenAI stand-in for logging tests.
    def __init__(self) -> None:
        self.chat = _DummyChat()


def test_orchestration_logs_metadata_without_raw_text(monkeypatch, caplog):
    # Stub dependencies so we only exercise orchestration behavior.
    def _pass_validation(job_description: str, cv_text: str, user_prompt: str):
        return True, None

    def _fake_completion(messages, temperature):
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

    monkeypatch.setattr("app.core.orchestration.validate_inputs", _pass_validation)
    monkeypatch.setattr("app.core.orchestration.generate_completion", _fake_completion)

    payload = RequestPayload(
        job_description="JD secret text",
        cv_text="CV secret text",
        user_prompt="Prompt secret text",
        prompt_variant_id=1,
        temperature=0.3,
    )

    with caplog.at_level(logging.INFO):
        ok, _ = generate_questions(payload)

    assert ok is True
    record = next(r for r in caplog.records if r.message == "request_received")
    assert record.job_description_length == len(payload.job_description)
    assert record.cv_text_length == len(payload.cv_text)
    assert record.user_prompt_length == len(payload.user_prompt)
    record_text = " ".join(
        str(value) for value in record.__dict__.values() if isinstance(value, str)
    )
    assert payload.job_description not in record_text
    assert payload.cv_text not in record_text
    assert payload.user_prompt not in record_text


def test_openai_client_logs_metadata_without_prompt_content(monkeypatch, caplog):
    # Patch the OpenAI client to avoid real API calls.
    monkeypatch.setattr(openai_client, "OpenAI", _DummyOpenAI)

    messages = [
        {"role": "system", "content": "system secret"},
        {"role": "user", "content": "user secret"},
    ]

    with caplog.at_level(logging.INFO):
        ok, result = openai_client.generate_completion(messages, temperature=0.4)

    assert ok is True
    assert result == "mocked-response"
    record = next(r for r in caplog.records if r.message == "openai_request")
    record_text = " ".join(
        str(value) for value in record.__dict__.values() if isinstance(value, str)
    )
    assert "system secret" not in record_text
    assert "user secret" not in record_text


def test_setup_logging_creates_console_handler():
    # Temporarily clear handlers so we can verify setup_logging adds one.
    root_logger = logging.getLogger()
    original_handlers = list(root_logger.handlers)
    original_level = root_logger.level
    try:
        for handler in list(root_logger.handlers):
            root_logger.removeHandler(handler)
        setup_logging("INFO")
        assert root_logger.handlers
        assert root_logger.level == logging.INFO
    finally:
        # Restore original handlers and level to avoid side effects on other tests.
        for handler in list(root_logger.handlers):
            root_logger.removeHandler(handler)
        for handler in original_handlers:
            root_logger.addHandler(handler)
        root_logger.setLevel(original_level)
