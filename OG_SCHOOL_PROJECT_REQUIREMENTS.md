Checklist derived from the original OG brief, verified against code where possible.

OG requirements checklist (required + optional)

Required tasks (minimum requirements)
- [x] Decide interview-prep focus (tailored questions based on JD/CV) - defined in REQUIREMENTS.md
- [x] Decide front-end approach (Streamlit single-page) - REQUIREMENTS.md + app/ui/App.py
- [x] Create OpenAI API key + use securely (env-based) - openai_client.py loads dotenv
- [x] Choose one allowed OpenAI model - DEFAULT_MODEL = gpt-4o-mini in openai_client.py
- [x] Write >= 5 system prompts with distinct techniques - prompts.py defines 5 variants
- [x] Tune >= 1 OpenAI parameter - temperature slider in Streamlit UI
- [x] Add >= 1 safety/security guard - safety module + output validation

Optional improvements (OG list)

Easy:
- [ ] Ask ChatGPT to critique the app
- [ ] Improve prompts for your preferred domain (not explicitly tracked)
- [x] Add stronger safety checks - multiple safety layers implemented
- [ ] Add difficulty levels for questions (easy/medium/hard)
- [ ] Support concise vs detailed outputs
- [ ] Generate structured evaluation guidelines (not explicit)
- [x] Role-play different interviewer personas (strict/neutral/friendly) - prompt variants include friendly/neutral/strict

Medium:
- [ ] Expose many OpenAI settings in the UI (model, temperature, penalties, etc.) (partial: model + temp + reasoning effort)
- [ ] Add at least two JSON output formats (only one schema exists now)
- [x] Deploy the app online
- [ ] Estimate and display prompt cost
- [ ] Read OpenAI docs and implement one self-chosen improvement
- [ ] Add a second LLM to judge/validate the first model's outputs
- [ ] Attempt to jailbreak the app and document results
- [x] Add an extra field for the job description (JD input present)
- [ ] Allow choosing among multiple LLM providers
- [ ] Add image generation and integrate it

Hard:
- [x] Build a true chatbot experience (multi-turn)
- [ ] Deploy to a major cloud provider (AWS/Azure, etc.)
- [x] Use LangChain to implement chains/agents (LangChain ChatOpenAI wrapper; no explicit agents)
- [ ] Add a vector database to avoid repeated prep content
- [ ] Use open-source LLMs
- [ ] Fine-tune an LLM for interview-prep behavior

Comparison: what is fulfilled vs OG requirements

Clearly fulfilled (verified in code or docs)
- Streamlit multipage app (classic + chat)
- OpenAI API call + allowed model selection (gpt-4o-mini + GPT-5 options)
- 5 system prompt variants (prompts.py)
- Model selector + temperature / reasoning effort in the UI
- Safety guardrails (input validation, injection heuristics, output validation)
- JD and CV inputs
- Structured JSON output + markdown rendering (classic)
- Multi-turn chat UI (OpenAI + LangChain)
- LangChain-based implementation (chat + questions)

Likely fulfilled but should verify in code if needed
- API key is provided via environment (dotenv load present; assumes OPENAI_API_KEY exists)

Not done (or not documented) from OG optional list
- Cost estimation
- Deployment (actual)
- LLM-as-judge
- Jailbreak testing + documentation
- Second JSON output format
- Difficulty toggle
- Concise vs detailed output toggle
- Multi-provider support
- Image generation
- Vector DB
- Open-source LLMs
- Fine-tuning
- Major cloud deployment

Optional extensions in REQUIREMENTS.md you can add now
- [x] Model selector UI (list of LLM models)
- [x] Deploy the app to the internet
- [x] Full-fledged chatbot (multi-turn)
- [x] LangChain chains/agents (LangChain-based implementation)

You asked for at least 2 medium and 2 hard optional tasks from OG list

Medium (pick at least 2)
- [ ] Add at least two JSON output formats (e.g., questions_only vs full_analysis)
- [ ] Estimate and display prompt cost (token estimate + cost calc)
- [ ] Expose more OpenAI settings in UI (top_p, penalties, model)
- [ ] Add LLM-as-judge (second call to score relevance/clarity)

Hard (pick at least 2)
- [x] True chatbot experience (multi-turn session memory in Streamlit)
- [ ] Deploy to major cloud provider (AWS/Azure)
- [x] LangChain chains/agents
- [ ] Vector DB to avoid repeated questions across sessions
