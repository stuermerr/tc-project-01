# RULES.md — Project-specific rules for AI-assisted coding

These rules are **project-specific** and override `AGENTS.md` when applicable.

---

## 1) Environment & tooling
- Tests: `conda run -n tc pytest -q`
- Lint/format: `ruff`

---

## 2) Testing (required)
- Add or update **pytest** tests for each implemented step.

---

## 3) Coding standards
- Use snake_case (Python).

---

## 4) Security & privacy
- Avoid logging raw user CV/JD text; prefer redacted summaries.
