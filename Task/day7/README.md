# Day 7 Task — Reliable Tool-Using Assistant

**Course:** Agentic AI: Foundations and Open-Source Practice  
**Task folder:** `Task/day7`  
**Scenario:** Personal Study Planner Assistant

## 1. Objective

Build a reliable assistant that can answer questions about a learner's study progress and upcoming deadlines by calling tools. The implementation should not trust model-generated tool arguments blindly: it must validate JSON, tool names, required fields, types, allowed values, and arithmetic expressions. It should return tool errors as text so the agent can recover instead of crashing.

This task applies the ideas visible in the supplied Day 7 starter files:
- structured JSON output;
- function/tool calling with strict argument schemas;
- argument validation;
- defensive tool execution;
- retry/step limits and repeated-call protection;
- fault injection to test failure cases.

The supplied examples use a college-fee assistant. **This task uses a different scenario**: a study planner. Replace the sample records with your own non-sensitive study subjects/hours/deadlines if you want to personalize it. Do not put passwords, account credentials, or other sensitive information in the project.

## 2. Project files

| File | Purpose |
|---|---|
| `config.py` | Loads the OpenAI-compatible API configuration from `.env` |
| `study_data.json` | Sample local study-progress data |
| `tools_v2.py` | Tool functions and JSON schemas |
| `validate.py` | Checks arguments against the supported schema rules |
| `structured_demo.py` | Compares free text, JSON mode, and schema-constrained extraction |
| `robust_agent.py` | Runs the tool-using assistant with validation and retry safeguards |
| `inject_faults.py` | Sends deliberately malformed calls through the defensive handler |
| `analysis.md` | Write-up template for observations and results |
| `Output/screenshots/` | Save terminal screenshots here |

## 3. Setup

Use Python 3.10 or newer.

1. Extract the ZIP into your repository's `Task/day7` folder.
2. Open a terminal in that folder.
3. Create and activate a virtual environment if you do not already have one:

   **Windows PowerShell**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
5. Copy `.env.example` to `.env`, then add your provider's API key and a model that supports tool calling. The sample is configured for Groq's OpenAI-compatible endpoint.
6. Run the scripts in the order below.

## 4. Run the task

```powershell
python validate.py
python structured_demo.py
python inject_faults.py
python robust_agent.py
```

If PowerShell blocks virtual-environment activation, you can run `.venv\Scripts\python.exe` directly or use your existing environment.

## 5. Experiments to perform

1. **Schema validation:** inspect the accepted and rejected arguments printed by `validate.py`.
2. **Structured output:** compare the three extraction modes. Record whether the selected model/provider supports each mode.
3. **Fault injection:** run `inject_faults.py`. Confirm that invalid JSON, unknown tools, missing arguments, wrong types, invalid enum values, extra fields, unknown subjects, and unsafe calculator expressions do not crash the handler.
4. **Tool calling:** run `robust_agent.py`. Observe when the model calls a tool and when it answers directly.
5. **Modify a record:** change one value in `study_data.json`, ask the matching question again, and confirm that the answer reflects the updated local data.
6. **Add a failure case:** add one case to `inject_faults.py` and explain the expected safe result.

## 6. Questions for `analysis.md`

- What problem does structured output solve?
- How is JSON mode different from schema-constrained output?
- Why should tool arguments be validated even when a tool schema is supplied to the model?
- What happens when the model sends malformed JSON or calls a nonexistent tool?
- Why is `eval()` unsafe for calculator input, and how does the supplied calculator avoid arbitrary code execution?
- What are the limitations of retry limits and repeated-call detection?
- Include actual outputs and explain any provider-specific errors.

## 7. Submission checklist

- [ ] All Python files run, or any provider limitation is clearly documented.
- [ ] `study_data.json` contains the records used in your experiment.
- [ ] `analysis.md` is completed with observations, not just copied definitions.
- [ ] Screenshots of the four scripts are saved under `Output/screenshots/`.
- [ ] No API key or `.env` file is committed to Git.
