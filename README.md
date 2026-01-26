# 🧩 Sprint 1 — Interview Practice App (Streamlit + OpenAI)

A single-page Streamlit app that generates **5 tailored interview questions (English)** using an OpenAI model, based on an optional **job description**, optional **CV text**, and an optional **user prompt**.

## ✅ What it does (MVP)
- ✅ Generates **exactly 5** interview questions, each with **tags** (e.g. `[Technical]`, `[Behavioral]`, `[Role-specific]`, `[Screening]`, `[Onsite]`, `[Final]`)
- ✅ Uses **5 different system prompt variants** (dropdown) to represent different interviewer modes / rounds
- ✅ If **Job Description is empty**, asks once for the **target role**, then proceeds
- ✅ If **CV is empty**, mentions once that adding it helps tailor questions better
- ✅ Includes a **temperature slider** (tuning requirement)
- ✅ Includes a **security guard** (input validation + basic prompt-injection detection)

Full behavior and output contract: see `REQUIREMENTS.md`.

## 🧰 Tech stack
- Frontend: **Streamlit**
- LLM API: **OpenAI**
- Tests: **pytest**
- Lint/format (later): **ruff**

## 🏃 Run locally
1) Create a virtual environment and install deps
2) Add your OpenAI key
3) Start the app

```bash
# example (adjust to your setup)
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env and set OPENAI_API_KEY=...

streamlit run app/ui/App.py
```

## 🧪 Run tests
```bash
pytest -q
```

## 🚀 Deploy on Streamlit Cloud
This app is designed to deploy from a single entrypoint. Use the multipage root:

- **Entrypoint**: `app/ui/App.py`
  - This launches the chat landing page and exposes the classic + LangChain pages via `app/ui/pages/`.

### Steps
1) Push this repo to GitHub.
2) In Streamlit Cloud, create a new app and point it at this repo.
3) Set the **Main file path** to `app/ui/App.py`.
4) Add the environment variable `OPENAI_API_KEY` in the app settings.
5) Deploy.

### Notes
- Dependencies are declared in `requirements.txt` and include Streamlit + OpenAI + LangChain.
- If you want a **LangChain-only** deployment, keep the entrypoint above and set
  `APP_IMPL=langchain` (default).

### Implementation toggle (dev/review)
- `APP_IMPL` controls which pages are shown: `langchain` (default), `openai`, or `both`.
- Set `ALLOW_IMPL_SWITCH=1` to show a sidebar toggle that lets reviewers switch views.

## 🧭 Repo navigation

REQUIREMENTS.md — MVP spec + acceptance criteria

PLAN.md — step-by-step implementation plan

AGENTS.md — canonical instructions for AI-assisted development

RULES.md — operational rules snapshot

ARCHITECTURE.md — architecture snapshot

PROGRESS_TRACKING.md — decisions + next steps

FAILED-DEV-INSIGHTS.md — post-mortems after failed attempts
