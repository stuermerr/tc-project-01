"""Shared structured-output schema and prompt guidance."""

from __future__ import annotations

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
    "- Write all strings in English.\n"
    "Do not include markdown, prose outside JSON, or extra keys."
)
