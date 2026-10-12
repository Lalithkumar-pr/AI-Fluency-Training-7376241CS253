"""Small schema validator for the JSON Schema subset used in this task."""
from tools_v2 import SCHEMAS

TYPES = {
    "string": str,
    "number": (int, float),
    "integer": int,
    "boolean": bool,
    "array": list,
    "object": dict,
}

def validate_arguments(arguments, schema):
    """Return None if valid; otherwise return a human-readable error string."""
    if not isinstance(arguments, dict):
        return "Arguments must be a JSON object."

    properties = schema.get("properties", {})
    for name in schema.get("required", []):
        if name not in arguments:
            return f"Missing required argument '{name}'. Expected: {', '.join(properties)}."

    if schema.get("additionalProperties") is False:
        extra = [key for key in arguments if key not in properties]
        if extra:
            return f"Unexpected argument(s): {', '.join(extra)}. Allowed: {', '.join(properties)}."

    for name, value in arguments.items():
        rule = properties.get(name, {})
        expected = TYPES.get(rule.get("type"))
        # bool is a subclass of int in Python; reject it for numeric types.
        if rule.get("type") in ("integer", "number") and isinstance(value, bool):
            return f"Argument '{name}' must be a {rule['type']}, but got bool: {value!r}."
        if expected and not isinstance(value, expected):
            return f"Argument '{name}' must be a {rule['type']}, but got {type(value).__name__}: {value!r}."
        if "enum" in rule and value not in rule["enum"]:
            return f"Argument '{name}' must be one of {rule['enum']}, got {value!r}."
    return None

if __name__ == "__main__":
    cases = [
        ("valid venue", "get_venue_capacity", {"venue_type": "lecture_hall"}),
        ("missing required", "get_venue_capacity", {}),
        ("wrong type", "get_venue_capacity", {"venue_type": 123}),
        ("outside enum", "get_venue_capacity", {"venue_type": "stadium"}),
        ("extra argument", "get_venue_capacity", {"venue_type": "lecture_hall", "year": 2026}),
        ("valid refreshments", "estimate_refreshment_cost", {"attendees": 20, "refreshment_type": "tea_snack"}),
        ("bool is not an integer", "estimate_refreshment_cost", {"attendees": True, "refreshment_type": "tea_snack"}),
    ]
    for label, tool_name, args in cases:
        print(f"{label:<26} {args!r} -> {validate_arguments(args, SCHEMAS[tool_name]) or 'OK'}")
