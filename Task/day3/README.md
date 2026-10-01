# Day 3 ReAct Agent Lab

Place this folder beside your existing `config.py` and `.env` from Day 1, or copy these files into your existing `day1_lab` folder as the manual instructs.

## Setup
```bash
pip install -r requirements.txt
python my_tools.py
python my_agent.py
python my_agent_fixed.py
```

Run from this directory so `notice.html` is found. `config.py` must provide `client`, `MODEL`, and `banner` as in your Day 1 setup.

## Experiments
1. Change the question in `my_agent.py` for the Part C questions.
2. Try the missing `fees.html` case with both agent versions.
3. Generate `big.html` with `python make_big_page.py`; compare output limits.
4. Record your actual outputs, step counts, and failures in your observation table. Do not claim sample outcomes as observed results.
