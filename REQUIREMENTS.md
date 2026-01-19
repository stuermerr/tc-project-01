🧩 Sprint 1 Project Description (MVP)
🎯 What you’re building

A single-page Streamlit Interview Practice App focused on generating tailored interview questions based on:

📄 Job description of the target role (optional input)

📎 CV/resume as plain text (optional input)

✍️ User prompt (optional guidance like “focus on system design”)

The app calls an OpenAI model to:

generate exactly 5 interview questions (English)

tailor questions to the job description and/or CV when provided

ask for missing info once when key fields are empty (JD/CV)

🖥️ UI (Streamlit) — Single Page Layout (MVP)
✅ Inputs

📄 Job Description (optional)

Large text area (copy/paste full JD)

If empty: the assistant asks once: “What is the target role?”

📎 CV / Resume (optional)

Large text area (copy/paste CV text)

If empty: the assistant mentions once in the initial answer:

“If you paste your CV, I can tailor the questions more precisely.”

✍️ User prompt (optional)

e.g., “Focus on backend + APIs” or “Ask hard questions”

🧪 Prompt variant selector (dropdown)

Variant 1–5 (your 5 system prompts)

⚙️ LLM settings

⚙️ Temperature slider (Sprint 1 tuning requirement)

✅ Buttons

▶️ Generate 5 Questions (calls OpenAI)

🧹 Reset (optional)

✅ Outputs

🗨️ 5 generated interview questions (English, structured)

✅ Metadata: selected prompt variant + temperature

🤖 LLM Behavior (MVP output contract)

When the user clicks Generate 5 Questions, the assistant outputs:

🧾 Target Role Context

If JD is provided: 1–3 bullets summarizing role expectations

If JD is missing: ask once for the target role, then proceed

📎 CV Note (only if CV missing)

One short sentence encouraging CV paste for better tailoring

🧠 Alignments (only if CV + JD provided)

2–5 bullets: where CV matches JD

⚠️ Gaps / Risk areas

If CV + JD provided:

list gaps inferred from mismatch

If CV is missing:

do not invent gaps

instead ask the user to self-identify focus/gaps, e.g.:

“What should we focus on?”

“Which requirements from the job description do you not satisfy?”

“Rate key requirements 0–5 (0 none → 5 expert).”

❓ Interview Questions (main output)

Exactly 5 questions in English

Each question includes tags, e.g.:

[Technical], [Behavioral], [Role-specific], [Screening], [Onsite], [Final]

The “round” style (screening/onsite/final) is represented via the selected system prompt variant (not a separate UI control)

🔁 Next-step suggestions

Include 2–4 follow-ups such as:

“Paste your CV for better alignment-based questions.”

“Tell me which requirements you rate lowest (0–5).”

“Ask for another set of 5 questions.”

“What further questions do you want to focus on—technical, role-specific, or something else?”

Note: The assistant should not reveal chain-of-thought. Output stays concise and structured.

🧠 Prompt Engineering Requirement (Sprint 1)

You will write at least 5 system prompts, selectable via dropdown. These represent different prompting techniques and/or interviewer modes, for example:

Friendly Screening Round (supportive tone, broad fit)

Neutral Technical Round (professional tone, skill depth)

Strict Onsite Round (challenging, high standards)

Clarify-first (asks key questions before generating)

Few-shot (includes example JD/CV → question patterns)

🔐 Security Guard (Sprint 1 requirement)

Before calling the model:

block obvious prompt injection attempts (e.g., “ignore previous instructions”, “reveal system prompt”)

reject illegal/harmful requests

enforce max length on JD/CV/user prompt

show a refusal message in the UI if triggered

✅ Sprint 1 course requirements — satisfied

✅ Single-page web app → Streamlit

✅ OpenAI API call + API key usage

✅ Choose one allowed model (GPT-4.1 / GPT-4.1 mini / GPT-4.1 nano / GPT-4o / GPT-4o mini)

✅ At least 5 system prompts with different techniques

✅ Tune ≥ 1 OpenAI setting → Temperature

✅ Add ≥ 1 security guard → input validation + injection defense

---

🧩 Optional Features (Out of Sprint 1 scope)
- Provide the user with the ability to choose from a list of LLM models
- Deploy the app to the Internet
- Use Streamlit to implement a full-fledged chatbot application instead of a one-time call
- Use LangChain packages to implement the app using chains or agents
