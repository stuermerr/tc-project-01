# AGENTS.md — Canonical instructions for AI-assisted development

This file is the **single source of truth** for how AI assistants should help in this repo.

---

## 1) Project purpose
See `REQUIREMENTS.md` for the stable reference of the project description.

## 2) Rules snapshot
See `RULES.md` for the stable reference of rules to comply.

## 3) Architecture snapshot
See `ARCHITECTURE.md` for the stable reference.


## 4) Repo map
- `AGENTS.md` — canonical assistant instructions (this file)
- `rules.md` — operational rules for coding sessions
- `requirements.md` — scope + definition of project
- `PLAN.md` — stepwise implementation plan
- `progress_tracking.md` — decisions + steps already done successfully + next steps + open questions
- `feature-dev-failed-insights.md` — post-mortem feature development insights to after failed attempts to prevent trying the same implementation approach again and learn from failed approaches.




## 5) Environment & tools
Assumptions (update as needed):
- Python: 3.11+
- Tests: `pytest`

Suggested (optional) tooling once Sprint 1 is stable:
- Lint/format: `ruff`

Runbook (filled once Step 1 is implemented):
- Run app: `streamlit run app/ui/streamlit_app.py`
- Run tests: `pytest -q`

Secrets:
- Never commit `.env`
- Use `.env.example` as documentation

---

## 6) Git workflow
- Commit frequently: small, reviewable commits.
- Message format:
  - `feat: ...`, `fix: ...`, `chore: ...`, `docs: ...`, `test: ...`
- If an AI assistant produced most of a change, append: ` [AI-assisted]`

Important:
- The AI assistant may **suggest** git commands, but **you execute them**.
- Do not allow automated bulk changes without review.

---

## 7) Coding standards
- Keep modules small and testable.
- Prefer explicit types for public functions.
- Add docstrings for public functions.
- Error handling:
  - fail fast for programmer errors
  - graceful user-facing messages for runtime errors
- Logging:
  - avoid logging secrets and personal data
  - redact user input where appropriate

---

## 8) Testing strategy
- Use `pytest`.
- Each component should have unit tests as it is added.
- Prefer tests that assert:
  - input → output contracts
  - safety guard behavior
  - prompt builder message structure

---

## 9) Research rules
- If a library behavior is uncertain, consult **official docs**.
- Prefer minimal dependencies; justify each new dependency.

---

## 10) AI-assisted workflow protocol
### Planning sessions (reasoning model)
- Goal: refine scope and write/update `PLAN.md` and `requirements.md`.
- Output: clear numbered steps, explicit interfaces, test strategy.

### Implementation sessions (coding model)
- Implement **one PLAN step only**.
- Do not refactor unrelated modules.
- Add tests for the step.
- If uncertain: add `TODO:` and state assumptions.

### Debugging sessions
- Provide failing test + stack trace + relevant code.
- Ask for the **smallest possible fix**.

### Observability sessions (later)
- Add structured logging and redaction.
- Instrument pipelines and tool invocations.

---

## 11) Context handoff template (for new chats)
Paste only:
- Relevant excerpt of `AGENTS.md`
- The exact PLAN step you want implemented
- The few code files involved in that step
- Any failing test output

---

## 12) Failure-handling strategy (important)
If a feature attempt fails:
1) Do **not** keep iterating in the same chat.
2) Document the failure in `feature-dev-failed-insights.md`.
3) Start a new session and re-implement using the insights.

---

## 13) Codex/Agent-mode usage (practical)
- Use **chat mode** for planning and writing docs (`PLAN.md`, `requirements.md`).
- Use **agent mode** only for small, mechanical tasks (e.g., implement Step N exactly).
- If the assistant starts asking many follow-ups that do not change the outcome, ask it to **consolidate into docs**.
- Always review diffs and run tests before committing.


Non-goals for this project:
- RAG
- tools/function calling
- AI agents
- long-term memory
- deployment