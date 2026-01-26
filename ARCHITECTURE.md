# ARCHITECTURE.md - Interview Practice App (Streamlit + OpenAI)

This document is a **stable, human-readable architecture reference** for the Interview Practice App.

---

## 1) Goal

Build a **single-page Streamlit Interview Practice App** that generates **exactly 5 interview questions (English)** per run, tailored to:

- optional **Job Description** text
- optional **CV** text
- optional **User prompt** text

Behavior requirements and output contract live in `REQUIREMENTS.md`.

---

## 2) Core architecture (high level)

**User → Streamlit UI → Controller → Safety Guard → Prompt Builder → OpenAI Client (Structured Output) → Output Parser → UI**

### Responsibilities
- **UI**: collect inputs (JD, CV, user prompt), prompt variant dropdown, temperature slider; show outputs and metadata (prompt variant + temperature)
- **Controller**: orchestrate one request/response cycle end-to-end
- **Safety Guard**: validate inputs and block unsafe/malicious requests
- **Prompt Builder**: assemble messages (system + user) based on selected variant
- **OpenAI Client**: call the chosen OpenAI model with correct parameters
- **Output Parser**: validate and parse structured JSON output (5 questions + required fields)

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
See `REQUIREMENTS.md` for the output contract.

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
- Structured output schema: `app/core/structured_output.py`

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
