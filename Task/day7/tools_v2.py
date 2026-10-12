"""Study planner tools with strict function schemas."""
import ast
import json
import operator
from pathlib import Path

DATA_PATH = Path(__file__).with_name("study_data.json")
VALID_SUBJECTS = ("JAVA", "NETWORKS", "SQL")

def _load_data():
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))

def get_study_progress(subject: str) -> str:
    """Return completed and target study hours for one subject."""
    key = subject.strip().upper()
    record = _load_data()["subjects"].get(key)
    if record is None:
        return f"Unknown subject: {subject}. Valid subjects: {', '.join(VALID_SUBJECTS)}"
    return json.dumps({
        "subject": key,
        "hours_completed": record["hours_completed"],
        "hours_target": record["hours_target"],
        "hours_remaining": max(0, record["hours_target"] - record["hours_completed"])
    })

def get_next_deadline(subject: str) -> str:
    """Return the next recorded deadline and task for one subject."""
    key = subject.strip().upper()
    record = _load_data()["subjects"].get(key)
    if record is None:
        return f"Unknown subject: {subject}. Valid subjects: {', '.join(VALID_SUBJECTS)}"
    return json.dumps({"subject": key, "next_deadline": record["next_deadline"], "task": record["task"]})

_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.USub: operator.neg}

def _evaluate(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_evaluate(node.left), _evaluate(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_evaluate(node.operand))
    raise ValueError("Unsupported expression")

def calculator(expression: str) -> str:
    """Evaluate basic arithmetic without executing arbitrary Python."""
    try:
        return str(_evaluate(ast.parse(expression, mode="eval").body))
    except Exception as error:
        return f"Calculator error: {error}. Use numbers and + - * / with parentheses only."

TOOL_FUNCTIONS = {
    "get_study_progress": get_study_progress,
    "get_next_deadline": get_next_deadline,
    "calculator": calculator,
}

TOOLS = [
    {"type": "function", "function": {
        "name": "get_study_progress",
        "description": "Get completed, target, and remaining study hours for one subject.",
        "parameters": {"type": "object",
            "properties": {"subject": {"type": "string", "enum": list(VALID_SUBJECTS)}},
            "required": ["subject"], "additionalProperties": False}}},
    {"type": "function", "function": {
        "name": "get_next_deadline",
        "description": "Get the next deadline and task for one subject.",
        "parameters": {"type": "object",
            "properties": {"subject": {"type": "string", "enum": list(VALID_SUBJECTS)}},
            "required": ["subject"], "additionalProperties": False}}},
    {"type": "function", "function": {
        "name": "calculator",
        "description": "Evaluate a basic arithmetic expression using numbers, + - * / and parentheses.",
        "parameters": {"type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"], "additionalProperties": False}}},
]
SCHEMAS = {t["function"]["name"]: t["function"]["parameters"] for t in TOOLS}
