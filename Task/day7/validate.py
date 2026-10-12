"""Small JSON-schema validator for the subset used by this project."""
TYPES = {"string": str, "number": (int, float), "integer": int,
         "boolean": bool, "array": list, "object": dict}

def validate_arguments(arguments, schema):
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
        # bool is a subclass of int in Python; explicitly reject it for numeric schemas.
        if expected and not isinstance(value, expected):
            return f"Argument '{name}' must be a {rule['type']}, but got {type(value).__name__}: {value!r}."
        if rule.get("type") in ("number", "integer") and isinstance(value, bool):
            return f"Argument '{name}' must be a {rule['type']}, not boolean."
        if "enum" in rule and value not in rule["enum"]:
            return f"Argument '{name}' must be one of {rule['enum']}, got {value!r}."
    return None

if __name__ == "__main__":
    from tools_v2 import SCHEMAS
    schema = SCHEMAS["get_study_progress"]
    cases = [
        {"subject": "JAVA"},
        {},
        {"subject": 101},
        {"subject": "BIOLOGY"},
        {"subject": "SQL", "year": 2026},
    ]
    for case in cases:
        print(f"{case!s:<45} -> {validate_arguments(case, schema) or 'OK'}")
