# 🧩 Interview Practice App (Streamlit + OpenAI + LangChain)

## ✅ Overview
- 🎯 Generates exactly 5 interview questions from JD + CV.
- 🧭 Tailors questions with optional user prompt (focus areas).
- 💬 Chat mode supports coaching, feedback, and follow-ups.
- 🧾 Question generator output uses structured JSON rendered as markdown.
- 🛡️ Safety guard blocks obvious prompt injection, illegal/harmful requests (via OpenAI moderation), and enforces length limits.
- 🎚️ Model settings: temperature for `gpt-4o-mini`, reasoning effort for GPT-5.

## 🧰 Tech stack
- 🖥️ Streamlit
- 🤖 OpenAI API + LangChain
- 🧪 pytest

## ⬇️ Clone
```bash
git clone https://github.com/TuringCollegeSubmissions/psturm-AE.1.5.git
cd psturm-AE.1.5
```

## 🔐 Environment
- 🧾 Copy the example file and set your key.
```bash
cp .env.example .env
```
- 🔑 Set `OPENAI_API_KEY=...` inside `.env` for local runs.
- 🔀 Toggle pages via `.env`: set `APP_IMPL=langchain|openai|both` and/or `ALLOW_IMPL_SWITCH=1`.
- 🔀 Toggle pages via CLI: `APP_IMPL=both ALLOW_IMPL_SWITCH=1 streamlit run app/ui/App.py`.

## ▶️ Install + run (Option A: Conda)
```bash
conda env create -f environment.yml
conda activate tc
streamlit run app/ui/App.py
```

## ▶️ Install + run (Option B: venv)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/ui/App.py
```

## 🧪 Tests
- ✅ Conda:
```bash
conda run -n tc pytest -q
```
- ✅ venv:
```bash
pytest -q
```
