# ARCHITECTURE.md - Interview Practice App (Streamlit + OpenAI)

This document is a **stable, human-readable architecture reference** for the Interview Practice App.

---

## 1) Goal

Build a **single-page Streamlit Interview Practice App** that generates **exactly 5 interview questions (English)** per run, tailored to:

- optional **Job Description** text
- optional **CV** text
- optional **User prompt** text

Behavior requirements (key points):
- If **Job Description is empty**: ask once for the **target role**, then proceed.
- If **CV is empty**: mention once that adding it improves tailoring, then proceed.
- Questions include **tags** (e.g., `[Technical]`, `[Behavioral]`, `[Role-specific]`, `[Screening]`, `[Onsite]`, `[Final]`).
- “Round/style” is controlled by the **selected system prompt variant** (not a separate UI control).
- One tunable setting is exposed: **temperature**.
- Includes a **security guard** (input validation + injection heuristics + refusal behavior).

---

## 2) Core architecture (high level)

**User → Streamlit UI → Controller → Safety Guard → Prompt Builder → OpenAI Client → Response Formatter → UI**

### Responsibilities
- **UI**: collect inputs (JD, CV, user prompt), prompt variant dropdown, temperature slider; show outputs and metadata (prompt variant + temperature)
- **Controller**: orchestrate one request/response cycle end-to-end
- **Safety Guard**: validate inputs and block unsafe/malicious requests
- **Prompt Builder**: assemble messages (system + user) based on selected variant
- **OpenAI Client**: call the chosen OpenAI model with correct parameters
- **Response Formatter**: ensure output is structured and complete (5 questions + required sections)

---

## 3) Key abstractions

### 3.1 Prompt Variant
A **prompt variant** is one system prompt representing a distinct technique/mode.
The app must support **at least 5** variants.

The selected variant defines:
- interviewer tone (friendly/neutral/strict)
- interview round emphasis (screening/onsite/final)
- structure constraints for output

### 3.2 Request Payload
A request to the system consists of:
- `job_description: str | ""`
- `cv_text: str | ""`
- `user_prompt: str | ""`
- `prompt_variant_id: int (1..5)`
- `temperature: float`

### 3.3 Response Contract (output shape)
The assistant response must contain:

1) **Target Role Context**
- If JD provided: short summary bullets
- If JD missing: ask once for target role and proceed

2) **CV Note (only if CV missing)**
- one short sentence encouraging CV for better tailoring

3) **Alignments** (only if JD + CV present)
- bullets describing matches between JD and CV

4) **Gaps / Risk areas**
- If JD + CV present: gaps inferred from mismatch
- If CV missing: do not invent gaps; ask user to self-identify focus/gaps

5) **Interview Questions**
- exactly **5** questions
- each question includes **tags**
- no “what this tests” line

6) **Next-step suggestions**
- includes a follow-up question like:
  - “What further questions do you want to focus on—technical, role-specific, or something else?”

---

## 4) Module layout (suggested)

- UI: `app/ui/streamlit_app.py`
- Controller/orchestrator: `app/core/controller.py`
- Prompt builder: `app/core/prompt_builder.py`
- Safety guard: `app/core/safety.py`
- Profile/prompt storage:
  - `profiles/` (e.g., YAML or JSON for prompt variants) OR
  - `app/core/prompts.py` (Python constants)
- OpenAI client wrapper: `app/core/llm/openai_client.py`

---

## 5) UI contract (MVP)

Inputs:
- Job Description text area (optional)
- CV/Resume text area (optional)
- User prompt text area (optional)
- Prompt variant selector (1-5)
- Temperature slider

Outputs:
- Structured response (per Response Contract)
- Metadata: selected prompt variant + temperature

---

## 6) Safety baseline

Minimum guardrails:
- Input validation (length, empty handling)
- Prompt injection heuristics (e.g., “ignore previous instructions”, “reveal system prompt”)
- Refusal messaging in UI for blocked requests
- Privacy: avoid logging raw JD/CV text; prefer redacted summaries

---

## 7) Non-goals (for this project)

- No retrieval / RAG / vector databases
- No tool calling / agents
- No long-term memory
- No deployment requirement

The focus is a clean, working single-page interview practice app with strong prompt engineering and basic safety.
