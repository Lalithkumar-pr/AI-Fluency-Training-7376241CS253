# Day 2 Task — Direct Prompting vs Chain-of-Thought vs ReAct

## Scenario
Personal Study Planner: deciding how to allocate a limited 90-minute study session.

This is intentionally different from the Day 2 lab's college-fee scenario.

## Files
- direct_prompt.py
- cot_prompt.py
- self_consistency.py
- tools.py
- react_agent.py
- config.py
- analysis.md
- screenshots/

## Setup
Create `.env` from `.env.example`, then install:

```bash
pip install -r requirements.txt
```
A student has 90 minutes available and needs to decide which complete study tasks can fit into that time.

Private data:

Subject	Required time
Python	40 min
Computer Networks	35 min
SQL	30 min
Machine Learning	50 min
Do not commit `.env`.
