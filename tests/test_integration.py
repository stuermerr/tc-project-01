from app.core.dataclasses import RequestPayload
from app.core.llm import openai_client
from app.core.orchestration import generate_questions


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
            (
                '{"target_role_context":["Backend role summary"],'
                '"cv_note":null,'
                '"alignments":["Python APIs align with JD"],'
                '"gaps_or_risk_areas":["Deepen distributed systems"],'
                '"interview_questions":['
                '"[Technical] Question one?",'
                '"[Behavioral] Question two?",'
                '"[Role-specific] Question three?",'
                '"[Screening] Question four?",'
                '"[Onsite] Question five?"'
                '],'
                '"next_step_suggestions":["Paste your CV","Ask for another set"]}'
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


def test_end_to_end_flow_with_mocked_openai(monkeypatch):
    # Patch the OpenAI client so no network calls are made.
    monkeypatch.setattr(openai_client, "OpenAI", _DummyOpenAI)

    # Build a realistic payload to exercise the structured-output path.
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
    assert isinstance(response, dict)
    assert "target_role_context" in response
    assert "alignments" in response
    assert "gaps_or_risk_areas" in response
    assert "interview_questions" in response
    assert "next_step_suggestions" in response
    assert len(response["interview_questions"]) == 5
