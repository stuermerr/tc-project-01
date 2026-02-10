"""Shared helpers for Streamlit chat UIs."""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from collections.abc import Callable
from datetime import date
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

from app.core.chat_exports import (
    build_chat_pdf_bytes,
    build_response_pdf_bytes,
)
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
    get_allowed_models,
    get_reasoning_effort_options,
    is_gpt5_model,
)
from app.core.prompts import (
    DEFAULT_CHAT_PROMPT_VARIANT_ID,
    get_chat_prompt_variant_description,
    get_chat_prompt_variant_display_name,
)
from app.core.safety import check_rate_limit

_LOGGER = logging.getLogger(__name__)

# Keep a conservative character limit so chat history stays manageable.
_MAX_HISTORY_CHARS = 4000
# Summary should include as much of the transcript as possible.
_MAX_SUMMARY_HISTORY_CHARS = 28000

_COVER_LETTER_MARKERS = (
    "sehr geehrte",
    "mit freundlichen",
    "bewerbung",
    "anschreiben",
    "[unternehmen]",
    "[position]",
)


def _inject_chat_action_button_styles() -> None:
    """Apply compact styling to action buttons rendered inside chat messages."""

    st.markdown(
        """
<style>
div[data-testid="stChatMessage"] div[data-testid="stButton"] > button,
div[data-testid="stChatMessage"] div[data-testid="stDownloadButton"] > button {
  font-size: 0.84rem;
  padding: 0.20rem 0.55rem;
  min-height: 1.95rem;
}
</style>
        """,
        unsafe_allow_html=True,
    )


def _build_key(prefix: str, name: str) -> str:
    """Build a stable widget/session key scoped to a chat page."""

    return f"{prefix}_{name}"


def _extract_chat_text(value: Any) -> str:
    """Extract plain text from a chat input value."""

    if value is None:
        return ""
    if isinstance(value, str):
        return value
    text = getattr(value, "text", "")
    return text if isinstance(text, str) else ""


def _queue_chat_input(
    state: dict,
    chat_input_widget_key: str,
    pending_input_key: str,
) -> None:
    """Store submitted chat text in session state for reliable consumption."""

    text = _extract_chat_text(state.get(chat_input_widget_key))
    if text.strip():
        state[pending_input_key] = text


def _consume_chat_input(
    state: dict,
    pending_input_key: str,
    direct_chat_input: Any,
) -> str:
    """Consume queued chat input first, then fall back to direct return value."""

    queued = state.pop(pending_input_key, "")
    if isinstance(queued, str) and queued.strip():
        return queued
    return _extract_chat_text(direct_chat_input)


def _build_settings_snapshot(
    *,
    selected_label: str,
    selected_variant_id: int,
    model_name: str,
    temperature: float | None,
    reasoning_effort: str | None,
) -> dict[str, str]:
    """Create a serializable snapshot of active chat settings."""

    return {
        "selected_label": selected_label,
        "selected_variant_id": str(selected_variant_id),
        "model_name": model_name,
        "temperature": f"{temperature:.2f}" if temperature is not None else "default",
        "reasoning_effort": reasoning_effort or "default",
    }


def _build_settings_change_note(settings_snapshot: dict[str, str]) -> str:
    """Build a short note that tells the model settings changed this turn."""

    return (
        "[Configuration update for this response]\n"
        f"- Interview style: {settings_snapshot['selected_label']}\n"
        f"- Model: {settings_snapshot['model_name']}\n"
        f"- Temperature: {settings_snapshot['temperature']}\n"
        f"- Reasoning effort: {settings_snapshot['reasoning_effort']}\n"
        "Apply this updated configuration from this response onward."
    )


def _prepend_settings_note(history_prompt: str, settings_snapshot: dict[str, str]) -> str:
    """Prepend a settings update note to the serialized chat history."""

    note = _build_settings_change_note(settings_snapshot)
    if history_prompt:
        return f"{note}\n\n{history_prompt}"
    return note


def _prepend_current_date_note(history_prompt: str) -> str:
    """Add today's date so cover-letter generation can use an explicit value."""

    current_date = date.today().strftime("%B %d, %Y").replace(" 0", " ")
    note = f"[Current date: {current_date}]"
    if history_prompt:
        return f"{note}\n\n{history_prompt}"
    return note


def _format_applied_settings_caption(
    *,
    model_name: str,
    selected_label: str,
    temperature: float | None,
    reasoning_effort: str | None,
) -> str:
    """Render a compact caption that confirms which settings were applied."""

    if temperature is None:
        return (
            f"Using `{model_name}` | style: `{selected_label}` | "
            f"reasoning effort: `{reasoning_effort or 'default'}`"
        )
    return (
        f"Using `{model_name}` | style: `{selected_label}` | "
        f"temperature: `{temperature:.2f}`"
    )


def _looks_like_cover_letter(text: str) -> bool:
    """Return True when assistant text resembles a cover letter."""

    lowered = text.lower()
    marker_hits = sum(1 for marker in _COVER_LETTER_MARKERS if marker in lowered)
    if marker_hits >= 2:
        return True
    # Handle short letters that still include a greeting and closing.
    if "sehr geehrte" in lowered and "mit freundlichen" in lowered:
        return True
    return False


def _is_mock_interview_request(user_input: str) -> bool:
    """Return True when user requests an interview-mode switch."""

    lowered = user_input.lower()
    return any(
        phrase in lowered
        for phrase in (
            "mock interview",
            "start interview",
            "interview me",
            "start a mock",
        )
    )


def _build_prompt_history(messages: list[ChatMessage], max_chars: int) -> str:
    """Serialize chat history for prompting without mutating stored transcript."""

    # Copy messages so trimming does not remove items from the visible chat/export history.
    prompt_messages = [
        ChatMessage(role=message.role, content=message.content, message_type=message.message_type)
        for message in messages
    ]
    trim_chat_history(prompt_messages, max_chars=max_chars)
    return _history_to_prompt(prompt_messages)


def _scroll_to_latest_assistant_message_top() -> None:
    """Scroll viewport to the top of the latest assistant message."""

    components.html(
        """
<script>
const doc = window.parent.document;
const chatMessages = doc.querySelectorAll('[data-testid="stChatMessage"]');
if (chatMessages.length > 0) {
  const lastMessage = chatMessages[chatMessages.length - 1];
  lastMessage.scrollIntoView({ behavior: "smooth", block: "start" });
}
</script>
        """,
        height=0,
    )


def _render_copy_button(
    *,
    label: str,
    content: str,
    element_key: str,
) -> None:
    """Render a browser-side copy-to-clipboard button for arbitrary text."""

    button_id = f"copy_{hashlib.sha1(element_key.encode('utf-8')).hexdigest()[:12]}"
    button_label_json = json.dumps(label)
    content_json = json.dumps(content)
    html = f"""
<button id="{button_id}" style="font-size:0.84rem;padding:0.20rem 0.55rem;border-radius:0.45rem;border:1px solid #ccc;background:#f7f7f7;cursor:pointer;">
  {label}
</button>
<script>
const button = document.getElementById("{button_id}");
button.addEventListener("click", async () => {{
  const original = button.textContent;
  try {{
    await navigator.clipboard.writeText({content_json});
    button.textContent = "Copied";
  }} catch (e) {{
    button.textContent = "Copy failed";
  }}
  setTimeout(() => {{
    button.textContent = JSON.parse({button_label_json});
  }}, 1200);
}});
</script>
"""
    components.html(html, height=38)


def _render_assistant_message_actions(
    *,
    message: ChatMessage,
    message_index: int,
    latest_assistant_index: int,
    all_messages: list[ChatMessage],
    state_key_prefix: str,
) -> bool:
    """Render copy/download actions for assistant messages."""

    # Keep controls attached to the latest assistant message for better discoverability.
    is_latest = message_index == latest_assistant_index
    action_cols = st.columns([1, 1, 1, 1] if is_latest else [1, 1, 2, 0.01])
    with action_cols[0]:
        _render_copy_button(
            label="Copy response",
            content=message.content,
            element_key=_build_key(state_key_prefix, f"copy_response_{message_index}"),
        )
    with action_cols[1]:
        st.download_button(
            "Download Response (PDF)",
            data=build_response_pdf_bytes(message.content),
            file_name=f"assistant_response_{message_index + 1}.pdf",
            mime="application/pdf",
            key=_build_key(state_key_prefix, f"response_pdf_{message_index}"),
        )
    if is_latest:
        with action_cols[2]:
            summary_requested = st.button(
                "Summarize Chat",
                key=_build_key(state_key_prefix, f"summary_button_{message_index}"),
            )
        with action_cols[3]:
            st.download_button(
                "Download Full Chat (PDF)",
                data=build_chat_pdf_bytes(all_messages),
                file_name="interview_chat_transcript.pdf",
                mime="application/pdf",
                key=_build_key(state_key_prefix, f"chat_pdf_button_{message_index}"),
            )
        return summary_requested
    return False


def _build_payload(
    job_description: str,
    cv_text: str,
    user_prompt: str,
    prompt_variant_id: int,
    temperature: float | None,
    model_name: str,
    reasoning_effort: str | None,
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
    )


def _history_to_prompt(messages: list[ChatMessage]) -> str:
    """Serialize chat history into a single prompt string."""

    # Convert chat turns into a simple transcript format.
    lines: list[str] = []
    for message in messages:
        role = "User" if message.role == "user" else "Assistant"
        lines.append(f"{role}: {message.content}")
    return "\n".join(lines).strip()


def render_chat_ui(
    *,
    page_title: str,
    caption: str,
    prompt_variants: list,
    prompt_label: str,
    state_key_prefix: str,
    generate_response: Callable[[RequestPayload], tuple[bool, str]],
    generate_cover_letter: Callable[[RequestPayload], tuple[bool, str]],
    generate_summary: Callable[[RequestPayload], tuple[bool, str]],
) -> None:
    """Render a chat UI with pluggable backend response generation."""

    st.title(page_title)
    st.caption(caption)
    _inject_chat_action_button_styles()

    # Build clear user-facing labels while keeping stable numeric IDs in payloads.
    variant_options: list[tuple[str, int]] = []
    for variant in prompt_variants:
        variant_options.append(
            (
                get_chat_prompt_variant_display_name(variant.id, variant.name),
                variant.id,
            )
        )
    variant_labels = {label: variant_id for label, variant_id in variant_options}
    variant_ids = [variant_id for _, variant_id in variant_options]
    default_variant_index = (
        variant_ids.index(DEFAULT_CHAT_PROMPT_VARIANT_ID)
        if DEFAULT_CHAT_PROMPT_VARIANT_ID in variant_ids
        else 0
    )
    # Scope widget/session keys so each chat page can keep independent state.
    model_key = _build_key(state_key_prefix, "model")
    variant_key = _build_key(state_key_prefix, "variant")
    reasoning_key = _build_key(state_key_prefix, "reasoning_effort")
    temperature_key = _build_key(state_key_prefix, "temperature")
    chat_input_widget_key = _build_key(state_key_prefix, "chat_input")
    pending_input_key = _build_key(state_key_prefix, "pending_chat_input")
    cover_letter_button_key = _build_key(state_key_prefix, "cover_letter_button")
    last_applied_settings_key = _build_key(state_key_prefix, "last_applied_settings")
    cover_letter_context_key = _build_key(state_key_prefix, "cover_letter_context_active")
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
            key=model_key,
        )
    with settings_mid:
        selected_label = st.selectbox(
            prompt_label,
            options=[label for label, _ in variant_options],
            index=default_variant_index,
            key=variant_key,
        )
        selected_variant_id = variant_labels[selected_label]
        # Keep a short explanation near the selector to clarify each mode.
        variant_description = get_chat_prompt_variant_description(selected_variant_id)
        if variant_description:
            st.caption(variant_description)
    with settings_right:
        if model_name == "gpt-5.2-chat-latest":
            st.empty()
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
                key=reasoning_key,
            )
            temperature = None
        else:
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=1.0,
                value=0.2,
                step=0.05,
                key=temperature_key,
            )
            reasoning_effort = None

    # Capture the selected settings so request handling can compare against prior turns.
    settings_snapshot = _build_settings_snapshot(
        selected_label=selected_label,
        selected_variant_id=selected_variant_id,
        model_name=model_name,
        temperature=temperature,
        reasoning_effort=reasoning_effort,
    )

    st.divider()

    # Initialize or retrieve chat history from session state.
    messages = init_chat_history(st.session_state)
    assistant_indices = [idx for idx, msg in enumerate(messages) if msg.role == "assistant"]
    latest_assistant_index = assistant_indices[-1] if assistant_indices else -1

    # Render existing conversation turns in order.
    summary_requested = False
    for index, message in enumerate(messages):
        with st.chat_message(message.role):
            st.markdown(message.content)
            if message.role == "assistant":
                summary_requested = (
                    _render_assistant_message_actions(
                        message=message,
                        message_index=index,
                        latest_assistant_index=latest_assistant_index,
                        all_messages=messages,
                        state_key_prefix=state_key_prefix,
                    )
                    or summary_requested
                )

    # Keep cover letter generation available as a primary action.
    missing_cover_letter_inputs = not (job_description.strip() and cv_text.strip())
    cover_letter_requested = st.button(
        "Generate cover letter (German)",
        disabled=missing_cover_letter_inputs,
        help=(
            "Please add both a job description and a CV to generate a cover letter."
            if missing_cover_letter_inputs
            else None
        ),
        key=cover_letter_button_key,
    )

    # Use a queued submit callback to avoid dropping a turn on reruns.
    direct_chat_input = st.chat_input(
        "Ask for coaching, feedback, or practice questions",
        key=chat_input_widget_key,
        on_submit=_queue_chat_input,
        kwargs={
            "state": st.session_state,
            "chat_input_widget_key": chat_input_widget_key,
            "pending_input_key": pending_input_key,
        },
    )
    user_input = _consume_chat_input(
        st.session_state, pending_input_key, direct_chat_input
    )
    has_user_input = bool(user_input.strip())

    if not has_user_input and not cover_letter_requested and not summary_requested:
        return

    # Detect whether settings changed since the previous sent request.
    last_applied_settings = st.session_state.get(last_applied_settings_key)
    settings_changed = (
        isinstance(last_applied_settings, dict)
        and last_applied_settings != settings_snapshot
    )
    # Mark current settings as the ones used for this submitted turn.
    st.session_state[last_applied_settings_key] = settings_snapshot

    # Record a request-level log entry without exposing user content.
    log_event = "chat_message_received"
    if cover_letter_requested:
        log_event = "cover_letter_button_clicked"
    elif summary_requested:
        log_event = "chat_summary_button_clicked"
    _LOGGER.info(
        log_event,
        extra={
            "job_description_length": len(job_description),
            "cv_text_length": len(cv_text),
            "user_prompt_length": len(user_input or ""),
            "selected_variant": selected_label,
            "selected_variant_id": selected_variant_id,
            "temperature": temperature if temperature is not None else "default",
            "reasoning_effort": reasoning_effort or "default",
            "model_name": model_name,
            "settings_changed": settings_changed,
        },
    )
    # Emit a plain log line so active settings are visible with the default formatter.
    _LOGGER.info(
        "chat_request_settings model=%s variant_id=%s variant_label=%s temperature=%s reasoning_effort=%s settings_changed=%s",
        model_name,
        selected_variant_id,
        selected_label,
        settings_snapshot["temperature"],
        settings_snapshot["reasoning_effort"],
        settings_changed,
    )

    # Rate limit per session to prevent accidental rapid-fire requests.
    if "rate_limit_key" not in st.session_state:
        st.session_state["rate_limit_key"] = str(uuid.uuid4())
    ok, refusal = check_rate_limit(st.session_state["rate_limit_key"])
    if not ok:
        _LOGGER.info("chat_rate_limited")
        st.error(refusal or "Too many requests. Please try again.")
        return

    # Append the user message and build a prompt snapshot for the model.
    if has_user_input:
        user_requested_mock = _is_mock_interview_request(user_input)
        if user_requested_mock:
            st.session_state[cover_letter_context_key] = False
        cover_letter_context_active = bool(
            st.session_state.get(cover_letter_context_key, False)
        )

        append_chat_message(messages, role="user", content=user_input, message_type="user")
        history_prompt = _build_prompt_history(messages, max_chars=_MAX_HISTORY_CHARS)
        if settings_changed:
            history_prompt = _prepend_settings_note(history_prompt, settings_snapshot)

        # Show the user message in the chat UI.
        with st.chat_message("user"):
            st.markdown(user_input)

        payload = _build_payload(
            job_description=job_description,
            cv_text=cv_text,
            user_prompt=history_prompt,
            prompt_variant_id=selected_variant_id,
            temperature=temperature,
            model_name=model_name,
            reasoning_effort=reasoning_effort,
        )

        # Generate the assistant response and render it in the chat.
        with st.chat_message("assistant"):
            with st.spinner("Drafting response..."):
                ok, response = generate_response(payload)

            if not ok:
                _LOGGER.info("chat_request_blocked")
                st.error(response)
                append_chat_message(
                    messages, role="assistant", content=str(response), message_type="chat"
                )
                return

            content = str(response)
            response_is_cover_letter = _looks_like_cover_letter(content) or (
                cover_letter_context_active and not user_requested_mock
            )
            response_message_type = "cover_letter" if response_is_cover_letter else "chat"
            if response_is_cover_letter:
                st.session_state[cover_letter_context_key] = True

            append_chat_message(
                messages,
                role="assistant",
                content=content,
                message_type=response_message_type,
            )
            response_index = len(messages) - 1
            st.markdown(content)
            st.caption(
                _format_applied_settings_caption(
                    model_name=model_name,
                    selected_label=selected_label,
                    temperature=temperature,
                    reasoning_effort=reasoning_effort,
                )
            )
            _render_assistant_message_actions(
                message=messages[response_index],
                message_index=response_index,
                latest_assistant_index=response_index,
                all_messages=messages,
                state_key_prefix=state_key_prefix,
            )
            _scroll_to_latest_assistant_message_top()
            _LOGGER.info("chat_request_success")
        return

    # Generate a summary using the existing chat history.
    if summary_requested:
        history_prompt = _build_prompt_history(
            messages, max_chars=_MAX_SUMMARY_HISTORY_CHARS
        )
        if settings_changed:
            history_prompt = _prepend_settings_note(history_prompt, settings_snapshot)
        payload = _build_payload(
            job_description=job_description,
            cv_text=cv_text,
            user_prompt=history_prompt,
            prompt_variant_id=selected_variant_id,
            temperature=temperature,
            model_name=model_name,
            reasoning_effort=reasoning_effort,
        )

        with st.chat_message("assistant"):
            with st.spinner("Summarizing chat..."):
                ok, response = generate_summary(payload)

            if not ok:
                _LOGGER.info("chat_summary_request_blocked")
                st.error(response)
                append_chat_message(
                    messages,
                    role="assistant",
                    content=str(response),
                    message_type="summary",
                )
                return

            content = str(response)
            append_chat_message(
                messages,
                role="assistant",
                content=content,
                message_type="summary",
            )
            response_index = len(messages) - 1
            st.markdown(content)
            st.caption(
                _format_applied_settings_caption(
                    model_name=model_name,
                    selected_label=selected_label,
                    temperature=temperature,
                    reasoning_effort=reasoning_effort,
                )
            )
            _render_assistant_message_actions(
                message=messages[response_index],
                message_index=response_index,
                latest_assistant_index=response_index,
                all_messages=messages,
                state_key_prefix=state_key_prefix,
            )
            _scroll_to_latest_assistant_message_top()
            _LOGGER.info("chat_summary_request_success")
        return

    # Generate a cover letter using the existing chat history.
    history_prompt = _build_prompt_history(messages, max_chars=_MAX_HISTORY_CHARS)
    history_prompt = _prepend_current_date_note(history_prompt)
    if settings_changed:
        history_prompt = _prepend_settings_note(history_prompt, settings_snapshot)
    payload = _build_payload(
        job_description=job_description,
        cv_text=cv_text,
        user_prompt=history_prompt,
        prompt_variant_id=selected_variant_id,
        temperature=temperature,
        model_name=model_name,
        reasoning_effort=reasoning_effort,
    )

    # Generate the cover letter and render it in the chat.
    with st.chat_message("assistant"):
        with st.spinner("Drafting cover letter..."):
            ok, response = generate_cover_letter(payload)

        if not ok:
            _LOGGER.info("cover_letter_request_blocked")
            st.error(response)
            append_chat_message(
                messages,
                role="assistant",
                content=str(response),
                message_type="chat",
            )
            return

        content = str(response)
        st.session_state[cover_letter_context_key] = True
        append_chat_message(
            messages,
            role="assistant",
            content=content,
            message_type="cover_letter",
        )
        response_index = len(messages) - 1
        st.markdown(content)
        st.caption(
            _format_applied_settings_caption(
                model_name=model_name,
                selected_label=selected_label,
                temperature=temperature,
                reasoning_effort=reasoning_effort,
            )
        )
        _render_assistant_message_actions(
            message=messages[response_index],
            message_index=response_index,
            latest_assistant_index=response_index,
            all_messages=messages,
            state_key_prefix=state_key_prefix,
        )
        _scroll_to_latest_assistant_message_top()
        _LOGGER.info("cover_letter_request_success")
