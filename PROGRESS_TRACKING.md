# PROGRESS_TRACKING.md - Decisions, progress, and next steps

## Current milestone
- Step 6 complete: controller orchestration

## Decisions log
| Date | Decision | Rationale | Impact |
|------|----------|-----------|--------|
| 2025-09-09 | Standardized PROGRESS_TRACKING.md usage + aligned docs | Keep project docs consistent and actionable | Clearer onboarding and next steps |
| 2026-01-19 | Implemented Step 1 core models + prompt variants | Establish typed interfaces and prompt set | Unblocked safety guard and prompt builder steps |
| 2026-01-19 | Implemented Step 2 safety guard | Enforce length limits + prompt injection checks | Ready for prompt builder integration |
| 2026-01-19 | Implemented Step 3 prompt builder | System+user message assembly with consistent fields | Ready for OpenAI client wrapper |
| 2026-01-19 | Implemented Step 4 OpenAI client wrapper (default gpt-4o-mini) | Enable model calls with temperature control | Ready for response formatter |
| 2026-01-19 | Implemented Step 5 response formatter | Enforce response contract + question count | Ready for controller orchestration |
| 2026-01-19 | Implemented Step 6 controller orchestration | Wire safety, prompt building, LLM, formatter | Ready for Streamlit UI |

## Open questions
- None currently.

## Usage
- Update after each working session or when scope/decisions change.
- Keep entries concise and dated when practical.

## Next steps
- [x] Implement PLAN Step 1: core models + prompt variants
- [x] Implement PLAN Step 2: safety guard (validation + injection heuristics)
- [x] Implement PLAN Step 3: prompt assembler
- [x] Implement PLAN Step 4: OpenAI client wrapper
- [x] Implement PLAN Step 5: response formatter (contract enforcement)
- [x] Implement PLAN Step 6: controller orchestration
- [ ] Implement PLAN Step 7: Streamlit UI single-page app
