# Repo Guide - Interview Practice App

## Overview
This repo contains a single-page Streamlit app that generates five interview questions using an OpenAI model. The app collects optional job description, CV text, and a user prompt, runs safety checks, builds a prompt, calls the model, and formats the response into the required sections.

## Directory map
- app/core - Core business logic (validation, prompt building, formatting, LLM wrapper).
- app/core/llm - Thin wrapper around the OpenAI client.
- app/ui - Streamlit UI entry point and multipage views.
- app/ui/pages - Streamlit multipage directory (classic flow).
- tests - Unit and integration tests.
- README.md - How to run the app and tests.
- PROGRESS_TRACKING.md - Decisions and milestones.

## Main execution flow (ASCII)
User
  |
  v
Streamlit UI (app/ui/Interview_Preparation_Chat.py)
  |
  v
RequestPayload (app/core/dataclasses.py)
  |
  v
generate_questions (app/core/orchestration.py)
  |
  +--> validate_inputs (app/core/safety.py)
  |
  +--> get_prompt_variants (app/core/prompts.py)
  |
  +--> build_messages (app/core/prompt_builder.py)
  |
  +--> generate_completion (app/core/llm/openai_client.py)
  |
  +--> format_response (app/core/response_formatter.py)
  |
  v
Response text rendered in Streamlit

## Module responsibilities and how they connect
- app/core/dataclasses.py
  - RequestPayload: data container passed from UI to orchestration.
  - PromptVariant: system prompt metadata used by the dropdown and prompt builder.

- app/core/prompts.py
  - get_prompt_variants(): returns the list of PromptVariant entries.
  - Used by: Streamlit UI (dropdown) and orchestration (variant selection).

- app/core/safety.py
  - validate_inputs(): enforces max length and prompt-injection heuristics.
  - Used by: orchestration before any model call.

- app/core/prompt_builder.py
  - build_messages(): builds the system and user messages for the OpenAI call.
  - Used by: orchestration.

- app/core/llm/openai_client.py
  - generate_completion(): sends the chat completion request to OpenAI.
  - Used by: orchestration.

- app/core/response_formatter.py
  - format_response(): ensures the response has the required sections and 5 tagged questions.
  - Used by: orchestration.

- app/core/orchestration.py
  - generate_questions(): main coordinator that wires safety, prompt building, LLM call, and formatting.
  - Used by: Streamlit UI.

- app/ui/Interview_Preparation_Chat.py
  - main(): renders the chat landing page for the multipage app.
  - Script entry point: streamlit run app/ui/Interview_Preparation_Chat.py
- app/ui/chat_ui.py
  - render_chat_ui(): shared chat UI layout and behavior.
- app/ui/classic_ui.py
  - render_classic_ui(): shared classic UI layout and behavior.
- app/ui/pages/1_Generate_Interview_Questions.py
  - Multipage wrapper that renders the classic UI.

## Tests and what they cover
- tests/test_prompts.py - Prompt variant list size and non-empty system prompts.
- tests/test_safety.py - Injection detection and input length limits.
- tests/test_prompt_builder.py - Message ordering and placeholder handling.
- tests/test_openai_client.py - OpenAI payload construction (mocked).
- tests/test_response_formatter.py - Required sections and question count enforcement.
- tests/test_controller.py - Orchestration flow with safety short-circuit and success path.
- tests/test_streamlit_app.py - Import smoke test for Streamlit app entrypoint.
- tests/test_streamlit_pages.py - Import smoke test for Streamlit pages.
- tests/test_chat_ui.py - Import smoke test for shared chat UI.
- tests/test_integration.py - End-to-end flow with a mocked OpenAI client.

## Scripts and commands
- Run the app: streamlit run app/ui/Interview_Preparation_Chat.py
- Run tests: pytest -q
