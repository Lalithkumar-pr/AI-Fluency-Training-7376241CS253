"""Deterministic fault injection: no model call is needed."""
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
    ("good call", FakeCall("get_venue_capacity", '{"venue_type":"lecture_hall"}')),
    ("invalid JSON", FakeCall("get_venue_capacity", '{"venue_type":"lecture_hall"')),
    ("unknown tool", FakeCall("send_email", '{"to":"events@college.edu"}')),
    ("missing required", FakeCall("get_venue_capacity", '{}')),
    ("wrong type", FakeCall("get_venue_capacity", '{"venue_type":123}')),
    ("outside enum", FakeCall("get_venue_capacity", '{"venue_type":"stadium"}')),
    ("invented argument", FakeCall("get_venue_capacity", '{"venue_type":"lecture_hall","year":2026}')),
    ("negative attendees", FakeCall("estimate_refreshment_cost", json.dumps({"attendees": -5, "refreshment_type": "tea_snack"}))),
    # User-designed fault 1: tool name case mismatch.
    ("case-mismatched tool", FakeCall("Get_Venue_Capacity", '{"venue_type":"lecture_hall"}')),
    # User-designed fault 2: valid JSON, wrong top-level shape (array instead of object).
    ("JSON array arguments", FakeCall("get_venue_capacity", '["lecture_hall"]')),
    ("empty arguments string", FakeCall("estimate_refreshment_cost", "")),
    ("unsafe expression is not a tool", FakeCall("estimate_refreshment_cost", json.dumps({"attendees": 3, "refreshment_type": "tea_snack", "expression": "__import__('os').system('dir')"}))),
]

if __name__ == "__main__":
    print("=" * 92)
    for label, call in FAULTS:
        result = handle_tool_call(call, log=False)
        print(f"{label:<26} -> {result[:140]}")
    print("=" * 92)
    print("Every injected case returned a string; the test loop continued.")
