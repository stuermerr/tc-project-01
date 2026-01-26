"""Tests for structured output markdown rendering and validation."""

from app.core.structured_output import render_markdown_from_response, validate_structured_response


def test_render_markdown_from_response_builds_sections():
    """Verify render markdown from response builds sections."""
    response = {
        "target_role_context": ["Role summary"],
        "cv_note": "Paste your CV for better alignment.",
        "alignments": ["Alignment point"],
        "gaps_or_risk_areas": ["Gap point"],
        "interview_questions": [
            "[Technical] Question one?",
            "[Behavioral] Question two?",
            "[Role-specific] Question three?",
            "[Screening] Question four?",
            "[Onsite] Question five?",
        ],
        "next_step_suggestions": ["Next step", "Another step"],
    }

    markdown = render_markdown_from_response(response)

    assert "## Target Role Context" in markdown
    assert "## CV Note" in markdown
    assert "## Alignments" in markdown
    assert "## Gaps / Risk areas" in markdown
    assert "## Interview Questions" in markdown
    assert "## Next-step suggestions" in markdown
    assert "1. [Technical] Question one?" in markdown
    assert "5. [Onsite] Question five?" in markdown


def test_render_markdown_from_response_skips_empty_sections():
    """Verify render markdown from response skips empty sections."""
    response = {
        "target_role_context": ["Role summary"],
        "cv_note": None,
        "alignments": [],
        "gaps_or_risk_areas": ["Gap point"],
        "interview_questions": [
            "[Technical] Question one?",
            "[Behavioral] Question two?",
            "[Role-specific] Question three?",
            "[Screening] Question four?",
            "[Onsite] Question five?",
        ],
        "next_step_suggestions": ["Next step", "Another step"],
    }

    markdown = render_markdown_from_response(response)

    assert "## CV Note" not in markdown
    assert "## Alignments" not in markdown


def test_validate_structured_response_rejects_non_list_field():
    """Verify validate structured response rejects non-list field."""
    response = {
        "target_role_context": ["Role summary"],
        "cv_note": "Paste your CV for better alignment.",
        "alignments": "not-a-list",
        "gaps_or_risk_areas": ["Gap point"],
        "interview_questions": [
            "[Technical] Question one?",
            "[Behavioral] Question two?",
            "[Role-specific] Question three?",
            "[Screening] Question four?",
            "[Onsite] Question five?",
        ],
        "next_step_suggestions": ["Next step", "Another step"],
    }

    ok, message = validate_structured_response(response)

    assert ok is False
    assert message


def test_validate_structured_response_rejects_invalid_cv_note_type():
    """Verify validate structured response rejects invalid cv_note type."""
    response = {
        "target_role_context": ["Role summary"],
        "cv_note": 123,
        "alignments": ["Alignment point"],
        "gaps_or_risk_areas": ["Gap point"],
        "interview_questions": [
            "[Technical] Question one?",
            "[Behavioral] Question two?",
            "[Role-specific] Question three?",
            "[Screening] Question four?",
            "[Onsite] Question five?",
        ],
        "next_step_suggestions": ["Next step", "Another step"],
    }

    ok, message = validate_structured_response(response)

    assert ok is False
    assert message
