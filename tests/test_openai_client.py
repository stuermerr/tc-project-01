from app.core.llm import openai_client


class _DummyMessage:
    def __init__(self, content: str) -> None:
        self.content = content


class _DummyChoice:
    def __init__(self, content: str) -> None:
        self.message = _DummyMessage(content)


class _DummyResponse:
    def __init__(self, content: str) -> None:
        self.choices = [_DummyChoice(content)]


class _DummyCompletions:
    def __init__(self) -> None:
        self.last_kwargs: dict[str, object] | None = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return _DummyResponse("mocked-response")


class _DummyChat:
    def __init__(self) -> None:
        self.completions = _DummyCompletions()


class _DummyOpenAI:
    def __init__(self, created_clients: list["_DummyOpenAI"]) -> None:
        self.chat = _DummyChat()
        created_clients.append(self)


def test_generate_completion_builds_payload(monkeypatch):
    created_clients: list[_DummyOpenAI] = []

    def _factory():
        return _DummyOpenAI(created_clients)

    monkeypatch.setattr(openai_client, "OpenAI", _factory)
    messages = [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "user"},
    ]

    result = openai_client.generate_completion(messages, temperature=0.4)

    assert result == "mocked-response"
    assert len(created_clients) == 1
    last_kwargs = created_clients[0].chat.completions.last_kwargs
    assert last_kwargs["model"] == openai_client.DEFAULT_MODEL
    assert last_kwargs["messages"] == messages
    assert last_kwargs["temperature"] == 0.4
