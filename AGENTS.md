# AGENTS.md — Canonical instructions for AI-assisted development

This file defines the **contract** for how AI assistants should behave in this repository.

---

## 0) Quick start (read this first)

1) Read these files (in this order):
   - `REQUIREMENTS.md` (what we’re building + acceptance criteria)
   - `RULES.md` (hard do/don’t rules)
   - `ARCHITECTURE.md` (snapshot of high-level overview of architecture (modules, data flow, etc)
   - `PLAN.md` (the next small step to implement)
   - `PROGRESS_TRACKING.md` (recent decisions + current state)
2) Implement **only one PLAN step per session**.
3) If anything is underspecified, ask questions **before** coding.
4) Prefer the smallest change that works, with tests.

---

## 1) Source-of-truth docs (what each file is for)
- `AGENTS.md` — how the AI assistant must operate (this file)
- `RULES.md` — short operational rules (short version for copy paste)
- `REQUIREMENTS.md` — product scope + constraints + definition of done
- `PLAN.md` — numbered implementation steps (small, testable, sequential)
- `ARCHITECTURE.md` — stable architecture snapshot (modules, data flow, etc)
- `PROGRESS_TRACKING.md` — Track current done milestone, decisions, open questions, and next steps
- `FAILED-DEV-INSIGHTS.md` — post-mortems for failed attempts (used to avoid repeating mistakes)
- `OG_SCHOOL_PROJECT_REQUIREMENTS.md` — user notes (reference only, not a source-of-truth)

**Update policy**
- If scope/behavior changes → update `REQUIREMENTS.md`.
- If implementation approach changes → update `PLAN.md`.
- If module boundaries/data flow changes → update `ARCHITECTURE.md`.
- If a coding attempt fails → update `FAILED-DEV-INSIGHTS.md`.
- If AI workflow rules evolve → update `AGENTS.md` (and keep `RULES.md` in sync).
- After each working session and completion of a PLAN step or when scope/decisions change → update `PROGRESS_TRACKING.md` (Keep entries short, dated when applicable, and focused on what changed)


---

## 2) Roles & responsibilities
**User (human)**
- Owns architecture choices, scope decisions, and quality bar.
- Runs tests locally and decides what gets committed.

**AI assistant**
- Proposes options, explains trade-offs, implements small steps with tests.
- Never assumes requirements that aren’t written.
- Never performs large refactors unless explicitly requested.

---

## 3) Session protocol (how we work)
### 3.1 Planning sessions (reasoning model)
**Goal**
- Refine scope and acceptance criteria in `REQUIREMENTS.md`.
- Produce/adjust a stepwise implementation plan in `PLAN.md`.

**Output**
- Clear numbered steps with:
  - inputs/outputs
  - success criteria
  - minimal tests per step
  - explicit interfaces (function signatures / data models)

### 3.2 Implementation sessions (coding model)
**Rules**
- Implement **only next Step N** from `PLAN.md`.
- Do not modify unrelated files.
- Do not refactor for “cleanliness” unless asked.
- Add/adjust tests for Step N.
- If uncertain, write `TODO:` + state assumptions.

**Done means**
- Code runs.
- Tests pass.
- Changes are minimal and readable.

### 3.3 Debugging sessions
Provide:
- failing test output
- stack trace
- relevant files/snippets

AI Assistant must:
- explain root cause briefly
- propose the **smallest possible fix**
- avoid unrelated refactors

### 3.4 Observability sessions
- Add structured logging + redaction.
- Instrument key boundaries (pipelines, tool invocations).
- Log errors/timeouts/retries without leaking secrets or sensitive user text.

---

## 4) Environment & tooling
**Secrets**
- Never commit `.env` or API keys.

**Commands (default)**
- Tests: `pytest -q`
- Lint/format: `ruff`

If the project uses different tools/versions, document them in:
- `REQUIREMENTS.md` (constraints)
- or `README.md` (how to run)

---

## 5) Git workflow (AI suggests, user executes)
- Make small, reviewable commits.
- Prefer many small commits over one large commit.
- Commit message format:
  - `AI - feat: ...`
  - `AI - fix: ...`
  - `AI - chore: ...`
  - `AI - docs: ...`
  - `AI - test: ...`

**Important**
- The AI assistant may suggest git commands, but the **user runs them**.
- No bulk changes without explicit user approval.

---

## 6) Coding standards (defaults)
- Keep modules small and testable.
- Prefer explicit types for public functions.
- Add docstrings for public functions/classes.
- Use consistent naming (snake_case in Python).
- Error handling:
  - fail fast for programmer errors (bad internal state)
  - user-facing messages for runtime errors (bad input, network, API issues)
- Logging:
  - never log secrets
  - avoid logging raw user CV/JD text; prefer redacted summaries

---

## 7) Testing strategy
- Use `pytest`.
- Add unit tests as each component is introduced.
- Prefer tests that assert:
  - input → output contracts
  - safety guard behavior
  - prompt/message structure (roles, ordering, required fields)

---

## 8) Research & dependencies
- If library behavior is uncertain, consult official docs.
- Prefer minimal dependencies.
- Any new dependency must be justified:
  - what it’s for
  - why it’s needed now (not “maybe later”)

---

## 9) Failure-handling strategy (important)
If a feature implementation attempt fails and the user wants to stop the current chat:

Update `FAILED-DEV-INSIGHTS.md` with:
- Which `PLAN.md` step/feature failed
- What approach was tried
- What went wrong (error messages + symptoms)
- Minimal reproduction steps (if possible)
- What to try next / what to avoid next time
