import ast
import operator
from config import COURSE_FEES

def get_course_fee(course_code: str) -> str:
    fee = COURSE_FEES.get(course_code.strip().upper())
    return str(fee) if fee is not None else f"Unknown course code: {course_code}"

OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.USub: operator.neg
}

def evaluate(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        return OPS[type(node.op)](evaluate(node.left), evaluate(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
        return OPS[type(node.op)](evaluate(node.operand))
    raise ValueError("Unsupported expression")

def calculator(expression: str) -> str:
    try:
        return str(evaluate(ast.parse(expression, mode="eval").body))
    except Exception as exc:
        return f"Calculator error: {exc}"

TOOL_FUNCTIONS = {
    "get_course_fee": get_course_fee,
    "calculator": calculator,
}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_course_fee",
            "description": "Get the fee in rupees for one course code.",
            "parameters": {
                "type": "object",
                "properties": {"course_code": {"type": "string"}},
                "required": ["course_code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Calculate an arithmetic expression using numbers and + - * / brackets.",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"],
            },
        },
    },
]
