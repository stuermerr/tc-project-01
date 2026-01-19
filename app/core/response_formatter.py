"""Format raw model output into the required response contract."""

from __future__ import annotations

import re
from collections import Counter

from app.core.dataclasses import RequestPayload

_TAG_PATTERN = re.compile(r"\[[^\]]+\]")
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
_TOKEN_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9+#-]{2,}")

_STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "your",
    "you",
    "our",
    "are",
    "was",
    "were",
    "have",
    "has",
    "had",
    "will",
    "shall",
    "should",
    "would",
    "could",
    "from",
    "into",
    "about",
    "their",
    "they",
    "them",
    "these",
    "those",
    "role",
    "roles",
    "job",
    "position",
    "candidate",
}

_DEFAULT_QUESTIONS = [
    "[Technical] Walk through a recent system you built and the trade-offs you made.",
    "[Behavioral] Tell me about a time you resolved a high-pressure incident.",
    "[Role-specific] Which core requirement are you least confident in, and why?",
    "[Screening] What motivated you to pursue this role?",
    "[Onsite] How would you prioritize improvements in your first 90 days?",
]


def _strip_list_prefix(line: str) -> str:
    return re.sub(r"^\s*(?:[-*]|\d+[.)])\s*", "", line).strip()


def _extract_tagged_questions(raw_text: str) -> list[str]:
    questions: list[str] = []
    for line in raw_text.splitlines():
        candidate = _strip_list_prefix(line)
        if not candidate:
            continue
        if _TAG_PATTERN.search(candidate):
            questions.append(candidate)
    return questions


def _ensure_tagged(question: str) -> str:
    if _TAG_PATTERN.search(question):
        return question
    return f"[General] {question}"


def _fallback_questions_from_text(raw_text: str) -> list[str]:
    questions: list[str] = []
    for segment in raw_text.split("?"):
        cleaned = segment.strip()
        if not cleaned:
            continue
        question = cleaned if cleaned.endswith("?") else f"{cleaned}?"
        questions.append(_ensure_tagged(question))
    return questions


def _ensure_five_questions(raw_text: str) -> list[str]:
    questions = _extract_tagged_questions(raw_text)
    if len(questions) < 5:
        for candidate in _fallback_questions_from_text(raw_text):
            if len(questions) >= 5:
                break
            if candidate not in questions:
                questions.append(candidate)
    if len(questions) < 5:
        for candidate in _DEFAULT_QUESTIONS:
            if len(questions) >= 5:
                break
            if candidate not in questions:
                questions.append(candidate)
    return questions[:5]


def _summarize_job_description(job_description: str) -> list[str]:
    sentences: list[str] = []
    for line in job_description.splitlines():
        line = line.strip()
        if not line:
            continue
        sentences.extend(_SENTENCE_SPLIT.split(line))
        if len(sentences) >= 3:
            break
    bullets = []
    for sentence in sentences[:3]:
        trimmed = sentence.strip()
        if not trimmed:
            continue
        if len(trimmed) > 160:
            trimmed = f"{trimmed[:157]}..."
        bullets.append(f"- {trimmed}")
    if not bullets:
        bullets.append("- Role expectations are based on the provided job description.")
    return bullets


def _top_keywords(text: str, limit: int = 8) -> list[str]:
    tokens = [
        token
        for token in _TOKEN_PATTERN.findall(text.lower())
        if token not in _STOPWORDS
    ]
    if not tokens:
        return []
    counts = Counter(tokens)
    return [word for word, _ in counts.most_common(limit)]


def _format_section(title: str, lines: list[str]) -> str:
    if not lines:
        return ""
    return "\n".join([title, *lines])


def _has_required_headings(raw_text: str, payload: RequestPayload) -> bool:
    lowered = raw_text.lower()
    required = {
        "target role context",
        "gaps / risk areas",
        "interview questions",
        "next-step suggestions",
    }
    if not payload.cv_text.strip():
        required.add("cv note")
    if payload.cv_text.strip() and payload.job_description.strip():
        required.add("alignments")
    return all(heading in lowered for heading in required)


def format_response(raw_text: str, payload: RequestPayload) -> str:
    """Ensure the response contains required sections and exactly 5 questions."""

    questions = _ensure_five_questions(raw_text)
    if _has_required_headings(raw_text, payload) and len(questions) == 5:
        return raw_text.strip()

    sections: list[str] = []

    if payload.job_description.strip():
        target_role_lines = _summarize_job_description(payload.job_description)
    else:
        target_role_lines = ["- What is the target role you want to practice for?"]
    sections.append(_format_section("Target Role Context", target_role_lines))

    if not payload.cv_text.strip():
        sections.append(
            _format_section(
                "CV Note",
                ["If you paste your CV, I can tailor the questions more precisely."],
            )
        )

    if payload.cv_text.strip() and payload.job_description.strip():
        jd_keywords = _top_keywords(payload.job_description)
        cv_keywords = _top_keywords(payload.cv_text)
        shared = [word for word in jd_keywords if word in cv_keywords]
        if shared:
            alignments = [f"- Shared focus areas: {', '.join(shared[:5])}."]
        else:
            alignments = ["- No obvious keyword overlaps detected; review JD and CV for fit."]
        sections.append(_format_section("Alignments", alignments))

    if payload.cv_text.strip() and payload.job_description.strip():
        jd_keywords = _top_keywords(payload.job_description)
        cv_keywords = _top_keywords(payload.cv_text)
        gaps = [word for word in jd_keywords if word not in cv_keywords]
        if gaps:
            gap_lines = [f"- Potential gaps to review: {', '.join(gaps[:5])}."]
        else:
            gap_lines = ["- No obvious keyword gaps detected; validate depth in key areas."]
    else:
        gap_lines = [
            "- What should we focus on?",
            "- Which requirements from the job description do you not satisfy?",
            "- Rate key requirements from 0 (none) to 5 (expert).",
        ]
    sections.append(_format_section("Gaps / Risk areas", gap_lines))

    question_lines = [
        f"{index}. {_ensure_tagged(question)}" for index, question in enumerate(questions, 1)
    ]
    sections.append(_format_section("Interview Questions", question_lines))

    suggestions = [
        "Paste your CV for better alignment-based questions.",
        "Tell me which requirements you rate lowest (0–5).",
        "Ask for another set of 5 questions.",
        "What further questions do you want to focus on—technical, role-specific, or something else?",
    ]
    if payload.cv_text.strip():
        suggestions = suggestions[1:]
    sections.append(
        _format_section("Next-step suggestions", [f"- {item}" for item in suggestions[:4]])
    )

    return "\n\n".join(section for section in sections if section)
