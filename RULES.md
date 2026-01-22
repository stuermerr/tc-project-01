# RULES.md — Operational rules for AI-assisted coding (copy/paste)

These rules are **hard constraints** for AI-assisted work in this repo.
If there’s a conflict, follow this file first, then `AGENTS.md`.

---

## 1) Scope & workflow
- Implement **only the next Step N** from `PLAN.md`.
- If anything is underspecified, **ask questions before coding**.
- Prefer the **smallest change** that works.
- No “vibe coding” or speculative features.

---

## 2) File modification rules
- Do **not** modify unrelated files.
- Do **not** refactor for cleanliness unless explicitly asked.
- If you must touch another file, explain:
  - why it’s necessary
  - what changed (briefly)

---

## 3) Dependencies & research
- Prefer minimal dependencies.
- Any new dependency must be justified:
  - what it’s for
  - why it’s needed now
- If library behavior is uncertain, consult **official docs**.

---

## 4) Testing (required)
- Add or update **pytest** tests for each implemented step.
- “Done” means:
  - code runs
  - tests pass (`pytest -q`)
- Prefer tests that assert:
  - input → output contracts
  - safety guard behavior
  - prompt/message structure

---

## 5) Security & privacy
- Never log or print secrets (API keys, `.env`).
- Avoid logging raw user CV/JD text; prefer redacted summaries.
- Add/maintain basic prompt-injection defenses when relevant.
- Validate user input (length limits, obvious abuse patterns).

---

## 6) Coding standards
- Keep modules small and testable.
- Use snake_case (Python).
- Prefer explicit types for public functions.
- Add docstrings for public functions/classes.
- Error handling:
  - fail fast for programmer errors
  - user-friendly messages for runtime errors

---

## 7) Git workflow (AI suggests, user executes)
- AI may suggest git commands; the **user runs them**.
- Make small, reviewable commits.
- No bulk changes without explicit user approval.
- Commit message format must start with:
  - `AI - feat: ...`
  - `AI - fix: ...`
  - `AI - chore: ...`
  - `AI - docs: ...`
  - `AI - test: ...`

---

## 8) Uncertainty handling
- If uncertain: add `TODO:` and state assumptions.
- Never guess hidden requirements.
- Prefer asking one clear question over making a risky assumption.

---

## 9) Failure handling
If an implementation attempt fails and the user wants to stop the chat:
- Document the failure in `FAILED-DEV-INSIGHTS.md`:
  - which `PLAN.md` step failed
  - what was tried
  - what went wrong (errors + symptoms)
  - minimal reproduction steps (if possible)
  - what to try next / what to avoid
