# Analysis: Plain Chatbot vs Rule-Based Workflow vs AI Agent

## 1. Scenario

The selected scenario is a college course-fee assistant. The college stores private fee information that is not included in the public training data of a general LLM:

| Course | Private fee |
|---|---:|
| CS101 | Rs. 12,000 |
| AI202 | Rs. 18,000 |
| DS303 | Rs. 15,000 |

The system must answer fee questions, perform calculations, compare courses, and respond to a general welcome-message request. The same questions are given to a plain chatbot, a rule-based workflow, and an AI agent.

## 2. Plain chatbot

The plain chatbot sends the user's question directly to an LLM. It does not receive the college's private fee dictionary and it has no database lookup tool or calculator tool. Therefore, it cannot reliably know the actual fees. It may produce a confident but incorrect answer, or it may honestly state that it does not know.

For the first three questions, the chatbot is likely to hallucinate because the private data is not present in its prompt or context. Question four does not require private data, so the chatbot can normally create a suitable welcome message. Its main strength is flexibility in natural-language generation. Its main weakness is that it cannot verify private facts and may sound confident even when it is wrong.

## 3. Rule-based workflow

The rule-based workflow uses predefined Python conditions, regular expressions, and the local `COURSE_FEES` dictionary. It does not use an LLM. The program extracts course codes, finds their fees, checks keywords such as `total`, `scholarship`, and `more expensive`, and applies fixed calculations.

When the input matches a rule, the result is predictable, repeatable, and fast. However, the workflow is rigid. A differently worded question may fail even when it has the same meaning. It also cannot easily handle new requests unless a programmer adds more rules. Its reliability is high for covered cases but low for unexpected language and unsupported tasks.

## 4. AI agent

The AI agent combines an LLM, tools, and a loop. The LLM interprets the question and decides whether it needs a fee lookup or a calculation. The Python program executes the selected tool, returns the observation to the LLM, and allows the LLM to continue until it produces a final answer or the maximum number of steps is reached.

The fee lookup tool reads the private course-fee dictionary. The calculator performs arithmetic without using unsafe `eval()`. For the scholarship question, the agent can look up CS101 and AI202, calculate `(12000 + 18000) * 0.9`, observe the result, and answer Rs. 27,000. For the comparison question, it can look up both fees and calculate the difference. For the welcome message, it should not need a tool.

The agent is more flexible than the fixed workflow and can handle multi-step requests. However, its behaviour depends on the LLM. It may skip a tool, choose an incorrect tool, produce malformed arguments, repeat actions, or stop at the step limit. Therefore, tool validation, logging, permissions, and human review may be required in a real system.

## 5. Comparison table

| Basis | Plain chatbot | Rule-based workflow | AI agent |
|---|---|---|---|
| Flexibility | Flexible language generation but lacks private facts | Low; follows fixed patterns | High; interprets requests and selects tools |
| Decision-making | Generates an answer; no external action | Programmer-defined conditions | LLM chooses actions within allowed tools |
| Tool usage | None | Python functions are fixed logic, not LLM-selected tools | Uses fee lookup and calculator tools |
| Private-data access | No access in this implementation | Direct access to local dictionary | Accesses private data through tools |
| Multi-step task handling | Limited to response generation | Only explicitly programmed sequences | Can perform lookup, calculation, observation, and follow-up |
| Automation | Answers text questions | Fast for predefined cases | Automates flexible multi-step tasks |
| Reliability | Low for unknown private facts; may hallucinate | High for covered rules; rigid outside them | Potentially useful but depends on tool selection and model behaviour |

## 6. Suitability analysis

For this scenario, the rule-based workflow is suitable for a small set of highly predictable fee operations because the answers must be exact and repeatable. It is easy to test and does not depend on model behaviour. However, it requires a new rule for every new wording or request.

The AI agent is suitable when students or staff ask varied natural-language questions involving several steps, such as comparing courses, applying discounts, or checking combinations within a budget. It can select tools dynamically and handle requests that were not individually hard-coded. Nevertheless, it should be constrained by trusted tools and validation because an LLM can make mistakes.

A practical college system could use a rule-based workflow for common, high-confidence operations and route unfamiliar or multi-step questions to an agent. Sensitive actions, such as changing official fee records or issuing refunds, should require additional authorization and verification.

## 7. Conclusion

A plain chatbot is appropriate for conversation, drafting, explanations, and creative responses where verified private data is not required. A rule-based workflow is appropriate for stable, repetitive, and safety-sensitive operations with clearly defined inputs and outputs. An AI agent is appropriate for flexible tasks that require interpretation, tool selection, observation, and multiple steps.

The central distinction is that a chatbot mainly uses an LLM to generate a response, a rule-based workflow follows programmer-written conditions, and an AI agent combines an LLM, tools, and a loop. The choice should depend on the required flexibility, correctness, data access, complexity, and risk.

## 8. Personal observations from execution

Complete this section after running the programs. Do not invent values.

- Chatbot Q1 correct: [Y/N]
- Chatbot Q2 correct: [Y/N]
- Chatbot Q3 correct: [Y/N]
- Chatbot Q4 handled well: [Y/N]
- Workflow Q1 correct: [Y/N]
- Workflow Q2 correct: [Y/N]
- Workflow Q3 correct: [Y/N]
- Workflow Q4 handled well: [Y/N]
- Agent Q1 correct: [Y/N]
- Agent Q2 correct: [Y/N]
- Agent Q3 correct: [Y/N]
- Agent Q4 handled well: [Y/N]
- Challenge handled by workflow: [Y/N]
- Challenge handled by agent: [Y/N]
- Repeat-run consistency: [describe]
- Approximate response time: [record from your run]
- Agent trace for Question 2: [paste terminal output here]

## 9. Discussion questions

### 1. Why is a confident wrong fee dangerous?

A confident wrong fee can cause a student or staff member to make a financial decision based on false information. A clear “I don't know” exposes uncertainty and allows the user to verify the fee through an official source.

### 2. Why might a finance office prefer a workflow?

A finance office may prefer a workflow because its approved rules are predictable, auditable, fast, and easy to test. It does not introduce the same open-ended generation risk as an LLM.

### 3. What problems can changing agent steps cause?

Changing steps can make debugging, auditing, testing, cost estimation, and reproducibility difficult. The agent might also use different tools or take unnecessary actions for similar requests.

### 4. How can a hybrid system be designed?

The workflow can handle known course-code lookups, standard scholarship calculations, and validated comparisons. Requests involving ambiguous language, multiple conditions, or unsupported combinations can be passed to the agent. The agent's final answer should still be checked against trusted data.

### 5. Which parts are the LLM, tools, and loop?

The LLM call is `client.chat.completions.create(...)`. The tools are `get_course_fee()` and `calculator()` in `tools.py`. The loop is the `for step in range(1, max_steps + 1)` section in `agent.py`, which repeatedly requests a decision, executes tools, sends observations back, and waits for the final response.
