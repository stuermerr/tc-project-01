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
