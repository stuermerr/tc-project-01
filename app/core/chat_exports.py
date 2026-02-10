"""Utilities for exporting assistant responses and chat transcripts as PDFs."""

from __future__ import annotations

import os
import tempfile

from app.core.chat_history import ChatMessage

try:
    from markdown_pdf import MarkdownPdf, Section
except ImportError:  # pragma: no cover - exercised when dependency is missing
    MarkdownPdf = None
    Section = None


def _render_pdf_bytes(title: str, markdown_body: str) -> bytes:
    """Render markdown text into PDF bytes using markdown-pdf."""

    if MarkdownPdf is None or Section is None:
        raise RuntimeError(
            "PDF export dependency missing. Install with `pip install markdown-pdf`."
        )

    body = markdown_body.strip() or "_No content._"
    document_markdown = f"# {title}\n\n{body}\n"

    # Build a single-section document so markdown formatting is preserved.
    pdf = MarkdownPdf(toc_level=0)
    pdf.meta["title"] = title
    pdf.add_section(Section(document_markdown))

    # markdown-pdf writes to file paths; write to a temp file and return bytes for Streamlit.
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
        temp_path = temp_file.name
    try:
        pdf.save(temp_path)
        with open(temp_path, "rb") as handle:
            return handle.read()
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def build_response_pdf_bytes(response_text: str) -> bytes:
    """Build a PDF for a single assistant response."""

    return _render_pdf_bytes("Assistant Response", response_text)


def build_chat_pdf_bytes(messages: list[ChatMessage]) -> bytes:
    """Build a PDF transcript of the full chat history."""

    if not messages:
        return _render_pdf_bytes("Interview Chat Transcript", "_No chat messages yet._")

    sections: list[str] = []
    for message in messages:
        role = "User" if message.role == "user" else "Assistant"
        sections.append(f"## {role}\n\n{message.content.strip()}")
    transcript_markdown = "\n\n---\n\n".join(sections)
    return _render_pdf_bytes("Interview Chat Transcript", transcript_markdown)
