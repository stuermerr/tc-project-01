# 📌 PROGRESS_TRACKING.md - Decisions, progress, and next steps

## ✅ Current milestone
- Step 54 complete: CV length requirement aligned to 4000

## 🧭 Decisions log
| Date | Decision | Rationale | Impact |
|------|----------|-----------|--------|
| 2025-09-09 | Standardized PROGRESS_TRACKING.md usage + aligned docs | Keep project docs consistent and actionable | Clearer onboarding and next steps |
| 2026-01-19 | Implemented Step 1 core models + prompt variants | Establish typed interfaces and prompt set | Unblocked safety guard and prompt builder steps |
| 2026-01-19 | Implemented Step 2 safety guard | Enforce length limits + prompt injection checks | Ready for prompt builder integration |
| 2026-01-19 | Implemented Step 3 prompt builder | System+user message assembly with consistent fields | Ready for OpenAI client wrapper |
| 2026-01-19 | Implemented Step 4 OpenAI client wrapper (default gpt-4o-mini) | Enable model calls with temperature control | Ready for response formatter |
| 2026-01-19 | Implemented Step 5 response formatter | Enforce response contract + question count | Ready for controller orchestration |
| 2026-01-19 | Implemented Step 6 controller orchestration | Wire safety, prompt building, LLM, formatter | Ready for Streamlit UI |
| 2026-01-19 | Implemented Step 7 Streamlit UI | Single-page inputs + generate flow | Ready for integration tests |
| 2026-01-19 | Implemented Step 8 integration test + README update | End-to-end coverage and run instructions | Sprint 1 MVP complete |
| 2026-01-19 | Added inline code comments + repo guide | Improve readability and onboarding | Easier navigation and understanding |
| 2026-01-22 | Implemented Step 9 beginner-friendly comments pass | Clarify intent of code blocks for new readers | Improved onboarding readability |
| 2026-01-23 | Planned Steps 10-16: Multi-layer safety hardening | Research-based defense-in-depth approach combining heuristics, ML detection, architectural separation, output validation, logging, and rate limiting | Comprehensive safety roadmap defined for post-Sprint 1 implementation |
| 2026-01-23 | Implemented Step 10 input safety hardening | Add extra injection patterns and control-character validation | Stronger input guardrails with minimal false positives |
| 2026-01-23 | Implemented Step 11 ML-based injection detection hook | Optional pytector check with fail-open behavior | Added ML layer without hard dependency |
| 2026-01-23 | Implemented Step 12 system prompt role separation rules | Added explicit instruction boundaries to prompt variants | Reduced prompt-injection leverage in system prompts |
| 2026-01-23 | Implemented Step 13 salted tag separation | Added per-request salted tags and system header | Stronger prompt injection resistance |
| 2026-01-23 | Implemented Step 14 output validation and sanitization | Added output checks and redaction logic | Blocks leaked internal tags or prompts |
| 2026-01-23 | Implemented Step 15 safety logging and metrics | Added privacy-aware event logging and counters | Visibility into blocked/sanitized events |
| 2026-01-23 | Implemented Step 16 basic rate limiting | Added per-session request throttling | Prevents rapid-fire usage spikes |
| 2026-01-23 | Implemented Step 17 dotenv loading in OpenAI client | Load local .env for API key without UI coupling | Streamlit picks up OPENAI_API_KEY from .env |
| 2026-01-23 | Implemented Step 18 remove pytector ML safety check | Avoid torch/pytector dependency issues | Safety relies on heuristic checks only |
| 2026-01-23 | Implemented Step 19 privacy-aware logging | Add request lifecycle logs without leaking user content | Observability across UI, controller, formatter, and client |
| 2026-01-23 | Implemented Step 20 standard logging configuration | Ensure console logs appear in terminal with INFO default | Visibility without debug mode |
| 2026-01-23 | Implemented Step 21 job description limit update | Allow larger JD input up to 6000 chars | Users can paste longer JDs |
| 2026-01-23 | Implemented Step 22 structured output JSON | Replace hardcoded formatter with JSON schema output + parser | Structured outputs enforced by prompts and schema |
| 2026-01-23 | Implemented Step 23 markdown rendering | Display structured JSON as user-friendly markdown | Improved UI readability |
| 2026-01-23 | Consolidated optional additions plan | Merged optional follow-ups into a single ordered set of steps (24-30) | One cohesive optional roadmap tied to current app |
| 2026-01-23 | Adjusted chat steps to align with Streamlit Session State | Updated optional steps 26-28 to use built-in session state and chat components | Avoided redundant custom memory/persistence |
| 2026-01-23 | Implemented Step 24 model catalog + payload support | Added model catalog, payload support, and OpenAI model override wiring | Ready for UI layout refresh |
| 2026-01-23 | Implemented Step 25 classic UI layout refresh + Enter-to-submit | Reordered inputs, added model/settings row, and centered submit button | Ready for chat history helpers |
| 2026-01-23 | Implemented Step 26 chat history state helpers | Added session-state chat message helpers with trimming | Ready for chat UI work |
| 2026-01-23 | Implemented Step 27 Streamlit chat UI (MVP) | Added chat UI entrypoint with session history and structured responses | Ready for multi-page navigation |
| 2026-01-26 | Refined Step 28 multi-page navigation | Switched to Streamlit pages directory with chat as landing page and classic as secondary page | Ready for LangChain app core |
| 2026-01-26 | Cleaned UI multipage layout | Moved chat UI logic into shared module and removed legacy entrypoint | UI directory aligned with pages structure |
| 2026-01-26 | Aligned page labels and layouts | Renamed pages for navigation labels and matched chat layout to classic inputs | Multipage navigation matches desired naming |
| 2026-01-26 | Approved free-form chat behavior with structured classic UI | Allow chat to be flexible while keeping classic JSON contract | Requires new chat prompt variants and split orchestration |
| 2026-01-26 | Implemented Step 29 chat prompt variants | Added chat-only prompts with flexible initial guidance and free-form follow-ups | Unblocked chat orchestration split |
| 2026-01-26 | Implemented Step 30 chat orchestration split | Added free-form chat generation path and kept classic structured parsing | Ready to update chat UI rendering |
| 2026-01-26 | Implemented Step 31 chat UI rendering | Wired chat UI to free-form prompts and responses | Ready for chat behavior tests |
| 2026-01-26 | Implemented Step 32 chat behavior tests | Added free-form chat client test ensuring no JSON schema enforcement | Chat testing coverage aligned with new flow |
| 2026-01-26 | Implemented Step 33 chat prompt length increase | Added chat-specific validation to allow longer history prompts | Prevents premature length refusals |
| 2026-01-26 | Implemented Step 34 JD/CV session persistence | Shared Streamlit session state across chat/classic | Stops inputs from resetting mid-session |
| 2026-01-26 | Implemented Step 35 chat prompt formatting | Encouraged bullet-first responses and light emoji section labels | Chat responses are more scannable |
| 2026-01-26 | Implemented Step 36 JD/CV persistence fix | Moved classic JD/CV outside form to persist on navigation | Shared inputs stay in sync |
| 2026-01-26 | Reverted JD/CV persistence attempts | Streamlit multipage widgets do not persist natively across pages | Kept default widget behavior |
| 2026-01-26 | Planned chat initial-response gating + model-specific settings | Ensure structured intro appears once and GPT-5 uses reasoning effort | New steps added before LangChain work |
| 2026-01-26 | Implemented Step 36 chat initial-response gating | Added transcript-based rule so initial structure applies only once | Follow-ups stay free-form |
| 2026-01-26 | Implemented Step 37 model-specific settings | Added reasoning effort for GPT-5 and omitted temperature | Model switches avoid temperature errors |
| 2026-01-26 | Implemented Step 38 documentation pass | Added module and public API docstrings across Python files | Clearer reviewer-facing documentation |
| 2026-01-26 | Split LangChain plan into smaller steps | Improve granularity for wrapper, structured output, and UI entrypoint | Clearer sequencing before deployment prep |
| 2026-01-26 | Implemented Step 39 LangChain core wrapper | Added LangChain client wrapper with prompt wiring and validation | Ready for structured output integration |
| 2026-01-26 | Implemented Step 40 LangChain structured output integration | Parsed structured JSON from LangChain responses using existing contract checks | Ready for LangChain UI entrypoint |
| 2026-01-26 | Implemented Step 41 LangChain Streamlit entrypoint | Added LangChain UI page and import smoke test | Ready for deployment prep |
| 2026-01-26 | Implemented Step 42 Streamlit deployment prep | Added requirements.txt and deployment runbook in README | Deployment instructions ready |
| 2026-01-26 | Implemented Step 43 LangChain import cleanup | Removed deprecated langchain.schema fallback import | IDE import errors resolved |
| 2026-01-26 | Implemented Step 44 LangChain chat wrapper | Added free-form LangChain chat response path with chat validation | Ready for LangChain chat UI |
| 2026-01-26 | Implemented Step 45 LangChain chat UI entrypoint | Added shared chat UI helper and LangChain chat page | Ready for chat behavior tests |
| 2026-01-26 | Implemented Step 46 LangChain chat behavior tests | Added test ensuring LangChain chat skips structured parsing | Chat coverage complete |
| 2026-01-26 | Implemented Step 47 LangChain-only navigation entrypoint | Added Streamlit navigation entrypoint for LangChain pages only | Allows LangChain-only view |
| 2026-01-26 | Implemented Step 48 implementation toggle | Added APP_IMPL and optional UI switch to filter navigation pages | Dev/reviewer toggles enabled |
| 2026-01-26 | Implemented Step 49 README cleanup | Rewrote README with concise bullet sections and updated commands | Cleaner onboarding and accurate run/test/deploy info |
| 2026-01-26 | Implemented Step 50 OG checklist sync | Updated OG requirements checklist with implemented items | Status reflects current app features |
| 2026-01-26 | Implemented Step 51 README + dependency alignment | Updated README, added .env.example, aligned requirements | Setup docs match env manifests |
| 2026-01-26 | Implemented Step 52 deployment guide | Removed README deploy section and added private Streamlit guide | Deployment steps are kept local |
| 2026-01-26 | Implemented Step 53 illegal/harmful request blocking | Added conservative safety checks for obvious harmful intent | Meets safety requirement without overblocking |
| 2026-01-26 | Implemented Step 56 OpenAI moderation guardrail | Added moderation endpoint check with fail-open behavior | Standardized illegal/harmful filtering |
| 2026-01-26 | Implemented Step 54 CV max length alignment | Updated requirements to 4000 chars to match current validation | Requirement and code are consistent |

## ❓ Open questions
- None currently.

## 📝 Usage
- Update after each working session or when scope/decisions change.
- Keep entries concise and dated when practical.

## 🧩 Next steps
- [x] Implement PLAN Step 1: core models + prompt variants
- [x] Implement PLAN Step 2: safety guard (validation + injection heuristics)
- [x] Implement PLAN Step 3: prompt assembler
- [x] Implement PLAN Step 4: OpenAI client wrapper
- [x] Implement PLAN Step 5: response formatter (contract enforcement)
- [x] Implement PLAN Step 6: controller orchestration
- [x] Implement PLAN Step 7: Streamlit UI single-page app
- [x] Implement PLAN Step 8: Integration tests + docs
- [x] Implement PLAN Step 9: Beginner-friendly comments pass
- [x] Implement PLAN Step 10: Strengthen input safety heuristics (extended patterns + character validation)
- [x] Implement PLAN Step 11: Integrate ML-based prompt injection detection (pytector)
- [x] Implement PLAN Step 12: Strengthen system prompts with explicit role separation instructions
- [x] Implement PLAN Step 13: Implement salted XML tag architectural separation
- [x] Implement PLAN Step 14: Add output validation and sanitization
- [x] Implement PLAN Step 15: Logging and metrics for safety events
- [x] Implement PLAN Step 16: Basic in-process rate limiting for safety
- [x] Implement PLAN Step 17: Load local .env with python-dotenv in OpenAI client
- [x] Implement PLAN Step 18: Remove ML-based prompt injection detection (pytector)
- [x] Implement PLAN Step 19: Add privacy-aware logging across the core workflow
- [x] Implement PLAN Step 20: Standardize console logging configuration
- [x] Implement PLAN Step 21: Increase job description max length
- [x] Implement PLAN Step 22: Structured output (replace hardcoded formatter)
- [x] Implement PLAN Step 23: Render structured output as markdown
- [x] Implement PLAN Step 24: Model catalog + payload support
- [x] Implement PLAN Step 25: Classic UI layout refresh + Enter-to-submit
- [x] Implement PLAN Step 26: Chat history serialization helpers
- [x] Implement PLAN Step 27: Streamlit chat UI (MVP)
- [x] Implement PLAN Step 28: Multi-page navigation (classic + chat)
- [x] Implement PLAN Step 29: Chat prompt variants (free-form)
- [x] Implement PLAN Step 30: Chat orchestration split (structured vs free-form)
- [x] Implement PLAN Step 31: Chat UI rendering (free-form)
- [x] Implement PLAN Step 32: Chat behavior tests
- [x] Implement PLAN Step 33: Chat user prompt length increase
- [x] Implement PLAN Step 35: Chat prompt formatting (bullets + emojis)
- [x] Implement PLAN Step 36: Initial response guidance only once (chat)
- [x] Implement PLAN Step 37: Model-specific settings (reasoning effort for GPT-5)
- [x] Implement PLAN Step 38: Documentation pass (module + public API docstrings)
- [x] Implement PLAN Step 39: LangChain core wrapper + prompt wiring
- [x] Implement PLAN Step 40: LangChain structured output integration
- [x] Implement PLAN Step 41: LangChain Streamlit entrypoint
- [x] Implement PLAN Step 42: Streamlit deployment prep + runbook
- [x] Implement PLAN Step 43: LangChain import cleanup (remove deprecated schema fallback)
- [x] Implement PLAN Step 44: LangChain chat wrapper (free-form path)
- [x] Implement PLAN Step 45: LangChain chat UI entrypoint (separate page)
- [x] Implement PLAN Step 46: LangChain chat behavior tests
- [x] Implement PLAN Step 47: LangChain-only navigation entrypoint
- [x] Implement PLAN Step 48: Implementation toggle for navigation
- [x] Implement PLAN Step 49: README cleanup (concise bullet format)
- [x] Implement PLAN Step 50: OG checklist sync
- [x] Implement PLAN Step 51: README + dependency alignment
- [x] Implement PLAN Step 52: Deployment guide (private)
- [x] Implement PLAN Step 53: Block illegal/harmful requests (safety guard)
- [x] Implement PLAN Step 54: Align CV length limit with requirements
- [ ] Implement PLAN Step 55: Tighten structured output validation (LangChain + OpenAI)
- [x] Implement PLAN Step 56: Add OpenAI moderation guardrail
