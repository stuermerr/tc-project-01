# rules.md — How the AI assistant should behave in this repo

## Operating rules
- Implement **only the requested PLAN step**.
- Do not perform large refactors unless explicitly asked.
- Keep diffs small.
- Add/extend tests for each change.
- If uncertain, add `TODO:` and explain assumptions.

## Dependency policy
- Prefer no new dependencies.
- If needed, justify in a short comment and in the PR/commit message.

## Security
- Never log secrets.
- Never commit secrets.
- Add redaction if logging user input.

