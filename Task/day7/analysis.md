# Day 7 Task — Analysis and Observations

**Name:**  
**Date:**  
**Provider/model used:**  

## 1. Objective
In your own words, describe the purpose of a reliable tool-using assistant.

## 2. Structured output experiment
| Mode | Did it run? | Output shape | Observation |
|---|---|---|---|
| Free text | | | |
| JSON mode | | | |
| JSON Schema mode | | | |

Explain the difference between JSON mode and schema-constrained output.

## 3. Validation experiment
Record at least three valid/invalid argument examples from `validate.py`. Explain why each invalid input is rejected.

## 4. Fault injection
| Fault | Actual result | Why the result is safe |
|---|---|---|
| Invalid JSON | | |
| Unknown tool | | |
| Missing argument | | |
| Wrong type / invalid subject | | |
| Extra argument | | |
| Unsafe calculator expression | | |

## 5. Agent execution
Paste or summarize the actual outputs of `robust_agent.py`. Identify which questions required tools and which could be answered directly.

## 6. Modify and test
Change one value in `study_data.json`, rerun the relevant question, and explain how you verified that the answer changed.

## 7. Reflection
1. Why is schema validation needed even when the model receives tool schemas?
2. Why is `eval()` unsafe for calculator input?
3. What do the maximum-step and repeated-call guards prevent?
4. What failure modes remain possible in this design?
5. What would you improve next?

## 8. Conclusion
Write a short conclusion based on your own observations and actual run results.
