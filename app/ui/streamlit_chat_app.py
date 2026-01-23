"""Chat-style Streamlit UI for the interview practice app."""

from __future__ import annotations

import logging
import uuid

import streamlit as st

from app.core.chat_history import (
    ChatMessage,
    append_chat_message,
    init_chat_history,
    trim_chat_history,
)
from app.core.dataclasses import RequestPayload
from app.core.logging_config import setup_logging
from app.core.model_catalog import DEFAULT_MODEL, get_allowed_models
from app.core.orchestration import generate_questions
from app.core.prompts import get_prompt_variants
from app.core.safety import check_rate_limit
from app.core.structured_output import render_markdown_from_response

_LOGGER = logging.getLogger(__name__)

# Keep a conservative character limit so chat history stays manageable.
_MAX_HISTORY_CHARS = 4000


def _build_payload(
    job_description: str,
    cv_text: str,
    user_prompt: str,
    prompt_variant_id: int,
    temperature: float,
    model_name: str,
) -> RequestPayload:
    # Bundle raw UI inputs into a typed payload for the controller.
    return RequestPayload(
        job_description=job_description,
        cv_text=cv_text,
        user_prompt=user_prompt,
        prompt_variant_id=prompt_variant_id,
        temperature=temperature,
        model_name=model_name,
    )


def _history_to_prompt(messages: list[ChatMessage]) -> str:
    """Serialize chat history into a single prompt string."""

    # Convert chat turns into a simple transcript format.
    lines: list[str] = []
    for message in messages:
        role = "User" if message.role == "user" else "Assistant"
        lines.append(f"{role}: {message.content}")
    return "\n".join(lines).strip()


def render_chat_ui() -> None:
    """Render the chat experience without setting page config."""

    st.title("Interview Practice Chat")
    st.caption("Chat with the app to generate structured interview questions.")

    # Load prompt variants to populate the dropdown.
    variants = get_prompt_variants()
    # Map labels to ids so the UI stays readable while the payload stays numeric.
    variant_labels = {variant.name: variant.id for variant in variants}
    # Load the supported model list so the UI stays in sync with the backend.
    allowed_models = get_allowed_models()

    # Keep JD/CV and settings in the sidebar so the chat stays front and center.
    with st.sidebar:
        st.header("Job context")
        job_description = st.text_area(
            "Job Description (optional)",
            height=180,
            placeholder="Paste the target role description here.",
        )
        cv_text = st.text_area(
            "CV / Resume (optional)",
            height=180,
            placeholder="Paste your CV or resume here.",
        )
        st.divider()
        model_name = st.selectbox(
            "Model",
            options=allowed_models,
            index=allowed_models.index(DEFAULT_MODEL)
            if DEFAULT_MODEL in allowed_models
            else 0,
        )
        selected_label = st.selectbox(
            "Prompt variant",
            options=list(variant_labels.keys()),
        )
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.2,
            step=0.05,
        )

    # Initialize or retrieve chat history from session state.
    messages = init_chat_history(st.session_state)

    # Render existing conversation turns in order.
    for message in messages:
        with st.chat_message(message.role):
            st.markdown(message.content)

    # Use the chat input so Enter sends the next message.
    user_input = st.chat_input("Ask for interview questions or focus areas")

    if not user_input:
        return

    # Record a request-level log entry without exposing user content.
    _LOGGER.info(
        "chat_message_received",
        extra={
            "job_description_length": len(job_description),
            "cv_text_length": len(cv_text),
            "user_prompt_length": len(user_input),
            "selected_variant": selected_label,
            "temperature": temperature,
            "model_name": model_name,
        },
    )

    # Rate limit per session to prevent accidental rapid-fire requests.
    if "rate_limit_key" not in st.session_state:
        st.session_state["rate_limit_key"] = str(uuid.uuid4())
    ok, refusal = check_rate_limit(st.session_state["rate_limit_key"])
    if not ok:
        _LOGGER.info("chat_rate_limited")
        st.error(refusal or "Too many requests. Please try again.")
        return

    # Append the user message and trim history before building the prompt.
    append_chat_message(messages, role="user", content=user_input)
    trim_chat_history(messages, max_chars=_MAX_HISTORY_CHARS)
    history_prompt = _history_to_prompt(messages)

    # Show the user message in the chat UI.
    with st.chat_message("user"):
        st.markdown(user_input)

    payload = _build_payload(
        job_description=job_description,
        cv_text=cv_text,
        user_prompt=history_prompt,
        prompt_variant_id=variant_labels[selected_label],
        temperature=temperature,
        model_name=model_name,
    )

    # Generate the assistant response and render it in the chat.
    with st.chat_message("assistant"):
        with st.spinner("Generating questions..."):
            ok, response = generate_questions(payload)

        if not ok:
            _LOGGER.info("chat_request_blocked")
            st.error(response)
            append_chat_message(messages, role="assistant", content=str(response))
            return

        if isinstance(response, dict):
            content = render_markdown_from_response(response)
        else:
            content = str(response)

        st.markdown(content)
        append_chat_message(messages, role="assistant", content=content)
        _LOGGER.info("chat_request_success")


if __name__ == "__main__":
    # Ensure standard console logging is active before any log calls.
    setup_logging()
    # Configure the page once at startup to control layout and branding.
    st.set_page_config(page_title="Interview Practice Chat", page_icon="🧩", layout="wide")
    render_chat_ui()


def main() -> None:
    """Entry point for Streamlit to render the chat UI standalone."""

    # Ensure standard console logging is active before any log calls.
    setup_logging()
    # Configure the page once at startup to control layout and branding.
    st.set_page_config(page_title="Interview Practice Chat", page_icon="🧩", layout="wide")
    render_chat_ui()
    # Allow `python streamlit_chat_app.py` for local debugging.
    main()
