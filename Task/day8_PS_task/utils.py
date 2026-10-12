"""Dependency-free deterministic business rules and safe arithmetic."""
import ast
import operator

COURSE_FEES = {"CS101": 12000, "AI202": 18000}
LATE_FEE_PER_DAY = 100
MAX_LATE_FEE = 2000
CONDONATION_FEE_PER_COURSE = 500

_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
}
_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def safe_calculate(expression: str):
    """Evaluate only numeric constants and explicitly allowed arithmetic AST nodes."""
    try:
        tree = ast.parse(expression, mode="eval")
    except (SyntaxError, ValueError) as exc:
        raise ValueError("Invalid arithmetic expression.") from exc

    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)) and right == 0:
                raise ValueError("Division by zero is not allowed.")
            return _BIN_OPS[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
            return _UNARY_OPS[type(node.op)](visit(node.operand))
        raise ValueError("Only basic arithmetic is allowed; names and function calls are forbidden.")

    result = visit(tree)
    if abs(result) > 10**15:
        raise ValueError("Result is too large.")
    return result


def get_course_fee(course_code: str):
    code = course_code.strip().upper()
    if code not in COURSE_FEES:
        return None
    return COURSE_FEES[code]


def late_fee(days_late: int) -> int:
    if isinstance(days_late, bool) or not isinstance(days_late, int) or days_late < 0:
        raise ValueError("Days late must be a non-negative integer.")
    return min(days_late * LATE_FEE_PER_DAY, MAX_LATE_FEE)


def check_exam_eligibility(attendance: float) -> dict:
    try:
        value = float(attendance)
    except (TypeError, ValueError) as exc:
        raise ValueError("Attendance must be a number from 0 to 100.") from exc
    if not 0 <= value <= 100:
        raise ValueError("Attendance must be between 0 and 100.")
    if value >= 75:
        return {"attendance": value, "status": "eligible", "message": "Eligible under the attendance rule; other institutional requirements may apply.", "condonation_fee_per_course": 0}
    if value >= 65:
        return {"attendance": value, "status": "condonation_required", "message": "May apply for condonation; approval is not automatic.", "condonation_fee_per_course": CONDONATION_FEE_PER_COURSE}
    return {"attendance": value, "status": "not_eligible", "message": "Not eligible under these attendance rules.", "condonation_fee_per_course": 0}
