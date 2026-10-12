"""Guarded tool-calling agent for the campus event planner."""
import json
from config import client, MODEL, banner
from tools_v2 import TOOLS, TOOL_FUNCTIONS, SCHEMAS
from validate import validate_arguments

SYSTEM_PROMPT = (
    "You are a campus event planning assistant. Use get_venue_capacity to look up venue capacity. "
    "Use estimate_refreshment_cost for refreshment estimates. Do not invent venue capacities or prices. "
    "Valid venue types: lecture_hall, seminar_room, computer_lab. "
    "Valid refreshment types: water_snack, tea_snack, lunch_box. "
    "Use tools when a lookup or calculation is needed; answer greetings directly."
)
MAX_TOKENS = 500
REPEAT_LIMIT = 3

def handle_tool_call(call, log=True):
    """Parse, look up, validate and execute; always return a string."""
    name = call.function.name
    raw = call.function.arguments or "{}"
    try:
        arguments = json.loads(raw)
    except json.JSONDecodeError as error:
        return f"Argument error: invalid JSON ({error}). Send valid JSON for '{name}'."

    function = TOOL_FUNCTIONS.get(name)
    if function is None:
        return f"Unknown tool: {name}. Available tools: {', '.join(TOOL_FUNCTIONS)}."

    problem = validate_arguments(arguments, SCHEMAS[name])
    if problem:
        return f"Argument error: {problem}"

    try:
        result = str(function(**arguments))
    except Exception as error:
        result = f"Tool error in {name}: {type(error).__name__}: {error}"

    if log:
        print(f"      {name}({arguments}) -> {result[:120]}")
    return result

def agent(question, max_steps=6, verbose=True):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    seen = {}
    max_tokens = MAX_TOKENS
    step = 0
    while step < max_steps:
        step += 1
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS,
            temperature=0, max_tokens=max_tokens,
        )
        choice = response.choices[0]
        message = choice.message

        if choice.finish_reason == "length":
            if max_tokens >= 2000:
                return "Stopped: reply was still truncated at 2000 tokens."
            max_tokens = min(max_tokens * 2, 2000)
            if verbose:
                print(f"   step {step}: truncated; retrying with max_tokens={max_tokens}")
            # Retry the same conversation; do not treat incomplete output as a tool call.
            step -= 1
            continue

        if not message.tool_calls:
            return (message.content or "").strip()

        messages.append({
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": [
                {"id": call.id, "type": "function",
                 "function": {"name": call.function.name, "arguments": call.function.arguments}}
                for call in message.tool_calls
            ],
        })
        if verbose:
            print(f"   step {step}: {len(message.tool_calls)} tool call(s)")

        for call in message.tool_calls:
            signature = (call.function.name, call.function.arguments)
            seen[signature] = seen.get(signature, 0) + 1
            if seen[signature] >= REPEAT_LIMIT:
                return f"Stopped: {call.function.name} was called {REPEAT_LIMIT} times with the same arguments and made no progress."
            result = handle_tool_call(call, log=verbose)
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

    return "Stopped: maximum steps reached without a final answer."

if __name__ == "__main__":
    banner("DAY 6 — CAMPUS EVENT PLANNER")
    questions = [
        "What is the capacity of a computer lab?",
        "Estimate tea and snack cost for 80 attendees.",
        "We need a venue for 50 people and lunch boxes for 50 people. Check the computer lab capacity and estimate the lunch-box cost.",
        "What is the capacity of a stadium?",
        "Write a one-line welcome message for a campus event.",
    ]
    for question in questions:
        print(f"\nQ: {question}")
        try:
            print("A:", agent(question))
        except Exception as error:
            print(f"Provider/API error: {type(error).__name__}: {error}")
