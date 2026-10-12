"""Compare unconstrained, JSON-mode and schema-mode extraction."""
import json
from config import client, MODEL, banner

SCHEMA = {
    "type": "object",
    "properties": {
        "event_type": {"type": "string", "enum": ["workshop", "seminar", "hackathon", "other"]},
        "attendees": {"type": "integer"},
        "needs_refreshments": {"type": "boolean"},
    },
    "required": ["event_type", "attendees", "needs_refreshments"],
    "additionalProperties": False,
}
QUESTION = "We are running a two-day hackathon for 120 students and need snacks. Extract the event type, attendee count, and whether refreshments are needed."

def ask(response_format, label):
    print(f"\n--- {label} ---")
    try:
        reply = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Extract the requested fields. When asked for JSON, return JSON only."},
                {"role": "user", "content": QUESTION},
            ],
            temperature=0,
            **({"response_format": response_format} if response_format is not None else {}),
        )
        raw = (reply.choices[0].message.content or "").strip()
        print("raw:", raw)
        try:
            print("parsed:", json.loads(raw))
        except json.JSONDecodeError as error:
            print(f"parsed: not valid JSON ({error})")
    except Exception as error:
        print(f"not supported here ({type(error).__name__}: {error})")

if __name__ == "__main__":
    banner("STRUCTURED OUTPUTS — CAMPUS EVENT PLANNER")
    ask(None, "1. no constraint")
    ask({"type": "json_object"}, "2. JSON mode")
    ask({"type": "json_schema", "json_schema": {"name": "event_request", "schema": SCHEMA, "strict": True}},
        "3. schema mode")
