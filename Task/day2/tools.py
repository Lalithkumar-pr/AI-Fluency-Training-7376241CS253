import ast
import operator

# Private data: deliberately not included in the ReAct question.
STUDY_TASKS = {
    "python": 40,
    "computer networks": 35,
    "sql": 30,
    "machine learning": 50,
}

def get_study_time(subject: str) -> str:
    value = STUDY_TASKS.get(subject.strip().lower())
    return str(value) if value is not None else f"Unknown subject: {subject}"

OPS = {ast.Add: operator.add, ast.Sub: operator.sub,
       ast.Mult: operator.mul, ast.Div: operator.truediv}

def evaluate(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        return OPS[type(node.op)](evaluate(node.left), evaluate(node.right))
    raise ValueError("Unsupported expression")

def calculator(expression: str) -> str:
    try:
        return str(evaluate(ast.parse(expression, mode="eval").body))
    except Exception as e:
        return f"Calculator error: {e}"

TOOL_FUNCTIONS = {"get_study_time": get_study_time, "calculator": calculator}

TOOLS = [
    {"type": "function", "function": {
        "name": "get_study_time",
        "description": "Look up private study time in minutes for one subject.",
        "parameters": {"type": "object",
                       "properties": {"subject": {"type": "string"}},
                       "required": ["subject"]}}},
    {"type": "function", "function": {
        "name": "calculator",
        "description": "Perform arithmetic using numbers, +, -, *, / and parentheses.",
        "parameters": {"type": "object",
                       "properties": {"expression": {"type": "string"}},
                       "required": ["expression"]}}},
]
