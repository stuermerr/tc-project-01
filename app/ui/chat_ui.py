"""Chat UI rendering helpers for the multipage Streamlit app."""

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
from app.core.model_catalog import (
    DEFAULT_MODEL,
    DEFAULT_REASONING_EFFORT,
    DEFAULT_VERBOSITY,
    get_allowed_models,
    get_reasoning_effort_options,
    get_verbosity_options,
    is_gpt5_model,
)
from app.core.orchestration import generate_chat_response
from app.core.prompts import get_chat_prompt_variants
from app.core.safety import check_rate_limit

_LOGGER = logging.getLogger(__name__)

# Keep a conservative character limit so chat history stays manageable.
_MAX_HISTORY_CHARS = 4000


def _build_payload(
    job_description: str,
    cv_text: str,
    user_prompt: str,
    prompt_variant_id: int,
    temperature: float | None,
    model_name: str,
    reasoning_effort: str | None,
    verbosity: str | None,
) -> RequestPayload:
    # Bundle raw UI inputs into a typed payload for the controller.
    return RequestPayload(
        job_description=job_description,
        cv_text=cv_text,
        user_prompt=user_prompt,
        prompt_variant_id=prompt_variant_id,
        temperature=temperature,
        model_name=model_name,
        reasoning_effort=reasoning_effort,
        verbosity=verbosity,
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

    st.title("Interview Preparation Chat")
    st.caption("Chat with the app for coaching, feedback, and practice questions.")

    # Load prompt variants to populate the dropdown.
    variants = get_chat_prompt_variants()
    # Map labels to ids so the UI stays readable while the payload stays numeric.
    variant_labels = {variant.name: variant.id for variant in variants}
    # Load the supported model list so the UI stays in sync with the backend.
    allowed_models = get_allowed_models()

    # Place JD and CV side-by-side at the top to match the classic layout.
    col_left, col_right = st.columns(2)
    with col_left:
        job_description = st.text_area(
            "Job Description (optional)",
            height=220,
            placeholder="Paste the target role description here.",
        )
    with col_right:
        cv_text = st.text_area(
            "CV / Resume (optional)",
            height=220,
            placeholder="Paste your CV or resume here.",
        )

    # Collect settings below the JD/CV inputs in a single row.
    settings_left, settings_mid, settings_right = st.columns(3)
    with settings_left:
        model_name = st.selectbox(
            "Model",
            options=allowed_models,
            index=allowed_models.index(DEFAULT_MODEL)
            if DEFAULT_MODEL in allowed_models
            else 0,
        )
    with settings_mid:
        selected_label = st.selectbox(
            "Prompt variant",
            options=list(variant_labels.keys()),
        )
    with settings_right:
        if model_name == "gpt-5.2-chat-latest":
            verbosity_options = get_verbosity_options(model_name)
            verbosity = st.selectbox(
                "Verbosity",
                options=verbosity_options or [DEFAULT_VERBOSITY],
                index=(verbosity_options or [DEFAULT_VERBOSITY]).index(DEFAULT_VERBOSITY),
            )
            reasoning_effort = None
            temperature = None
        elif is_gpt5_model(model_name):
            effort_options = get_reasoning_effort_options(model_name)
            reasoning_effort = st.selectbox(
                "Reasoning effort",
                options=effort_options or [DEFAULT_REASONING_EFFORT],
                index=(effort_options or [DEFAULT_REASONING_EFFORT]).index(
                    DEFAULT_REASONING_EFFORT
                ),
            )
            verbosity = None
            temperature = None
        else:
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=1.0,
                value=0.2,
                step=0.05,
            )
            reasoning_effort = None
            verbosity = None

    st.divider()

    # Initialize or retrieve chat history from session state.
    messages = init_chat_history(st.session_state)

    # Render existing conversation turns in order.
    for message in messages:
        with st.chat_message(message.role):
            st.markdown(message.content)

    # Use the chat input so Enter sends the next message.
    user_input = st.chat_input("Ask for coaching, feedback, or practice questions")

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
            "temperature": temperature if temperature is not None else "default",
            "reasoning_effort": reasoning_effort or "default",
            "verbosity": verbosity or "default",
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
        reasoning_effort=reasoning_effort,
        verbosity=verbosity,
    )

    # Generate the assistant response and render it in the chat.
    with st.chat_message("assistant"):
        with st.spinner("Drafting response..."):
            ok, response = generate_chat_response(payload)

        if not ok:
            _LOGGER.info("chat_request_blocked")
            st.error(response)
            append_chat_message(messages, role="assistant", content=str(response))
            return

        content = str(response)

        st.markdown(content)
        append_chat_message(messages, role="assistant", content=content)
        _LOGGER.info("chat_request_success")
