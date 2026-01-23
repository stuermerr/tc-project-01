import re

from app.core.dataclasses import RequestPayload
from app.core.response_formatter import format_response

# Shared tag matcher for counting questions.
_TAG_PATTERN = re.compile(r"\[[^\]]+\]")


def _count_tagged_questions(text: str) -> int:
    # Count lines that include a bracketed tag.
    return sum(1 for line in text.splitlines() if _TAG_PATTERN.search(line))


def test_format_response_includes_required_sections_and_questions():
    # Provide full inputs so alignments and gaps are expected.
    payload = RequestPayload(
        job_description="Looking for a backend engineer with Python API experience.",
        cv_text="Built Python APIs and maintained production services.",
        user_prompt="",
        prompt_variant_id=1,
        temperature=0.2,
    )
    raw_text = "\n".join(
        [
            "[Technical] Question one?",
            "[Behavioral] Question two?",
            "[Role-specific] Question three?",
            "[Screening] Question four?",
            "[Onsite] Question five?",
        ]
    )

    # Format the response and verify the required sections exist.
    result = format_response(raw_text, payload)

    assert "Target Role Context" in result
    assert "Alignments" in result
    assert "Gaps / Risk areas" in result
    assert "Interview Questions" in result
    assert "Next-step suggestions" in result
    assert _count_tagged_questions(result) == 5


def test_format_response_missing_cv_includes_note_and_no_alignments():
    # Omit JD and CV to trigger the missing-data branches.
    payload = RequestPayload(
        job_description="",
        cv_text="",
        user_prompt="",
        prompt_variant_id=1,
        temperature=0.2,
    )
    raw_text = "\n".join(
        [
            "[Technical] Question one?",
            "[Behavioral] Question two?",
            "[Role-specific] Question three?",
            "[Screening] Question four?",
            "[Onsite] Question five?",
        ]
    )

    # Verify that a CV note is added and alignments are omitted.
    result = format_response(raw_text, payload)

    assert "CV Note" in result
    assert "Alignments" not in result
    assert _count_tagged_questions(result) == 5
