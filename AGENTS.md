# AGENTS.md — Canonical instructions for AI-assisted development

This file defines the **contract** for how AI assistants should behave in this repository.

---

## 0) Quick start (read this first)

1) Read these files (in this order):
   - `REQUIREMENTS.md` (what we’re building + acceptance criteria)
   - `RULES.md` (project-specific rules)
   - `ARCHITECTURE.md` (snapshot of high-level overview of architecture (modules, data flow, etc)
   - `PLAN.md` (the next small step to implement)
   - `FAILED-DEV-INSIGHTS.md` (avoid repeating past failures)
   - `PROGRESS_TRACKING.md` (recent decisions + current state)
2) Implement **only one PLAN step per session**.
3) If anything is underspecified, ask questions **before** coding.
4) Prefer the smallest change that works, with tests.
5) If all PLAN steps are complete and the user explicitly requests a new implementation, add a new step to `PLAN.md` and proceed to implement that step in the same session without additional approval.
6) If all PLAN steps are complete and there is no explicit new implementation request, stop and ask the user to update `PLAN.md`/`REQUIREMENTS.md` before coding, and prompt with next-step ideas (extensions, refactors, cleanup, logging, comments, etc.).

---

## 1) Source-of-truth docs (what each file is for)
- **[Generic]** `AGENTS.md` — how the AI assistant must operate (this file)
- **[Generic]** `RULES.md` — short operational rules (short version for copy paste)
- **[Generic]** `REQUIREMENTS.md` — product scope + constraints + definition of done
- **[Generic]** `PLAN.md` — numbered implementation steps (small, testable, sequential)
- **[Generic]** `ARCHITECTURE.md` — stable architecture snapshot (modules, data flow, etc)
- **[Generic]** `PROGRESS_TRACKING.md` — Track current done milestone, decisions, open questions, and next steps
- **[Generic]** `FAILED-DEV-INSIGHTS.md` — post-mortems for failed attempts (used to avoid repeating mistakes)
- **[Project-specific]** `OG_SCHOOL_PROJECT_REQUIREMENTS.md` — user notes (reference only, not a source-of-truth)

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
- When implementing or editing code, add brief beginner-friendly comments for each meaningful block explaining what it does and why.

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

**Commands**
- Keep project-specific commands in `RULES.md` or `README.md`.

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

**Allowed git commands**
- `git status`, `git diff`, `git log`, `git show` (local inspection)
- `git add`, `git restore`, `git reset` (staging and local undo)
- `git branch` (local branch management)
- `git switch`, `git checkout` (switch branches)
- `git commit` (local commits on feature branches)

**Prompt before**
- `git switch main` or `git checkout main` (confirm before moving to main)
- `git merge` (merge only after tests pass)

**Forbidden**
- `git push`, `git pull`, `git fetch`, `git clone` (no remote git operations)
- `git remote` (do not modify remotes)
- `git rebase` (avoid history rewriting)

**Git identity**
- Set `git config user.name "Stuermer"` and `git config user.email "philipp.sturmer@gmail.com"` before committing.

---

## 6) Coding standards (defaults)
- Keep modules small and testable.
- Prefer explicit types for public functions.
- Add docstrings for public functions/classes.
- Error handling:
  - fail fast for programmer errors (bad internal state)
  - user-facing messages for runtime errors (bad input, network, API issues)
- Logging:
  - never log secrets

---

## 7) Testing strategy
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
