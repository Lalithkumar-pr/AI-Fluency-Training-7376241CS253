import json
from config import client, MODEL
from tools import TOOLS, TOOL_FUNCTIONS

QUESTION = """
I have a 90-minute study session. Find a combination of complete study
tasks that maximizes the number of tasks I can finish. Available subjects
are Python, Computer Networks, SQL, and Machine Learning. Their exact
private study times are not given here, so use the available tools to
retrieve them. Do not guess missing times.
"""

SYSTEM_PROMPT = """
You are a study-planning ReAct agent. Use get_study_time whenever an exact
private study time is needed. Use calculator for arithmetic. Reason about
what information is missing, call tools, observe results, and continue
until you can give a justified final answer.
"""

def agent(question, max_steps=8):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    for step in range(1, max_steps + 1):
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS, temperature=0
        )
        message = response.choices[0].message
        if not message.tool_calls:
            return message.content.strip()

        messages.append({
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": [
                {"id": c.id, "type": "function",
                 "function": {"name": c.function.name,
                              "arguments": c.function.arguments}}
                for c in message.tool_calls
            ],
        })

        for call in message.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments or "{}")
            result = TOOL_FUNCTIONS[name](**args)
            print(f"Step {step}: {name}({args}) -> {result}")
            messages.append({
                "role": "tool", "tool_call_id": call.id, "content": result
            })

    return "Stopped: maximum steps reached."

if __name__ == "__main__":
    print("=== REACT AGENT ===")
    print("Q:", QUESTION)
    print("A:", agent(QUESTION))
