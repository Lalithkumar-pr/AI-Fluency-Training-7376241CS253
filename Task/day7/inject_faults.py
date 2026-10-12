"""Test defensive tool handling without depending on the model to make mistakes."""
import json
from robust_agent import handle_tool_call

class FakeFunction:
    def __init__(self, name, arguments):
        self.name, self.arguments = name, arguments

class FakeCall:
    def __init__(self, name, arguments, call_id="call_test"):
        self.id, self.type = call_id, "function"
        self.function = FakeFunction(name, arguments)

FAULTS = [
    ("a good call", FakeCall("get_study_progress", '{"subject": "JAVA"}')),
    ("invalid JSON", FakeCall("get_study_progress", '{"subject": "JAVA"')),
    ("unknown tool", FakeCall("delete_records", '{"subject": "SQL"}')),
    ("missing required", FakeCall("get_study_progress", '{}')),
    ("wrong type", FakeCall("get_study_progress", '{"subject": 101}')),
    ("value outside enum", FakeCall("get_study_progress", '{"subject": "BIOLOGY"}')),
    ("invented extra argument", FakeCall("get_study_progress", '{"subject": "SQL", "year": 2026}')),
    ("unknown subject reaches tool", FakeCall("get_next_deadline", '{"subject": "BIOLOGY"}')),
    ("unsafe expression", FakeCall("calculator", json.dumps({
        "expression": "__import__('os').system('echo unsafe')"
    }))),
    ("empty arguments string", FakeCall("calculator", "")),
]

if __name__ == "__main__":
    print("=" * 82)
    for label, call in FAULTS:
        result = handle_tool_call(call, log=False)
        print(f"{label:<28} -> {result[:110]}")
    print("=" * 82)
    print("Review the output to confirm malformed calls return text instead of crashing.")
