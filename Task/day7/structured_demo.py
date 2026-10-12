"""Compare free text, JSON mode, and schema-constrained extraction."""
import json
from config import client, MODEL, banner

SCHEMA = {
    "type": "object",
    "properties": {
        "subject": {"type": "string", "enum": ["JAVA", "NETWORKS", "SQL"]},
        "wants_progress": {"type": "boolean"},
        "needs_tool": {"type": "boolean"}
    },
    "required": ["subject", "wants_progress", "needs_tool"],
    "additionalProperties": False
}
QUESTION = "How many study hours do I still need for Java, and when is its next deadline?"

def ask(response_format, label, system_message="Extract the request details as JSON. Reply with JSON only."):
    print(f"\\n--- {label} ---")
    try:
        reply = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": QUESTION}
            ],
            temperature=0,
            response_format=response_format
        )
        raw = (reply.choices[0].message.content or "").strip()
        print("raw:", raw)
        print("parsed:", json.loads(raw))
    except Exception as error:
        print(f"Not supported or request failed ({type(error).__name__}: {error})")

if __name__ == "__main__":
    banner("STRUCTURED OUTPUTS")
    ask(None, "1. no constraint (free text)")
    ask({"type": "json_object"}, "2. JSON mode: valid JSON, any shape")
    ask({"type": "json_schema", "json_schema": {
        "name": "study_request", "schema": SCHEMA, "strict": True}},
        "3. schema mode: valid JSON in the required shape")
