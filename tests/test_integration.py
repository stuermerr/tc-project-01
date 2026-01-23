import re

from app.core.dataclasses import RequestPayload
from app.core.llm import openai_client
from app.core.orchestration import generate_questions

# Shared tag matcher for counting questions.
_TAG_PATTERN = re.compile(r"\[[^\]]+\]")


class _DummyMessage:
    # Mirror the response message structure used by the API.
    def __init__(self, content: str) -> None:
        self.content = content


class _DummyChoice:
    # Wrap a single message in the choices format.
    def __init__(self, content: str) -> None:
        self.message = _DummyMessage(content)


class _DummyResponse:
    # Provide the choices list expected by the OpenAI wrapper.
    def __init__(self, content: str) -> None:
        self.choices = [_DummyChoice(content)]


class _DummyCompletions:
    # Return five tagged questions to simulate a compliant model output.
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
    # Provide a completions attribute like the real OpenAI client.
    def __init__(self) -> None:
        self.completions = _DummyCompletions()


class _DummyOpenAI:
    # Minimal client stub used by the orchestration layer.
    def __init__(self) -> None:
        self.chat = _DummyChat()


def _count_tagged_questions(text: str) -> int:
    # Count only lines that include a bracketed tag.
    return sum(1 for line in text.splitlines() if _TAG_PATTERN.search(line))


def test_end_to_end_flow_with_mocked_openai(monkeypatch):
    # Patch the OpenAI client so no network calls are made.
    monkeypatch.setattr(openai_client, "OpenAI", _DummyOpenAI)

    # Build a realistic payload to exercise the formatter path.
    payload = RequestPayload(
        job_description="Backend engineer role focused on Python services.",
        cv_text="Built Python APIs and deployed microservices.",
        user_prompt="Focus on backend systems.",
        prompt_variant_id=1,
        temperature=0.3,
    )

    # Run the controller end-to-end with the mocked LLM.
    ok, response = generate_questions(payload)

    # Validate required sections and question count in the response.
    assert ok is True
    assert "Target Role Context" in response
    assert "Alignments" in response
    assert "Gaps / Risk areas" in response
    assert "Interview Questions" in response
    assert "Next-step suggestions" in response
    assert _count_tagged_questions(response) == 5
