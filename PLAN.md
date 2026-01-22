# PLAN.md - Implementation plan

> Each step should be independently implementable and testable.

## Goals (Sprint 1)
- Single-page Streamlit app that generates exactly 5 interview questions per run.
- Inputs: JD, CV, user prompt (all optional), prompt variant selector (1-5), temperature slider.
- Output follows the response contract in `REQUIREMENTS.md` (sections + tags).
- Uses an allowed OpenAI model with API key handling.
- Includes basic security guard (prompt injection heuristics, length limits, refusal messaging).

## Non-goals (Sprint 1)
- RAG or vector databases.
- Tool calling / agent workflows.
- Long-term memory or user accounts.
- Deployment or hosting.
- Multi-model selection UI.
- Full chatbot experience (multi-turn chat UI).
- LangChain-based implementation.

## Steps (Sprint 1)
### Step 1 - Define core data models + prompt variants
- Inputs: `REQUIREMENTS.md` response contract and prompt-variant list
- Outputs: `app/core/models.py` (request/response structs) + `app/core/prompts.py` (5+ system prompts)
- Interfaces:
  - `RequestPayload(job_description: str, cv_text: str, user_prompt: str, prompt_variant_id: int, temperature: float)`
  - `PromptVariant(id: int, name: str, system_prompt: str)`
  - `get_prompt_variants() -> list[PromptVariant]`
- Success criteria:
  - At least 5 distinct prompt variants are defined and selectable
  - Models are typed and documented
- Minimal tests:
  - `get_prompt_variants()` returns >= 5 unique IDs
  - Each variant has non-empty `system_prompt`

### Step 2 - Implement safety guard (validation + injection heuristics)
- Inputs: raw user inputs (JD, CV, user prompt)
- Outputs: `app/core/safety.py` with validation result and refusal message
- Interfaces:
  - `validate_inputs(job_description: str, cv_text: str, user_prompt: str) -> tuple[bool, str | None]`
- Success criteria:
  - Blocks obvious injection patterns
  - Enforces max length per field
  - Returns refusal message for UI display
- Minimal tests:
  - Injection phrase triggers refusal
  - Oversized input triggers refusal
  - Clean input passes

### Step 3 - Build prompt assembler
- Inputs: request payload + selected prompt variant
- Outputs: `app/core/prompt_builder.py` returning message list for OpenAI
- Interfaces:
  - `build_messages(payload: RequestPayload, variant: PromptVariant) -> list[dict[str, str]]`
- Success criteria:
  - Includes system prompt + user content
  - User content includes JD/CV/user prompt (when provided)
- Minimal tests:
  - Correct role ordering (`system`, then `user`)
  - Missing fields are represented consistently (empty or omitted)

### Step 4 - OpenAI client wrapper
- Inputs: messages, model name, temperature
- Outputs: `app/core/llm/openai_client.py` with thin call wrapper
- Interfaces:
  - `generate_completion(messages: list[dict[str, str]], temperature: float) -> str`
- Success criteria:
  - Uses allowed model
  - Exposes temperature setting
- Minimal tests:
  - Client builds correct request payload (mocked)

### Step 5 - Response formatter (contract enforcement)
- Inputs: raw model text + original request payload
- Outputs: `app/core/response_formatter.py` with structured output builder
- Interfaces:
  - `format_response(raw_text: str, payload: RequestPayload) -> str`
- Success criteria:
  - Output contains all required sections
  - Exactly 5 tagged questions are present
- Minimal tests:
  - Output includes required headings
  - Exactly 5 questions detected

### Step 6 - Controller orchestration
- Inputs: request payload
- Outputs: `app/core/controller.py` orchestrating safety -> prompt -> client -> format
- Interfaces:
  - `generate_questions(payload: RequestPayload) -> tuple[bool, str]` (success flag + response or refusal)
- Success criteria:
  - Returns refusal when safety fails
  - Returns formatted response when successful
- Minimal tests:
  - Safety failure short-circuits call
  - Success path calls formatter

### Step 7 - Streamlit UI single-page app
- Inputs: user inputs via UI
- Outputs: `app/ui/streamlit_app.py`
- Interfaces:
  - UI wiring to `generate_questions`
- Success criteria:
  - All inputs + controls present
  - Metadata displayed (variant + temperature)
- Minimal tests:
  - Smoke test for UI module import

### Step 8 - Integration tests + docs
- Inputs: end-to-end flow from controller with mocked OpenAI
- Outputs: `tests/` coverage for main workflow; update README if needed
- Success criteria:
  - End-to-end test validates contract sections and 5 questions
- Minimal tests:
  - Controller + formatter output contains required sections and 5 questions

## Optional follow-up steps (only when finished the MVP)
### Step O1 - Multi-model selection
- Inputs: list of allowed models
- Outputs: UI selector + OpenAI client update to pass selected model
- Success criteria:
  - User can choose model from list
- Minimal tests:
  - Selected model is passed to client (mocked)

### Step O2 - Deployment
- Inputs: chosen hosting target
- Outputs: deployment configuration + runbook
- Success criteria:
  - App is reachable on the public Internet
- Minimal tests:
  - Manual smoke test in hosted environment

### Step O3 - Chatbot UX
- Inputs: chat history + user messages
- Outputs: Streamlit chat UI with multi-turn memory in-session
- Success criteria:
  - User can have multi-turn conversation without losing context
- Minimal tests:
  - Chat history preserved across turns in session

### Step O4 - LangChain implementation
- Inputs: existing controller/prompt flow
- Outputs: replacement using LangChain chains/agents
- Success criteria:
  - Behavior matches Sprint 1 output contract
- Minimal tests:
  - Output contract tests still pass
