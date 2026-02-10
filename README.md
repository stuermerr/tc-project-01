# 🧩 Interview Practice App

## ✅ Overview
Streamlit app for interview preparation with:
- 💬 Chat coaching and mock interview flow
- 📝 Cover letter generation from JD + CV
- ❓ Structured interview question generation (exactly 5 questions)
- 📄 Response export buttons (`Download Response (PDF)`, `Download Full Chat (PDF)`)

## 🌐 Live app
- https://tc-project-01git-ydv65ajrftafgtfn8yqe9z.streamlit.app/ (ask for access)

## 🧰 Tech Stack
- 🐍 Python 3.12+
- 🖥️ Streamlit
- 🤖 OpenAI + LangChain
- ⚡ `uv` for dependency and environment management
- 🧪 `pytest` for tests

## ⚙️ Setup
1. Install `uv` (system-wide), then in this repo run:
```bash
uv sync
```
2. Configure environment variables:
```bash
cp .env.example .env
```
3. Add your API key in `.env`:
```bash
OPENAI_API_KEY=...
```

## ▶️ Run
Use the Streamlit entrypoint with `run`:
```bash
uv run streamlit run app/ui/App.py
```

The app currently serves the LangChain experience with two pages:
- 💬 `Interview Preparation Chat`
- ❓ `Interview Questions Generator`

## 🧪 Tests
```bash
uv run pytest -q
```
