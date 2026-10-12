# Day 6 Task — Reliable Tool Calling

**Scenario:** Campus Event Planner  
**Course:** Agentic AI: Foundations and Open-Source Practice

This is a standalone implementation of the Day 6 task. It uses a scenario different from the course-fee example in the lab manual.

## What the agent does

The agent helps plan a campus event using two tools:

- `get_venue_capacity(venue_type)` — looks up the capacity of a campus venue.
- `estimate_refreshment_cost(attendees, refreshment_type)` — estimates refreshment cost from a fixed price list.

The agent validates model-generated tool arguments, returns readable errors instead of crashing, handles multiple tool calls, retries truncated replies, detects repeated calls, and demonstrates structured outputs.

## Setup

Python 3.10+ recommended.

```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env`. For Groq, add your API key and choose a model available to your account. Do not commit `.env`.

```env
PROVIDER=groq
GROQ_API_KEY=your_key_here
MODEL=openai/gpt-oss-120b
```

For a local Ollama endpoint, use:

```env
PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_API_KEY=ollama
MODEL=qwen2.5:1.5b
```

The selected model/provider must support the features being tested. Structured schema mode is not supported by every endpoint/model.

## Run in this order

```bash
python validate.py
python inject_faults.py
python robust_agent.py
python structured_demo.py
```

Capture your own terminal screenshots and save them in `screenshots/`. Model wording, parallel calls, truncation and structured-output support vary by provider; the supplied analysis identifies observations that must be filled in after your own run.

## Files

- `tools_v2.py` — tool implementations, JSON Schema definitions, shared schema registry.
- `validate.py` — schema argument validator and standalone tests.
- `robust_agent.py` — guarded OpenAI-compatible tool-calling loop.
- `inject_faults.py` — deterministic fault-injection tests that need no model or internet.
- `structured_demo.py` — compares unconstrained output, JSON mode and schema mode.
- `analysis.md` — conceptual analysis, comparison and observation tables.
- `config.py` — provider/client configuration.
- `.env.example` — configuration template without secrets.
