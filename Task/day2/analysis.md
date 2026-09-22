# Day 2 Task Analysis
## Direct Prompting vs Chain-of-Thought vs ReAct

## 1. Scenario

This task uses a **personal study-planning scenario**, intentionally different from the college-fee scenario used in the lab.

A student has a limited 90-minute study session. The private study-time data is:

| Subject | Required time |
|---|---:|
| Python | 40 minutes |
| Computer Networks | 35 minutes |
| SQL | 30 minutes |
| Machine Learning | 50 minutes |

For the ReAct experiment, these exact times are kept outside the user question and are available only through a tool.

## 2. Direct Prompting

Direct prompting sends the question directly to the language model and asks for an answer. It has no tool access and no explicit step-by-step reasoning instruction. When all required times are present in the prompt, it can solve the planning problem directly. Its limitation is that it cannot retrieve private study data that is not in its context.

## 3. Chain-of-Thought Prompting

Chain-of-Thought-style prompting asks the model to reason through the problem step by step. With the study times supplied, the model can compare combinations and check the 90-minute limit. This can help on multi-step reasoning tasks.

However, reasoning cannot create missing facts. If the private study times are absent, CoT has no mechanism to query the private data. It may therefore be unable to solve the real planning problem reliably.

## 4. ReAct Agent

The ReAct agent combines reasoning with actions and observations. It has two tools: `get_study_time` for private study data and `calculator` for arithmetic.

A typical cycle is:

**Thought → Action → Observation → Thought → Action → Observation → Final Answer**

The agent can retrieve the required study times, use the returned observations, calculate feasible combinations, and then give a recommendation. This demonstrates why ReAct is different from reasoning alone.

## 5. Comparison

| Basis | Direct prompting | Chain-of-Thought | ReAct agent |
|---|---|---|---|
| Reasoning depth | Low to moderate | Higher | Higher and iterative |
| Tool usage | None | None | Yes |
| Multi-step reliability | Depends on prompt/model | Often improved when facts are known | Can combine reasoning with verified tool results |
| Transparency | Final response only | Reasoning-oriented response | Tool actions and observations can be traced |
| Speed / cost | Lowest | Higher | Usually highest |
| Consistency | Usually stable at temperature 0 | Can vary at non-zero temperature | Can vary in tool path and model decisions |

## 6. Self-Consistency

`self_consistency.py` runs the same reasoning question five times at temperature 0.8 and then runs a control at temperature 0.

Record the actual outputs from your run in this section after executing the script. Identify the majority answer and whether it is correct. At temperature 0, repeated outputs should generally be more consistent.

## 7. Suitability

Direct prompting is suitable when the complete information is already available and the task is simple. Chain-of-Thought-style prompting is useful when the information is available but several reasoning steps are required. ReAct is suitable when the task requires both reasoning and external/private information retrieval.

For this scenario, ReAct is useful because the exact study times are outside the model's immediate context and must be retrieved before planning.

## 8. Conclusion

Direct prompting, Chain-of-Thought, and ReAct represent increasing interaction capabilities. Direct prompting answers directly. Chain-of-Thought encourages deeper reasoning over information already available. ReAct adds a tool interaction loop, allowing the model to obtain information, observe the results, reason again, and continue until it can complete the task.
