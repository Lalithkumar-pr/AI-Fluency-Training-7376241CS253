"""Day 6 task tools: campus event planning, with strict schemas."""
import ast
import operator

VENUE_CAPACITY = {
    "lecture_hall": 180,
    "seminar_room": 45,
    "computer_lab": 60,
}
REFRESHMENT_PRICE = {
    "water_snack": 35,
    "tea_snack": 55,
    "lunch_box": 120,
}

def get_venue_capacity(venue_type: str) -> str:
    """Return the maximum number of people for a supported campus venue."""
    key = venue_type.strip().lower()
    capacity = VENUE_CAPACITY.get(key)
    if capacity is None:
        return f"Unknown venue type: {venue_type}. Valid types: {', '.join(VENUE_CAPACITY)}"
    return str(capacity)

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
}

def _evaluate(node):
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_evaluate(node.left), _evaluate(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_evaluate(node.operand))
    raise ValueError("Unsupported expression")

def safe_calculator(expression: str) -> str:
    """Evaluate arithmetic without Python eval()."""
    try:
        return str(_evaluate(ast.parse(expression, mode="eval").body))
    except Exception as error:
        return f"Calculator error: {error}. Use only numbers and + - * / and parentheses."

def estimate_refreshment_cost(attendees: int, refreshment_type: str) -> str:
    """Estimate the total refreshment cost in rupees for the requested attendance."""
    if attendees < 0:
        return "Attendee count cannot be negative."
    key = refreshment_type.strip().lower()
    price = REFRESHMENT_PRICE.get(key)
    if price is None:
        return f"Unknown refreshment type: {refreshment_type}. Valid types: {', '.join(REFRESHMENT_PRICE)}"
    return str(price * attendees)

TOOL_FUNCTIONS = {
    "get_venue_capacity": get_venue_capacity,
    "estimate_refreshment_cost": estimate_refreshment_cost,
}

TOOLS = [
    {"type": "function", "function": {
        "name": "get_venue_capacity",
        "description": "Look up capacity for one campus venue. Valid venue_type values: lecture_hall, seminar_room, computer_lab. Returns a number.",
        "parameters": {
            "type": "object",
            "properties": {
                "venue_type": {"type": "string", "enum": ["lecture_hall", "seminar_room", "computer_lab"],
                               "description": "Campus venue category."}
            },
            "required": ["venue_type"],
            "additionalProperties": False,
        },
    }},
    {"type": "function", "function": {
        "name": "estimate_refreshment_cost",
        "description": "Estimate total refreshments cost in rupees. Valid refreshment_type values: water_snack, tea_snack, lunch_box. One attendee receives one selected package.",
        "parameters": {
            "type": "object",
            "properties": {
                "attendees": {"type": "integer", "description": "Number of attendees; zero or greater."},
                "refreshment_type": {"type": "string", "enum": ["water_snack", "tea_snack", "lunch_box"],
                                     "description": "Refreshment package."}
            },
            "required": ["attendees", "refreshment_type"],
            "additionalProperties": False,
        },
    }},
]
SCHEMAS = {tool["function"]["name"]: tool["function"]["parameters"] for tool in TOOLS}
