"""Reliable study-planner agent with validated tools, bounded retries, and loop guards."""
import json
from config import client, MODEL, banner
from tools_v2 import TOOLS, TOOL_FUNCTIONS, SCHEMAS
from validate import validate_arguments

SYSTEM_PROMPT = (
    "You are a personal study planner assistant. Use get_study_progress for study-hour facts "
    "and get_next_deadline for deadlines; never invent these values. Use calculator for every "
    "arithmetic step. Valid subjects: JAVA, NETWORKS, SQL. If no tool is needed, answer directly. "
    "Do not claim a tool succeeded unless its result supports the claim."
)
MAX_TOKENS = 500
REPEAT_LIMIT = 3

def handle_tool_call(call, log=True):
    """Safely handle one model-generated tool call; always return text."""
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
        {"role": "user", "content": question}
    ]
    seen = {}
    max_tokens = MAX_TOKENS
    for step in range(1, max_steps + 1):
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS,
            temperature=0, max_tokens=max_tokens
        )
        choice = response.choices[0]
        message = choice.message
        if choice.finish_reason == "length":
            if max_tokens >= 2000:
                return "Stopped: reply remained truncated at 2000 tokens."
            max_tokens *= 2
            if verbose:
                print(f"   step {step}: truncated, retrying with max_tokens={max_tokens}")
            continue
        if not message.tool_calls:
            return (message.content or "").strip()
        messages.append({
            "role": "assistant", "content": message.content or "",
            "tool_calls": [{
                "id": call.id, "type": "function",
                "function": {"name": call.function.name, "arguments": call.function.arguments}
            } for call in message.tool_calls]
        })
        if verbose:
            print(f"   step {step}: {len(message.tool_calls)} tool call(s)")
        for call in message.tool_calls:
            signature = (call.function.name, call.function.arguments)
            seen[signature] = seen.get(signature, 0) + 1
            if seen[signature] >= REPEAT_LIMIT:
                return (f"Stopped: {call.function.name} was called {REPEAT_LIMIT} times "
                        "with identical arguments and made no progress.")
            result = handle_tool_call(call, log=verbose)
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
    return "Stopped: maximum steps reached without a final answer."

if __name__ == "__main__":
    banner("ROBUST STUDY PLANNER AGENT")
    questions = [
        "How many study hours remain for JAVA?",
        "When is the next SQL deadline, and what task is due?",
        "I completed 6.5 of 10 study hours. Calculate the percentage completed.",
        "Give me a short motivational sentence for my next study session."
    ]
    for question in questions:
        print("\\nQ:", question)
        try:
            print("A:", agent(question))
        except Exception as error:
            print(f"API request failed ({type(error).__name__}: {error})")
