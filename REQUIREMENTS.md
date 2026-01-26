🧩 **Sprint 1 Project Description (MVP)**

## 🎯 What you’re building

A single-page Streamlit Interview Practice App focused on generating tailored interview questions based on:

- 📄 Job description of the target role (optional input)
- 📎 CV/resume as plain text (optional input)
- ✍️ User prompt (optional guidance like “focus on system design”)

The app calls an OpenAI model to:

- generate exactly 5 interview questions (English)
- tailor questions to the job description and/or CV when provided
- ask for missing info once when key fields are empty (JD/CV)

---

## 🖥️ UI (Streamlit) — Single Page Layout (MVP)

### ✅ Inputs

**📄 Job Description (optional)**  
- Large text area (copy/paste full JD)  
- If empty: the assistant asks once:  
  > “What is the target role?”

**📎 CV / Resume (optional)**  
- Large text area (copy/paste CV text)  
- If empty: the assistant mentions once in the initial answer:  
  > “If you paste your CV, I can tailor the questions more precisely.”

**✍️ User prompt (optional)**  
- e.g., “Focus on backend + APIs” or “Ask hard questions”

**🧪 Prompt variant selector (dropdown)**  
- Variant 1–5 (your 5 system prompts)

**⚙️ LLM settings**  
- ⚙️ Temperature slider for `gpt-4o-mini`
- ⚙️ Reasoning effort selector for `gpt-5-nano` and `gpt-5.2-chat-latest`
- Temperature is not sent for GPT-5 models (use their default)

### ✅ Buttons

- ▶️ Generate 5 Questions (calls OpenAI)  
- 🧹 Reset (optional)

### ✅ Outputs

- 🗨️ 5 generated interview questions (English, structured)
- ✅ Metadata: selected prompt variant + temperature

---

## 🤖 LLM Behavior (Classic mode output contract)

When the user clicks **Generate 5 Questions** in the classic UI, the assistant outputs **structured JSON** with these keys:

```json
{
  "target_role_context": ["..."],
  "cv_note": "... or null",
  "alignments": ["..."],
  "gaps_or_risk_areas": ["..."],
  "interview_questions": ["[Technical] ...?", "..."],
  "next_step_suggestions": ["...", "..."]
}
```

Each key follows the rules below:

### 🧾 Target Role Context (`target_role_context`)
- If JD is provided: 1–3 bullets summarizing role expectations  
- If JD is missing: ask once for the target role, then proceed

### 📎 CV Note (`cv_note`, only if CV missing)
- One short sentence encouraging CV paste for better tailoring

### 🧠 Alignments (`alignments`, only if CV + JD provided)
- 2–5 bullets: where CV matches JD

### ⚠️ Gaps / Risk areas (`gaps_or_risk_areas`)
- If CV + JD provided:
  - list gaps inferred from mismatch
- If CV is missing:
  - do not invent gaps
  - instead ask the user to self-identify focus/gaps, e.g.:
    - “What should we focus on?”
    - “Which requirements from the job description do you not satisfy?”
    - “Rate key requirements 0–5 (0 none → 5 expert).”

### ❓ Interview Questions (`interview_questions`, main output)
- Exactly 5 questions in English
- Each question includes tags, e.g.:
  - [Technical], [Behavioral], [Role-specific], [Screening], [Onsite], [Final]
- The “round” style (screening/onsite/final) is represented via the selected system prompt variant (not a separate UI control)

### 🔁 Next-step suggestions (`next_step_suggestions`)
- Include 2–4 follow-ups such as:
  - “Paste your CV for better alignment-based questions.”
  - “Tell me which requirements you rate lowest (0–5).”
  - “Ask for another set of 5 questions.”
  - “What further questions do you want to focus on—technical, role-specific, or something else?”

> Note: The assistant should not reveal chain-of-thought. Output stays concise and structured.

---

## 🤖 LLM Behavior (Chat mode, flexible output)

Chat mode is intentionally **free-form** and does **not** require JSON output. It should behave like a natural coaching conversation and adapt to the user's inputs.

### ✅ Initial assistant response (guideline, not a rigid format)
For the **first assistant response only**, the model should *aim* to include:
- A brief summary of the JD / target role context (if available)
- A short alignment or strengths note (if CV/JD provided)
- A short gaps or risk note (if applicable)
- **Five** preparation questions (these can be labeled or unlabeled)
- A few practical tips or next steps

This is **high-level guidance** only. The response must remain flexible to the user's prompt and **must not be constrained** to this structure. If the transcript already includes an Assistant turn, do not re-apply the initial structure (model switches do not reset this).

### ✅ Follow-up responses (free-form)
After the initial response, the chat should behave freely:
- Respond directly to user answers
- Provide feedback, corrections, and tips
- **Score or rate** answers when helpful
- Ask follow-up questions as needed (not necessarily exactly 5)

### ✅ Prompt variants (chat)
Chat mode has its own prompt variants (selectable via the dropdown), and these **must not** include strict JSON or schema enforcement.

---

## 🧠 Prompt Engineering Requirement (Sprint 1)

You will write at least 5 system prompts, selectable via dropdown. These represent different prompting techniques and/or interviewer modes, for example:

- Friendly Screening Round (supportive tone, broad fit)
- Neutral Technical Round (professional tone, skill depth)
- Strict Onsite Round (challenging, high standards)
- Clarify-first (asks key questions before generating)
- Few-shot (includes example JD/CV → question patterns)

---

## 🔐 Security Guard (Sprint 1 requirement)

Before calling the model:

- block obvious prompt injection attempts (e.g., “ignore previous instructions”, “reveal system prompt”)
- reject illegal/harmful requests
- enforce max length on JD/CV/user prompt
  - Job Description max length: 6000 characters
- CV max length: 4000 characters
  - Classic user prompt max length: 2000 characters
  - Chat user prompt max length: 30000 characters
- show a refusal message in the UI if triggered

---

## ✅ Sprint 1 course requirements — satisfied

- ✅ Single-page web app → Streamlit
- ✅ OpenAI API call + API key usage
- ✅ Choose one allowed model (GPT-4.1 / GPT-4.1 mini / GPT-4.1 nano / GPT-4o / GPT-4o mini)
- ✅ At least 5 system prompts with different techniques
- ✅ Tune ≥ 1 OpenAI setting → Temperature
- ✅ Add ≥ 1 security guard → input validation + injection defense

---

## 🧩 Optional Features (Out of Sprint 1 scope)

- Provide the user with the ability to choose from a list of LLM models
- Deploy the app to the Internet
- Use Streamlit to implement a full-fledged chatbot application instead of a one-time call
- Use LangChain packages to implement the app using chains or agents

---

## 🧭 Sprint 2 (Optional Additions) — Planned Scope

These items extend the MVP without changing Sprint 1 requirements. They should be implemented in small, testable steps.

### 1) Streamlit layout refresh (classic single-shot mode)
- JD and CV inputs appear side-by-side at the top.
- Settings (model selector, prompt variant, temperature) appear below JD/CV.
- User prompt appears below settings in a smaller input.
- "Generate 5 Questions" button is centered at the bottom.
- Pressing Enter should submit the request (same as clicking the button).

### 2) MVP chat experience (new chat mode)
- Multi-turn chat UI using Streamlit chat components.
- Session history is preserved across turns.
- Chat responses are **free-form**, not JSON-structured.
- Initial assistant response should *loosely* follow the high-level structure:
  - brief JD/role summary, alignments, gaps, **5 prep questions**, tips
  - this is a guideline only; the response must remain flexible
- Follow-up responses are fully conversational:
  - evaluate user answers, give feedback and tips, **allow scoring**
  - ask follow-up questions as needed (not fixed to 5)
- Prompt variants for chat are selectable via dropdown and do **not** enforce structured output.
- MVP scope: keep it simple, no tool calling or long-term memory.

### 3) Model selection (OpenAI)
- Provide a dropdown with exactly these models:
  - `gpt-4o-mini`
  - `gpt-5-nano`
  - `gpt-5.2-chat-latest`
- Selected model is passed to the OpenAI API client (and LangChain client in the secondary app).

### 4) LangChain-based “second app”
- Keep the current implementation intact.
- Add a parallel Streamlit entrypoint that implements the same behavior using LangChain chains/agents.
- Both apps can be run and compared independently.

### 5) Streamlit deployment
- Provide deployment configuration and a short runbook.
- Make it clear which Streamlit entrypoint is intended for deployment.
