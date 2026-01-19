# ARCHITECTURE.md — Domain-agnostic Guided Expert Chat

This document is a **stable, human-readable architecture reference**.

## Goal
Build a **single-page LLM app** where different domains (Interview Prep vs Legal Employment) are implemented as **profiles**.

- **Sprint 1:** prompt-only pipeline (no retrieval, no tools)
- **Sprint 2:** add RAG (LangChain chains + retriever + vector store)
- **Sprint 3:** add tools/function calling, agent orchestration, optional long-term memory, optional automation hooks
- **Sprint 4:** harden, evaluate, deploy

## Core abstractions
- **Profile**: domain configuration (UI fields, system prompt variants, safety policy, feature toggles)
- **Pipeline**: “how we answer”
  - PromptOnlyPipeline (Sprint 1)
  - RAGPipeline (Sprint 2)
  - ToolCallingPipeline (Sprint 3 basic)
  - AgentPipeline (Sprint 3 advanced)

## Key modules
- UI: `app/ui/streamlit_app.py`
- Controller: `app/core/controller.py`
- Prompt builder: `app/core/prompt_builder.py`
- Safety guard: `app/core/safety.py`
- LLM clients:
  - Sprint 1: `app/core/llm/openai_client.py`
  - Sprint 2/3: `app/core/llm/langchain_client.py` (later)
- Retrieval (Sprint 2): `app/core/retrieval/*`
- Tools (Sprint 3): `app/core/tools/*`
- Memory (Sprint 3): `app/core/memory/*`
- Automation hooks (Sprint 3): `app/core/automation/*`

## Feature toggles
The controller selects behavior based on profile flags:
- `rag_enabled`
- `tools_enabled`
- `agent_enabled`
- `memory_enabled`

## Safety baseline (especially for legal domains)
- Input validation (length/empty)
- Prompt injection heuristics
- Refusal templates
- Avoid secrets/PII logging
