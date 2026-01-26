"""Shared structured-output schema and prompt guidance."""

from __future__ import annotations

import re

# Schema used by the OpenAI client to enforce structured JSON output.
STRUCTURED_OUTPUT_SCHEMA: dict[str, object] = {
    "name": "interview_practice_response",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "target_role_context": {
                "type": "array",
                "description": "1-3 short bullets summarizing target role expectations.",
                "items": {"type": "string"},
                "minItems": 1,
                "maxItems": 3,
            },
            "cv_note": {
                "type": ["string", "null"],
                "description": "Encouragement to paste CV when missing, otherwise null.",
            },
            "alignments": {
                "type": "array",
                "description": "2-5 bullets showing JD/CV alignment, or empty list if not applicable.",
                "items": {"type": "string"},
            },
            "gaps_or_risk_areas": {
                "type": "array",
                "description": "Bullets highlighting gaps or asking for self-identified gaps.",
                "items": {"type": "string"},
                "minItems": 1,
            },
            "interview_questions": {
                "type": "array",
                "description": "Exactly 5 tagged questions, each starting with a tag like [Technical].",
                "items": {"type": "string"},
                "minItems": 5,
                "maxItems": 5,
            },
            "next_step_suggestions": {
                "type": "array",
                "description": "2-4 follow-up suggestions.",
                "items": {"type": "string"},
                "minItems": 2,
                "maxItems": 4,
            },
        },
        "required": [
            "target_role_context",
            "cv_note",
            "alignments",
            "gaps_or_risk_areas",
            "interview_questions",
            "next_step_suggestions",
        ],
        "additionalProperties": False,
    },
}

# Prompt guidance that mirrors the schema so the model knows the exact structure.
STRUCTURED_OUTPUT_GUIDANCE = (
    "Return JSON only that matches this exact shape:\n"
    "{\n"
    '  "target_role_context": ["..."],\n'
    '  "cv_note": "... or null",\n'
    '  "alignments": ["..."],\n'
    '  "gaps_or_risk_areas": ["..."],\n'
    '  "interview_questions": ["[Technical] ...?", "..."],\n'
    '  "next_step_suggestions": ["...", "..."]\n'
    "}\n"
    "Rules:\n"
    "- target_role_context: 1-3 short bullets. If JD is missing, ask once for the target role.\n"
    "- cv_note: a single sentence only when CV is missing; otherwise null.\n"
    "- alignments: only when JD + CV are provided; otherwise return an empty list.\n"
    "- gaps_or_risk_areas: if CV missing, ask the user to self-identify gaps.\n"
    "- interview_questions: exactly 5 strings, each prefixed with a tag like "
    "[Technical], [Behavioral], [Role-specific], [Screening], [Onsite], [Final], or [General].\n"
    "- next_step_suggestions: 2-4 short follow-up ideas.\n"
    "- Write all strings in English and use Markdown-friendly text inside each string "
    "(e.g., **bold** for emphasis). Do not wrap the JSON in code fences.\n"
    "Do not include markdown, prose outside JSON, or extra keys."
)

_REQUIRED_KEYS = {
    "target_role_context",
    "cv_note",
    "alignments",
    "gaps_or_risk_areas",
    "interview_questions",
    "next_step_suggestions",
}
_TAGGED_QUESTION_PATTERN = re.compile(r"^\[[^\]]+\]\s*\S")


def validate_structured_response(response: dict[str, object]) -> tuple[bool, str | None]:
    """Validate the structured response against the contract expectations."""

    missing = _REQUIRED_KEYS.difference(response.keys())
    if missing:
        return False, "The model response was missing required fields. Please try again."

    extra = set(response.keys()).difference(_REQUIRED_KEYS)
    if extra:
        return False, "The model response included unexpected fields. Please try again."

    def _validate_list(
        name: str,
        value: object,
        min_items: int | None,
        max_items: int | None,
        require_tagged_questions: bool = False,
    ) -> tuple[bool, str | None]:
        if not isinstance(value, list):
            return False, f"The model response field '{name}' must be a list."
        if min_items is not None and len(value) < min_items:
            return False, f"The model response field '{name}' is too short."
        if max_items is not None and len(value) > max_items:
            return False, f"The model response field '{name}' is too long."
        for item in value:
            if not isinstance(item, str) or not item.strip():
                return False, f"The model response field '{name}' must contain strings."
            if require_tagged_questions and not _TAGGED_QUESTION_PATTERN.match(item.strip()):
                return False, "Each interview question must start with a tag like [Technical]."
        return True, None

    ok, message = _validate_list("target_role_context", response.get("target_role_context"), 1, 3)
    if not ok:
        return False, message

    cv_note = response.get("cv_note")
    if cv_note is not None:
        if not isinstance(cv_note, str) or not cv_note.strip():
            return False, "The model response field 'cv_note' must be a string or null."

    ok, message = _validate_list("alignments", response.get("alignments"), 0, 5)
    if not ok:
        return False, message

    ok, message = _validate_list("gaps_or_risk_areas", response.get("gaps_or_risk_areas"), 1, None)
    if not ok:
        return False, message

    ok, message = _validate_list(
        "interview_questions",
        response.get("interview_questions"),
        5,
        5,
        require_tagged_questions=True,
    )
    if not ok:
        return False, message

    ok, message = _validate_list("next_step_suggestions", response.get("next_step_suggestions"), 2, 4)
    if not ok:
        return False, message

    return True, None


def render_markdown_from_response(response: dict[str, object]) -> str:
    """Convert the structured response dict into user-friendly markdown."""

    def _as_list(value: object) -> list[str]:
        if isinstance(value, list):
            return [str(item) for item in value]
        return []

    def _add_section(lines: list[str], title: str, items: list[str], numbered: bool) -> None:
        if not items:
            return
        lines.append(f"## {title}")
        if numbered:
            for index, item in enumerate(items, 1):
                lines.append(f"{index}. {item}")
        else:
            for item in items:
                lines.append(f"- {item}")
        lines.append("")

    sections: list[str] = []

    _add_section(
        sections,
        "Target Role Context",
        _as_list(response.get("target_role_context")),
        numbered=False,
    )

    cv_note = response.get("cv_note")
    if isinstance(cv_note, str) and cv_note.strip():
        sections.append("## CV Note")
        sections.append(cv_note.strip())
        sections.append("")

    _add_section(
        sections,
        "Alignments",
        _as_list(response.get("alignments")),
        numbered=False,
    )

    _add_section(
        sections,
        "Gaps / Risk areas",
        _as_list(response.get("gaps_or_risk_areas")),
        numbered=False,
    )

    _add_section(
        sections,
        "Interview Questions",
        _as_list(response.get("interview_questions")),
        numbered=True,
    )

    _add_section(
        sections,
        "Next-step suggestions",
        _as_list(response.get("next_step_suggestions")),
        numbered=False,
    )

    return "\n".join(sections).strip()
