# Day 8 — Agentic RAG System with Memory, Guardrails, and Tool Calling

A beginner-friendly, Windows/PowerShell project demonstrating document ingestion, chunking, embeddings, Chroma vector search, a relevance guard, a LangGraph tool-using agent, conversational memory, safe arithmetic, and attendance eligibility checks.

> **Honest execution note:** the package is designed to run after dependencies are installed. Syntax checks and dependency-free unit tests are run when this ZIP is generated. LLM/Chroma integration requires installing the requirements and selecting an embedding/chat provider; no API key, model download, or live integration is assumed.

## 1. Architecture

1. `1_ingest.py` reads all `data/*.md` files, splits them into chunks, embeds them, and saves a Chroma database.
2. `2_search.py` queries that database, prints the retrieved chunk and distance, and applies a configurable relevance threshold.
3. `task_agent.py` exposes four tools to a LangGraph agent:
   - `search_handbook`: grounded document retrieval with a no-match fallback.
   - `get_course_fee`: course fees from `data/fee_policy.md`.
   - `calculator`: restricted arithmetic parser; does not use unrestricted `eval()`.
   - `check_exam_eligibility`: implements the exact attendance bands in `data/exam_regulations.md`.
4. A LangGraph checkpointer keeps conversation context for a consistent thread ID during the five-question demo.

Distance thresholds are **not universal**. The default `MAX_DISTANCE=0.6` is only a starting point for the lightweight hash embeddings. Inspect actual scores with `2_search.py` and tune `.env` for your chosen embedding model/vector-store configuration.

## 2. Project structure

```text
day8_task/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── lc_config.py
├── utils.py
├── 1_ingest.py
├── 2_search.py
├── task_agent.py
├── results.md
├── run_log.txt
├── data/
│   ├── hostel_rules.md
│   ├── placement_policy.md
│   ├── exam_regulations.md
│   ├── fee_policy.md
│   ├── library.md
│   └── ai_fluency_training.md
└── tests/
    └── test_utils.py
```

## 3. Prerequisites

- Windows 11 and Python 3.10 or 3.11 recommended.
- Internet access to install Python packages.
- For a natural-language agent, choose **one** chat provider:
  - **Ollama local:** install Ollama, start its service, and pull a chat model such as `llama3.1`. No hosted API key is needed.
  - **Groq hosted:** obtain a Groq API key and put it in `.env`. API access/model availability may depend on your account.
- Embeddings:
  - `hash` works locally without a model download. It is a lightweight deterministic fallback, not a high-quality semantic embedding model.
  - `ollama` requires an embedding model downloaded in Ollama (for example `nomic-embed-text`).

## 4. Setup in PowerShell

Open PowerShell in the directory where you extracted the ZIP:

```powershell
cd day8_task
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

If PowerShell blocks activation, you can use this command for the current terminal session only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Edit `.env` before running the agent. A basic local retrieval setup can use `EMBED_PROVIDER=hash`. For the agent, set `PROVIDER=ollama` and ensure Ollama is running with the selected model, or set `PROVIDER=groq` and add your API key.

## 5. Provider configuration

Example local Ollama configuration:

```dotenv
PROVIDER=ollama
CHAT_MODEL=llama3.1
EMBED_PROVIDER=hash
MAX_DISTANCE=0.6
```

For Ollama embeddings, set `EMBED_PROVIDER=ollama` and `EMBED_MODEL=nomic-embed-text`, then run `ollama pull nomic-embed-text`.

For Groq, set `PROVIDER=groq`, `CHAT_MODEL=llama-3.3-70b-versatile` (if available to your account), and `GROQ_API_KEY=your_real_key_here`. Do not commit `.env` or share your API key.

## 6. Build the vector database

Run this after installing dependencies and choosing `EMBED_PROVIDER`:

```powershell
python .\1_ingest.py
```

This recreates the local Chroma collection at `CHROMA_DIR` (default `chroma_db`). Re-run ingestion whenever source Markdown documents change. The database is intentionally not included in the ZIP.

## 7. Inspect retrieval and relevance guard

```powershell
python .\2_search.py
```

The script checks hostel in-time, placement criteria, international-student refund policy, and minimum exam attendance. It prints the real distances returned by Chroma; it does not pre-fill or fabricate scores. If the database is missing, it tells you to run ingestion first.

Tune `MAX_DISTANCE` in `.env` only after inspecting scores. Lower thresholds are stricter; the meaning and scale of distances depend on the embedding function and Chroma distance metric. The unknown refund-policy query should be rejected if its best result is beyond the threshold. With weak hash embeddings, verify the output and tune the threshold conservatively.

## 8. Run the agent and five-question demonstration

Make sure ingestion has completed and the chosen chat provider is configured:

```powershell
python .\task_agent.py
```

The script uses the same thread ID for all five questions:
1. What is the hostel in-time?
2. What are the eligibility criteria for placements?
3. What is the refund policy for international students?
4. What is the total amount for CS101 and AI202 course fees, plus the maximum late fee?
5. And if I pay only 5 days late instead?

The fourth and fifth turns share a checkpointed conversation. The system prompt instructs the agent to retain both course fees from the prior turn and replace only the late fee with the five-day fee. The fee policy states the expected totals: ₹32,000 and ₹30,500.

The agent's tool outputs are printed by the demo. LLM phrasing/tool selection can vary by provider; inspect the actual output rather than treating it as guaranteed. The unknown refund question must not be answered with an invented policy.

## 9. Eligibility tests

The agent script runs direct tool checks for 82%, 70%, and 50% attendance before the conversation demo. You can also run dependency-free unit tests:

```powershell
python -m unittest discover -s tests -v
```

Expected rules:
- 82%: eligible under the attendance rule.
- 70%: condonation application required; ₹500 per course, subject to approval.
- 50%: not eligible under the attendance rule.

## 10. Capture output and complete results

Capture terminal output (PowerShell):

```powershell
python .\1_ingest.py 2>&1 | Tee-Object -FilePath .\run_log.txt
python .\2_search.py 2>&1 | Tee-Object -FilePath .\run_log.txt -Append
python .\task_agent.py 2>&1 | Tee-Object -FilePath .\run_log.txt -Append
```

`results.md` is a template. Replace its placeholders with your real environment, actual ingestion counts, retrieval distances, agent responses, eligibility outputs, and any errors/fixes. `run_log.txt` is explicitly marked as a template until you capture a real run.

## 11. Common issues

- **`ModuleNotFoundError`:** activate `.venv`, then `pip install -r requirements.txt`.
- **Chroma database missing:** run `python .\1_ingest.py` before search/agent.
- **Ollama connection error:** start Ollama and check `ollama list`; pull the configured chat/embedding model.
- **Groq authentication/model error:** verify `.env`, API key, and model access.
- **Retrieval rejects everything:** inspect distances and tune `MAX_DISTANCE`; don't assume `0.6` is valid for every embedding.
- **Retrieval accepts an unrelated result:** lower the threshold and/or use a stronger embedding model; a threshold alone is not a complete semantic safety guarantee.
- **PowerShell activation blocked:** use the process-scoped execution-policy command shown above.
- **Chroma/platform install errors:** use a supported Python version and install from a fresh virtual environment.

## 12. Limitations

- Hash embeddings are a local, lightweight fallback; they do not provide the semantic quality of trained embeddings.
- A real LLM is required for the natural-language LangGraph agent. Retrieval and deterministic tools can run without a chat model.
- The included checkpointer is in-memory; conversation checkpoints are temporary and may not survive process restarts.
- A relevance threshold is model/configuration-specific and cannot prove that a result is relevant in every case.
- The fee and policy data are task-sheet examples, not real institutional advice.

## 13. Viva / demonstration talking points

- **RAG:** retrieves evidence before generating an answer.
- **Chunking:** splits long documents into searchable pieces.
- **Embeddings/vector store:** represents text as vectors and supports nearest-neighbour search.
- **Guardrail:** rejects low-relevance retrieval instead of guessing.
- **Tool calling:** delegates retrieval, fees, arithmetic, and eligibility to purpose-built functions.
- **Memory:** a thread ID and checkpointer preserve prior conversation state between turns.
- **Safe calculator:** parses a restricted arithmetic grammar rather than executing arbitrary Python.
- **Limitations:** retrieval scores depend on the embedding model and a chat model/provider must be configured for the full agent.
