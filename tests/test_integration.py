import re

from app.core.dataclasses import RequestPayload
from app.core.llm import openai_client
from app.core.orchestration import generate_questions

_TAG_PATTERN = re.compile(r"\[[^\]]+\]")


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
    def create(self, **kwargs):
        return _DummyResponse(
            "\n".join(
                [
                    "[Technical] Question one?",
                    "[Behavioral] Question two?",
                    "[Role-specific] Question three?",
                    "[Screening] Question four?",
                    "[Onsite] Question five?",
                ]
            )
        )


class _DummyChat:
    def __init__(self) -> None:
        self.completions = _DummyCompletions()


class _DummyOpenAI:
    def __init__(self) -> None:
        self.chat = _DummyChat()


def _count_tagged_questions(text: str) -> int:
    return sum(1 for line in text.splitlines() if _TAG_PATTERN.search(line))


def test_end_to_end_flow_with_mocked_openai(monkeypatch):
    monkeypatch.setattr(openai_client, "OpenAI", _DummyOpenAI)

    payload = RequestPayload(
        job_description="Backend engineer role focused on Python services.",
        cv_text="Built Python APIs and deployed microservices.",
        user_prompt="Focus on backend systems.",
        prompt_variant_id=1,
        temperature=0.3,
    )

    ok, response = generate_questions(payload)

    assert ok is True
    assert "Target Role Context" in response
    assert "Alignments" in response
    assert "Gaps / Risk areas" in response
    assert "Interview Questions" in response
    assert "Next-step suggestions" in response
    assert _count_tagged_questions(response) == 5
