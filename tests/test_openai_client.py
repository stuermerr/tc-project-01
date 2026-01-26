from app.core.llm import openai_client
from app.core.model_catalog import get_allowed_models, get_reasoning_effort_options
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


class _DummyResponsesResult:
    # Provide output_text for Responses API calls.
    def __init__(self, content: str) -> None:
        self.output_text = content


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


class _DummyResponses:
    # Record the last payload so the test can assert it.
    def __init__(self) -> None:
        self.last_kwargs: dict[str, object] | None = None

    # Return a deterministic response for testing.
    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return _DummyResponsesResult("mocked-response")


class _DummyOpenAI:
    # Capture created clients so we can inspect the payload used.
    def __init__(self, created_clients: list["_DummyOpenAI"]) -> None:
        self.chat = _DummyChat()
        self.responses = _DummyResponses()
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


def test_generate_completion_uses_model_override(monkeypatch):
    # Track client creation to inspect the request parameters.
    created_clients: list[_DummyOpenAI] = []

    # Provide a factory so the wrapper uses our dummy client.
    def _factory():
        return _DummyOpenAI(created_clients)

    monkeypatch.setattr(openai_client, "OpenAI", _factory)
    messages = [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "user"},
    ]
    override_model = get_allowed_models()[1]

    # Call the wrapper with an explicit model override.
    ok, result = openai_client.generate_completion(
        messages, temperature=0.2, model_name=override_model
    )

    assert ok is True
    assert result == "mocked-response"
    last_kwargs = created_clients[0].chat.completions.last_kwargs
    assert last_kwargs["model"] == override_model


def test_generate_completion_gpt5_uses_reasoning_effort(monkeypatch):
    # Track client creation to inspect the request parameters.
    created_clients: list[_DummyOpenAI] = []

    # Provide a factory so the wrapper uses our dummy client.
    def _factory():
        return _DummyOpenAI(created_clients)

    monkeypatch.setattr(openai_client, "OpenAI", _factory)
    messages = [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "user"},
    ]

    ok, result = openai_client.generate_completion(
        messages,
        temperature=None,
        model_name="gpt-5-nano",
        reasoning_effort="medium",
    )

    assert ok is True
    assert result == "mocked-response"
    last_kwargs = created_clients[0].chat.completions.last_kwargs
    assert last_kwargs["model"] == "gpt-5-nano"
    assert "temperature" not in last_kwargs
    assert last_kwargs["reasoning_effort"] == "medium"
    assert last_kwargs["response_format"]["type"] == "json_schema"


def test_generate_chat_completion_omits_response_format(monkeypatch):
    # Track client creation to inspect the request parameters.
    created_clients: list[_DummyOpenAI] = []

    # Provide a factory so the wrapper uses our dummy client.
    def _factory():
        return _DummyOpenAI(created_clients)

    monkeypatch.setattr(openai_client, "OpenAI", _factory)
    messages = [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "user"},
    ]

    # Call the chat wrapper and capture the result.
    ok, result = openai_client.generate_chat_completion(
        messages, temperature=0.1, model_name=get_allowed_models()[0]
    )

    assert ok is True
    assert result == "mocked-response"
    last_kwargs = created_clients[0].chat.completions.last_kwargs
    assert "response_format" not in last_kwargs
    assert last_kwargs["temperature"] == 0.1


def test_gpt5_models_accept_reasoning_effort_options(monkeypatch):
    # Track client creation so we can inspect each request payload.
    created_clients: list[_DummyOpenAI] = []

    def _factory():
        return _DummyOpenAI(created_clients)

    monkeypatch.setattr(openai_client, "OpenAI", _factory)
    messages = [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "user"},
    ]

    for model_name in ["gpt-5-nano", "gpt-5.2-chat-latest"]:
        for effort in get_reasoning_effort_options(model_name):
            ok, result = openai_client.generate_chat_completion(
                messages,
                temperature=None,
                model_name=model_name,
                reasoning_effort=effort,
            )

            assert ok is True
            assert result == "mocked-response"
            client = created_clients[-1]
            if model_name == "gpt-5.2-chat-latest":
                last_kwargs = client.responses.last_kwargs
                assert last_kwargs["model"] == model_name
                assert last_kwargs["reasoning"] == {"effort": effort}
                assert "temperature" not in last_kwargs
            else:
                last_kwargs = client.chat.completions.last_kwargs
                assert last_kwargs["model"] == model_name
                assert "temperature" not in last_kwargs
                assert last_kwargs["reasoning_effort"] == effort
