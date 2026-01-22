# Course Project Brief (Paraphrased) — Interview Preparation App

## Overview
You’re early in the AI engineering course and have learned prompt-engineering basics. This starter project is meant to turn those fundamentals into a working app.

You will build an **Interview Preparation app** that helps you practice for interviews more effectively (e.g., questions, exercises, personality-style prompts, strategies).

The key idea is: **use ChatGPT/OpenAI to generate interview prep content** so you can practice toward a target job.

---

## What you must build
### App format
- A **single-page web app**
- Built using either:
  - **Streamlit (Python)**, or
  - **Next.js (JavaScript)** (with HTML/CSS)

### LLM integration
- You must:
  - create and use an **OpenAI API key**
  - call the **OpenAI API** from your app
  - provide a **system prompt** (instructions for the model)
  - provide a **user prompt** (the interview-prep request)

### Freedom of scope (you choose what “interview prep” means)
You’re encouraged to decide what kind of interview prep your app focuses on, for example:
- generating interview questions
- practicing questions for a specific programming language
- preparing questions to ask the interviewer at the end
- analyzing a job description to propose a prep strategy
- any other interview-related training idea

Creativity is expected; you’re not meant to lock yourself into one narrow format.

---

## Required tasks (minimum requirements)
1) **Decide the exact interview-prep focus**
   - Research / think through what kind of prep you want your app to support.

2) **Decide your front-end approach**
   - Streamlit components (Python) OR HTML/CSS via Next.js.

3) **Create an OpenAI API key**
   - Use it securely in your app (don’t hardcode).

4) **Choose one allowed OpenAI model**
   - GPT-4.1  
   - GPT-4.1 mini  
   - GPT-4.1 nano  
   - GPT-4o  
   - GPT-4o mini  

5) **Write at least 5 different system prompts**
   - They must use **different prompting techniques**, such as:
     - zero-shot prompting
     - few-shot examples
     - chain-of-thought style reasoning (kept internal; you compare results)
     - or other distinct prompt strategies
   - You must test them and decide which works best.

6) **Tune at least one OpenAI parameter**
   - Examples:
     - temperature
     - top-p
     - frequency penalties
     - etc.

7) **Add at least one safety/security guard**
   - Prevent misuse / bad inputs
   - Examples: input validation, prompt validation, basic jailbreak defense

---

## Optional improvements (only after the main app works)

> These are grouped by difficulty. Some may require extra research or concepts introduced later.

### Easy options
- Ask ChatGPT to critique your app (usability, security, prompt quality)
- Improve prompts for your preferred domain (IT, finance, HR, communication, etc.)
- Add stronger safety checks (validate user input and/or system prompts)
- Add difficulty levels for questions (easy/medium/hard)
- Support concise vs detailed outputs
- Generate structured evaluation guidelines for interviews
- Role-play different interviewer personas (strict/neutral/friendly)

### Medium options
- Expose many OpenAI settings in the UI (model, temperature, penalties, etc.)
- Add **at least two JSON output formats** (structured outputs)
- Deploy the app online
- Estimate and display prompt cost
- Read OpenAI docs and implement one self-chosen improvement
- Add a second LLM to judge/validate the first model’s outputs (“LLM-as-judge”)
- Attempt to jailbreak your app and document results (e.g., in an Excel sheet)
- Add an extra field for the job description (or similar) to support more tailored prep (often described as “RAG” in the task list)
- Allow choosing among multiple LLM providers (OpenAI, Gemini, etc.)
- Add image generation creatively and integrate it into the app

### Hard options
- Build a true chatbot experience (multi-turn), not a single one-off call
- Deploy to a major cloud provider (e.g., AWS/Azure or similar)
- Use LangChain to implement chains/agents
- Add a vector database to detect repeated prep content and force novelty
- Use open-source LLMs (instead of OpenAI/Gemini/etc.)
- Fine-tune an LLM for interview-prep behavior

---

## How you will be evaluated

### Understanding of core concepts
You should be able to explain:
- different prompting techniques
- how model settings (temperature/top-p/etc.) change outputs
- the difference between **system**, **user**, and **assistant** roles
- different kinds of model output formats

### Technical implementation
Your project should:
- work as intended (it helps you prepare for interviews)
- call the OpenAI API correctly (right parameters)
- use a front-end library/framework successfully (Streamlit or Next.js)

### Reflection and improvement
You should be able to:
- justify your chosen prompting techniques and parameter settings
- explain risks/limitations of your app
- propose sensible improvements

### Bonus points
- To maximize points, you’re expected to implement **at least two** medium/hard optional tasks.
- Even more points if you implement more of the optional list.

---

## Framework guidance (Streamlit focus)
Streamlit is positioned as beginner-friendly:
- you can build an interactive UI using only Python
- no need to learn HTML/CSS/React for basic apps
- recommended learning path:
  - watch a quick intro video
  - read the official “Get Started” section
  - browse component documentation
  - optionally follow beginner tutorials (e.g., community tutorials)

---

## Suggested working approach
- Start by attempting the task for **1–5 hours** using:
  - your own knowledge
  - ChatGPT for understanding + coding + improvements + explanations
- If you feel missing knowledge:
  - revisit earlier course material
  - use the additional resources
- If after ~1–2 hours you’re stuck with no progress:
  - spend additional time with peers/JTL sessions
  - aim to work roughly half the time with others
- If you still can’t solve it:
  - review the suggested solution
  - invest time to fully understand it before submission
