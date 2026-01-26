# 🧩 Interview Practice App (Streamlit + OpenAI + LangChain)

## ✅ Overview
- 🎯 Classic mode generates exactly 5 tagged interview questions (English).
- 💬 Chat mode supports coaching, feedback, and follow-ups.
- 🧾 Classic output uses structured JSON rendered as markdown.
- 🛡️ Safety guard blocks obvious prompt injection and enforces length limits.
- 🎚️ Model settings: temperature for `gpt-4o-mini`, reasoning effort for GPT-5.

## 🧰 Tech stack
- 🖥️ Streamlit
- 🤖 OpenAI API + LangChain
- 🧪 pytest
- 🧹 ruff

## ▶️ Run locally
- 🧪 Create and activate a virtual environment.
- 📦 Install dependencies.
- 🔐 Create `.env` with `OPENAI_API_KEY=...` (local only).
- 🚀 Start the multipage app.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
printf "OPENAI_API_KEY=...\n" > .env
streamlit run app/ui/App.py
```

## 🧪 Run tests
- ✅ Default project command (conda):
```bash
conda run -n tc pytest -q
```
- ✅ Standard command (venv):
```bash
pytest -q
```

## 🚀 Deploy (Streamlit Cloud)
- 📌 Entrypoint: `app/ui/App.py`
- 🔧 Set `OPENAI_API_KEY` in Streamlit Cloud secrets.
- 🧭 Pages live in `app/ui/pages/`.
- 🧪 Dependencies are in `requirements.txt`.

## 🔀 Implementation toggle
- 🧪 `APP_IMPL=langchain` (default), `openai`, or `both`.
- 🧭 Set `ALLOW_IMPL_SWITCH=1` to show a sidebar toggle.

## 🧭 Repo map
- 🧩 `REQUIREMENTS.md` — product scope + acceptance criteria
- 🗺️ `ARCHITECTURE.md` — architecture snapshot
- 🧱 `PLAN.md` — implementation steps
- 📌 `PROGRESS_TRACKING.md` — decisions + current state
- 🧰 `RULES.md` — tooling + testing rules
- 🤖 `AGENTS.md` — AI workflow contract
- 🧯 `FAILED-DEV-INSIGHTS.md` — post-mortems
- 🧭 `REPO_GUIDE.md` — module map and flow
