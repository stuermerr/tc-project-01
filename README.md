# Interview Practice App

Streamlit app for interview preparation with:
- chat coaching and mock interview flow
- cover letter generation from JD + CV
- structured interview question generation (exactly 5 questions)
- response export buttons (`Download Response (PDF)`, `Download Full Chat (PDF)`)

## Tech Stack
- Python 3.12+
- Streamlit
- OpenAI + LangChain
- `uv` for dependency and environment management
- `pytest` for tests

## Setup
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

## Run
Use the Streamlit entrypoint with `run`:
```bash
uv run streamlit run app/ui/App.py
```

The app currently serves the LangChain experience with two pages:
- `Interview Preparation Chat`
- `Interview Questions Generator`

## Tests
```bash
uv run pytest -q
```

## Notes
- PDF exports are rendered from markdown using `markdown-pdf`.
- If you see `No such command 'app/ui/App.py'`, the command is missing `run`.
  Use: `uv run streamlit run app/ui/App.py`.
