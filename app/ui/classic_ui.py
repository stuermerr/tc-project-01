"""Classic single-shot UI rendering helpers."""

from __future__ import annotations

import logging
import uuid

import streamlit as st

from app.core.dataclasses import RequestPayload
from app.core.model_catalog import DEFAULT_MODEL, get_allowed_models
from app.core.orchestration import generate_questions
from app.core.prompts import get_prompt_variants
from app.core.safety import check_rate_limit
from app.core.structured_output import render_markdown_from_response

_LOGGER = logging.getLogger(__name__)


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


def render_classic_ui() -> None:
    """Render the single-shot classic UI without resetting page config."""

    st.title("Interview Practice App")
    st.caption("Generate tailored interview questions from your JD, CV, and focus areas.")

    # Load prompt variants to populate the dropdown.
    variants = get_prompt_variants()
    # Map labels to ids so the UI stays readable while the payload stays numeric.
    variant_labels = {variant.name: variant.id for variant in variants}

    # Load the supported model list so the UI stays in sync with the backend.
    allowed_models = get_allowed_models()

    # Wrap inputs in a form so Enter can submit from the single-line prompt field.
    with st.form("question_generator_form"):
        # Place JD and CV side-by-side at the top for easy comparison.
        col_left, col_right = st.columns(2)
        with col_left:
            # Capture JD input on the left to match typical reading order.
            job_description = st.text_area(
                "Job Description (optional)",
                height=220,
                placeholder="Paste the target role description here.",
            )
        with col_right:
            # Capture CV input on the right so both documents stay visible.
            cv_text = st.text_area(
                "CV / Resume (optional)",
                height=220,
                placeholder="Paste your CV or resume here.",
            )

        # Collect settings below the JD/CV inputs in a single row.
        settings_left, settings_mid, settings_right = st.columns(3)
        with settings_left:
            # Let users pick from the supported models while defaulting to the baseline.
            model_name = st.selectbox(
                "Model",
                options=allowed_models,
                index=allowed_models.index(DEFAULT_MODEL)
                if DEFAULT_MODEL in allowed_models
                else 0,
            )
        with settings_mid:
            # Prompt variant stays visible next to the model selector.
            selected_label = st.selectbox(
                "Prompt variant",
                options=list(variant_labels.keys()),
            )
        with settings_right:
            # Keep temperature tuning accessible without crowding the inputs.
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=1.0,
                value=0.2,
                step=0.05,
            )

        # Smaller single-line prompt lets Enter submit the form.
        user_prompt = st.text_input(
            "User Prompt (optional)",
            placeholder="e.g., Focus on backend APIs and system design.",
        )

        # Center the submit button at the bottom of the form.
        _, button_col, _ = st.columns([1, 1, 1])
        generate_clicked = button_col.form_submit_button(
            "Generate 5 Questions", type="primary"
        )

    st.divider()
    if generate_clicked:
        # Capture a request-level log entry without exposing user content.
        _LOGGER.info(
            "ui_generate_clicked",
            extra={
                "job_description_length": len(job_description),
                "cv_text_length": len(cv_text),
                "user_prompt_length": len(user_prompt),
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
            _LOGGER.info("ui_rate_limited")
            st.error(refusal or "Too many requests. Please try again.")
            return

        # Build the payload once so the controller gets a stable snapshot.
        payload = _build_payload(
            job_description=job_description,
            cv_text=cv_text,
            user_prompt=user_prompt,
            prompt_variant_id=variant_labels[selected_label],
            temperature=temperature,
            model_name=model_name,
        )

        # Show a spinner while the model call runs.
        with st.spinner("Generating questions..."):
            ok, response = generate_questions(payload)

        if not ok:
            # Surface safety refusals or validation errors to the user.
            _LOGGER.info("ui_request_blocked")
            st.error(response)
            return

        # Render the structured response returned by the controller.
        st.subheader("Generated Questions")
        if isinstance(response, dict):
            # Convert structured output into readable markdown for display.
            st.markdown(render_markdown_from_response(response))
        else:
            st.markdown(response)

        # Echo metadata so users can reproduce results.
        st.caption(
            f"Model: {model_name} | Prompt variant: {selected_label} | "
            f"Temperature: {temperature:.2f}"
        )
        _LOGGER.info("ui_request_success")
