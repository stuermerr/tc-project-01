# PLAN.md — Implementation plan

> This file is updated during the course.
> Each step should be independently implementable and testable.

## 0) Goals
- 

## 1) Non-goals
- 

## 2) Architecture overview
- 

## 3) Stepwise plan
### Step 1 — Repo bootstrapping
- [ ] Create minimal Streamlit UI skeleton
- [ ] Create OpenAI client wrapper
- [ ] Add configuration loading (.env)
- [ ] Add one basic unit test

### Step 2 — Profiles + prompt variants
- [ ] Define profile schema (YAML)
- [ ] Add interview profile with 5 system prompts
- [ ] Implement prompt builder
- [ ] Add tests for prompt builder

### Step 3 — Safety guard
- [ ] Input validation (length, empty, basic PII warning)
- [ ] Prompt injection heuristics
- [ ] Refusal templates
- [ ] Tests for safety guard

### Step 4 — Controller + pipeline
- [ ] PromptOnlyPipeline (Sprint 1)
- [ ] Controller orchestration
- [ ] Integration test: UI → controller → response

## 4) External services & APIs
- OpenAI API

## 5) Observability (later)
- Structured logging with redaction
- Correlation IDs per request

