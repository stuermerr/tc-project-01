from app.core.llm import openai_client
from app.core.structured_output import STRUCTURED_OUTPUT_SCHEMA


class _DummyMessage:
    # Simple container that mimics the OpenAI message shape.
    def __init__(self, content: str) -> None:
        self.content = content


class _DummyChoice:
    # Wrap the message in the structure returned by the API.
    def __init__(self, content: str) -> None:
        self.message = _DummyMessage(content)


class _DummyResponse:
    # Provide a choices list to match the OpenAI response contract.
    def __init__(self, content: str) -> None:
        self.choices = [_DummyChoice(content)]


class _DummyCompletions:
    # Record the last payload so the test can assert it.
    def __init__(self) -> None:
        self.last_kwargs: dict[str, object] | None = None

    # Return a deterministic response for testing.
    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return _DummyResponse("mocked-response")


class _DummyChat:
    # Provide a completions attribute like the OpenAI client.
    def __init__(self) -> None:
        self.completions = _DummyCompletions()


class _DummyOpenAI:
    # Capture created clients so we can inspect the payload used.
    def __init__(self, created_clients: list["_DummyOpenAI"]) -> None:
        self.chat = _DummyChat()
        created_clients.append(self)


def test_generate_completion_builds_payload(monkeypatch):
    # Track client creation to inspect the request parameters.
    created_clients: list[_DummyOpenAI] = []

    # Provide a factory so the wrapper uses our dummy client.
    def _factory():
        return _DummyOpenAI(created_clients)

    # Patch the OpenAI client constructor to avoid real API calls.
    monkeypatch.setattr(openai_client, "OpenAI", _factory)
    # Build a minimal message set to send to the wrapper.
    messages = [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "user"},
    ]

    # Call the wrapper and capture the result.
    ok, result = openai_client.generate_completion(messages, temperature=0.4)

    # Assert both return value and payload fields.
    assert ok is True
    assert result == "mocked-response"
    assert len(created_clients) == 1
    last_kwargs = created_clients[0].chat.completions.last_kwargs
    assert last_kwargs["model"] == openai_client.DEFAULT_MODEL
    assert last_kwargs["messages"] == messages
    assert last_kwargs["temperature"] == 0.4
    assert last_kwargs["response_format"]["type"] == "json_schema"
    assert last_kwargs["response_format"]["json_schema"] == STRUCTURED_OUTPUT_SCHEMA
