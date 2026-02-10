"""Tests for the LangChain client wrapper."""

from app.core import langchain_client
from app.core.dataclasses import RequestPayload


class _DummyLangchainResponse:
    # Simple response container that mimics LangChain message content.
    def __init__(self, content: str) -> None:
        self.content = content


class _DummyChatOpenAI:
    # Stand-in ChatOpenAI client that records inputs.
    next_response = "langchain-response"

    def __init__(self, created_clients: list["_DummyChatOpenAI"], **kwargs) -> None:
        self.kwargs = kwargs
        self.messages: list[object] | None = None
        created_clients.append(self)

    # Return a deterministic response to keep the test stable.
    def invoke(self, messages: list[object]):
        self.messages = messages
        return _DummyLangchainResponse(self.next_response)


def test_generate_langchain_completion_returns_text(monkeypatch):
    """Verify LangChain wrapper returns raw text."""
    # Capture client construction for later assertions.
    created_clients: list[_DummyChatOpenAI] = []
    _DummyChatOpenAI.next_response = "langchain-response"

    # Provide a factory so the wrapper uses the dummy client.
    def _factory(**kwargs):
        return _DummyChatOpenAI(created_clients, **kwargs)

    monkeypatch.setattr(langchain_client, "ChatOpenAI", _factory)

    # Build a minimal payload that should pass validation.
    payload = RequestPayload(
        job_description="Backend engineer role.",
        cv_text="Experience with Python.",
        user_prompt="Focus on APIs.",
        prompt_variant_id=1,
        temperature=0.3,
    )

    # Execute the wrapper and verify the raw response.
    ok, result = langchain_client.generate_langchain_completion(payload)

    assert ok is True
    assert result == "langchain-response"
    assert created_clients


def test_generate_langchain_questions_parses_structured_json(monkeypatch):
    """Verify LangChain wrapper parses structured JSON."""
    # Capture client construction for later assertions.
    created_clients: list[_DummyChatOpenAI] = []
    _DummyChatOpenAI.next_response = (
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

    def _factory(**kwargs):
        return _DummyChatOpenAI(created_clients, **kwargs)

    monkeypatch.setattr(langchain_client, "ChatOpenAI", _factory)

    payload = RequestPayload(
        job_description="JD",
        cv_text="CV",
        user_prompt="Prompt",
        prompt_variant_id=1,
        temperature=0.2,
    )

    ok, result = langchain_client.generate_langchain_questions(payload)

    assert ok is True
    assert isinstance(result, dict)
    assert len(result["interview_questions"]) == 5
    assert created_clients
    response_format = created_clients[0].kwargs.get("model_kwargs", {}).get("response_format")
    assert isinstance(response_format, dict)
    assert response_format.get("type") == "json_schema"


def test_generate_langchain_chat_response_returns_text(monkeypatch):
    """Verify LangChain chat wrapper returns plain text."""
    created_clients: list[_DummyChatOpenAI] = []
    _DummyChatOpenAI.next_response = "chat reply"

    def _factory(**kwargs):
        return _DummyChatOpenAI(created_clients, **kwargs)

    monkeypatch.setattr(langchain_client, "ChatOpenAI", _factory)

    payload = RequestPayload(
        job_description="JD",
        cv_text="CV",
        user_prompt="User prompt",
        prompt_variant_id=101,
        temperature=0.2,
    )

    ok, result = langchain_client.generate_langchain_chat_response(payload)

    assert ok is True
    assert result == "chat reply"


def test_generate_langchain_chat_response_does_not_parse_json(monkeypatch):
    """Verify LangChain chat wrapper does not parse JSON."""
    created_clients: list[_DummyChatOpenAI] = []
    _DummyChatOpenAI.next_response = "plain chat response"

    def _factory(**kwargs):
        return _DummyChatOpenAI(created_clients, **kwargs)

    monkeypatch.setattr(langchain_client, "ChatOpenAI", _factory)
    monkeypatch.setattr(
        langchain_client,
        "parse_structured_output",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("Structured parsing should not run for chat")
        ),
    )

    payload = RequestPayload(
        job_description="JD",
        cv_text="CV",
        user_prompt="User prompt",
        prompt_variant_id=101,
        temperature=0.2,
    )

    ok, result = langchain_client.generate_langchain_chat_response(payload)

    assert ok is True
    assert result == "plain chat response"


def test_generate_langchain_chat_response_handles_refusal(monkeypatch):
    """Verify LangChain chat wrapper surfaces refusals."""
    created_clients: list[object] = []

    class _RefusalChatOpenAI:
        # Minimal stand-in that returns a refusal response.
        def __init__(self, **kwargs) -> None:
            created_clients.append(kwargs)

        def invoke(self, messages: list[object]):
            class _RefusalResponse:
                def __init__(self) -> None:
                    self.refusal = "Blocked"
                    self.content = ""

            return _RefusalResponse()

    monkeypatch.setattr(langchain_client, "ChatOpenAI", _RefusalChatOpenAI)

    payload = RequestPayload(
        job_description="JD",
        cv_text="CV",
        user_prompt="User prompt",
        prompt_variant_id=101,
        temperature=0.2,
    )

    ok, result = langchain_client.generate_langchain_chat_response(payload)

    assert ok is False
    assert result == "Blocked"


def test_generate_langchain_chat_response_uses_selected_variant(monkeypatch):
    """Verify LangChain chat wrapper uses the requested prompt variant id."""
    created_clients: list[_DummyChatOpenAI] = []
    _DummyChatOpenAI.next_response = "chat reply"
    captured_variant_ids: list[int] = []

    def _factory(**kwargs):
        return _DummyChatOpenAI(created_clients, **kwargs)

    def _build_messages(payload, variant):
        captured_variant_ids.append(variant.id)
        return [
            {"role": "system", "content": "system"},
            {"role": "user", "content": payload.user_prompt},
        ]

    monkeypatch.setattr(langchain_client, "ChatOpenAI", _factory)
    monkeypatch.setattr(langchain_client, "build_messages", _build_messages)

    payload = RequestPayload(
        job_description="JD",
        cv_text="CV",
        user_prompt="User prompt",
        prompt_variant_id=102,
        temperature=0.2,
    )

    ok, result = langchain_client.generate_langchain_chat_response(payload)

    assert ok is True
    assert result == "chat reply"
    assert captured_variant_ids == [102]


def test_generate_langchain_chat_response_uses_selected_model_settings(monkeypatch):
    """Verify LangChain chat wrapper applies per-request model settings."""
    created_clients: list[_DummyChatOpenAI] = []
    _DummyChatOpenAI.next_response = "chat reply"

    def _factory(**kwargs):
        return _DummyChatOpenAI(created_clients, **kwargs)

    monkeypatch.setattr(langchain_client, "ChatOpenAI", _factory)

    payload = RequestPayload(
        job_description="JD",
        cv_text="CV",
        user_prompt="User prompt",
        prompt_variant_id=101,
        temperature=None,
        model_name="gpt-5-nano",
        reasoning_effort="high",
    )

    ok, result = langchain_client.generate_langchain_chat_response(payload)

    assert ok is True
    assert result == "chat reply"
    assert created_clients
    client_kwargs = created_clients[0].kwargs
    assert client_kwargs["model"] == "gpt-5-nano"
    assert client_kwargs.get("model_kwargs", {}).get("reasoning_effort") == "high"


def test_generate_langchain_chat_summary_returns_text(monkeypatch):
    """Verify LangChain chat summary wrapper returns plain text."""
    created_clients: list[_DummyChatOpenAI] = []
    _DummyChatOpenAI.next_response = "summary reply"

    def _factory(**kwargs):
        return _DummyChatOpenAI(created_clients, **kwargs)

    monkeypatch.setattr(langchain_client, "ChatOpenAI", _factory)

    payload = RequestPayload(
        job_description="JD",
        cv_text="CV",
        user_prompt="User: hello\nAssistant: hi",
        prompt_variant_id=101,
        temperature=0.2,
    )

    ok, result = langchain_client.generate_langchain_chat_summary(payload)

    assert ok is True
    assert result == "summary reply"


def test_generate_langchain_cover_letter_requires_jd_cv(monkeypatch):
    """Verify LangChain cover letter generation requires JD and CV."""
    # Guard against accidental LLM calls in the refusal path.
    def _unexpected_call(*args, **kwargs):  # pragma: no cover - should not be called
        raise AssertionError("LLM should not be called when JD/CV are missing")

    monkeypatch.setattr(langchain_client, "ChatOpenAI", _unexpected_call)

    payload = RequestPayload(
        job_description="JD",
        cv_text="",
        user_prompt="History",
        prompt_variant_id=101,
        temperature=0.2,
    )

    ok, message = langchain_client.generate_langchain_cover_letter_response(payload)

    assert ok is False
    assert "job description" in message
