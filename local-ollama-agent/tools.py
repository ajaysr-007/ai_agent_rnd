import ast
import operator

def get_weather(city: str) -> str:
    """Get the current weather for a given city."""
    # TODO: Integrate with a real weather API (e.g. Open-Meteo, no key required) later
    # Example: response = requests.get(f"https://api.open-meteo.com/v1/forecast?...&city={city}")
    return f"{city}: 28°C, clear skies"

def calculate(expression: str) -> str:
    """Safely evaluate a mathematical expression without using raw eval()."""
    # Define allowed operators
    operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos
    }

    def eval_node(node):
        # Numeric literals
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"Unsupported constant type: {type(node.value).__name__}")
        elif isinstance(node, ast.Num): # for compatibility with older Python versions
            return node.n
        # Binary operations (e.g. 5 + 3)
        elif isinstance(node, ast.BinOp):
            left = eval_node(node.left)
            right = eval_node(node.right)
            if type(node.op) not in operators:
                raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
            return operators[type(node.op)](left, right)
        # Unary operations (e.g. -5)
        elif isinstance(node, ast.UnaryOp):
            operand = eval_node(node.operand)
            if type(node.op) not in operators:
                raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
            return operators[type(node.op)](operand)
        else:
            raise ValueError(f"Unsupported syntax: {type(node).__name__}")

    try:
        # Parse the expression. mode='eval' ensures it's a single expression and not a statement block.
        tree = ast.parse(expression, mode='eval')
        result = eval_node(tree.body)
        return str(result)
    except ZeroDivisionError:
        return "Error: Division by zero"
    except Exception as e:
        return f"Error: {e}"

AVAILABLE_FUNCTIONS = {
    "get_weather": get_weather,
    "calculate": calculate
}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a given city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The name of the city, e.g. 'San Francisco', 'London'"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Safely evaluate a mathematical expression. Supports basic arithmetic operators (+, -, *, /, **, %, parentheses).",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The mathematical expression to evaluate, e.g. '(5 + 3) * 2'"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]
