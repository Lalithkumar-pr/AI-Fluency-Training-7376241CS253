import json
from config import client, MODEL, QUESTIONS, banner
from tools import TOOLS, TOOL_FUNCTIONS

SYSTEM_PROMPT = (
    "You are a college fee assistant. Never guess private fees. "
    "Use get_course_fee for every course fee and calculator for arithmetic. "
    "For general writing requests, answer directly without tools."
)

def agent(question, max_steps=6, verbose=True):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    for step in range(1, max_steps + 1):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            temperature=0,
        )
        message = response.choices[0].message

        if not message.tool_calls:
            return (message.content or "").strip()

        messages.append({
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments,
                    },
                }
                for call in message.tool_calls
            ],
        })

        for call in message.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments or "{}")
            function = TOOL_FUNCTIONS.get(name)
            result = function(**args) if function else f"Unknown tool: {name}"
            if verbose:
                print(f"step {step}: {name}({args}) -> {result}")
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result,
            })

    return "Stopped: maximum steps reached."

if __name__ == "__main__":
    banner("AI AGENT")
    for q in QUESTIONS:
        print("Q:", q)
        print("A:", agent(q))
        print("-" * 70)
