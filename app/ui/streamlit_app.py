"""Single-page Streamlit UI for the interview practice app."""

from __future__ import annotations

import logging
import uuid

import streamlit as st

from app.core.dataclasses import RequestPayload
from app.core.logging_config import setup_logging
from app.core.orchestration import generate_questions
from app.core.prompts import get_prompt_variants
from app.core.safety import check_rate_limit

_LOGGER = logging.getLogger(__name__)

def _build_payload(
    job_description: str,
    cv_text: str,
    user_prompt: str,
    prompt_variant_id: int,
    temperature: float,
) -> RequestPayload:
    # Bundle raw UI inputs into a typed payload for the controller.
    return RequestPayload(
        job_description=job_description,
        cv_text=cv_text,
        user_prompt=user_prompt,
        prompt_variant_id=prompt_variant_id,
        temperature=temperature,
    )


def main() -> None:
    # Ensure standard console logging is active before any log calls.
    setup_logging()
    # Configure the page once at startup to control layout and branding.
    st.set_page_config(page_title="Interview Practice", page_icon="🧩", layout="wide")
    st.title("Interview Practice App")
    st.caption("Generate tailored interview questions from your JD, CV, and focus areas.")

    # Load prompt variants to populate the dropdown.
    variants = get_prompt_variants()
    # Map labels to ids so the UI stays readable while the payload stays numeric.
    variant_labels = {variant.name: variant.id for variant in variants}

    # Two-column layout keeps the three text inputs visible at once.
    col_left, col_right = st.columns(2)
    with col_left:
        # Capture JD and CV inputs on the left to match typical reading order.
        job_description = st.text_area(
            "Job Description (optional)",
            height=220,
            placeholder="Paste the target role description here.",
        )
        cv_text = st.text_area(
            "CV / Resume (optional)",
            height=220,
            placeholder="Paste your CV or resume here.",
        )
    with col_right:
        # Capture user prompt and settings on the right for quick tuning.
        user_prompt = st.text_area(
            "User Prompt (optional)",
            height=220,
            placeholder="e.g., Focus on backend APIs and system design.",
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

    st.divider()

    # Trigger a single generation run on button click.
    generate_clicked = st.button("Generate 5 Questions", type="primary")
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
            # Display the JSON directly to avoid hard-coded formatting rules.
            st.json(response)
        else:
            st.markdown(response)

        # Echo metadata so users can reproduce results.
        st.caption(
            f"Prompt variant: {selected_label} | Temperature: {temperature:.2f}"
        )
        _LOGGER.info("ui_request_success")


if __name__ == "__main__":
    # Allow `python streamlit_app.py` for local debugging.
    main()
