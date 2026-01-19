"""Single-page Streamlit UI for the interview practice app."""

from __future__ import annotations

import streamlit as st

from app.core.dataclasses import RequestPayload
from app.core.orchestration import generate_questions
from app.core.prompts import get_prompt_variants


def _build_payload(
    job_description: str,
    cv_text: str,
    user_prompt: str,
    prompt_variant_id: int,
    temperature: float,
) -> RequestPayload:
    return RequestPayload(
        job_description=job_description,
        cv_text=cv_text,
        user_prompt=user_prompt,
        prompt_variant_id=prompt_variant_id,
        temperature=temperature,
    )


def main() -> None:
    st.set_page_config(page_title="Interview Practice", page_icon="🧩", layout="wide")
    st.title("Interview Practice App")
    st.caption("Generate tailored interview questions from your JD, CV, and focus areas.")

    variants = get_prompt_variants()
    variant_labels = {variant.name: variant.id for variant in variants}

    col_left, col_right = st.columns(2)
    with col_left:
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

    generate_clicked = st.button("Generate 5 Questions", type="primary")
    if generate_clicked:
        payload = _build_payload(
            job_description=job_description,
            cv_text=cv_text,
            user_prompt=user_prompt,
            prompt_variant_id=variant_labels[selected_label],
            temperature=temperature,
        )

        with st.spinner("Generating questions..."):
            ok, response = generate_questions(payload)

        if not ok:
            st.error(response)
            return

        st.subheader("Generated Questions")
        st.markdown(response)

        st.caption(
            f"Prompt variant: {selected_label} | Temperature: {temperature:.2f}"
        )


if __name__ == "__main__":
    main()
