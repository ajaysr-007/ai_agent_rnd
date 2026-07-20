import ast
import operator

def calculate(expression: str) -> str:
    """Safely evaluate a mathematical expression without using raw eval()."""
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
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"Unsupported constant type: {type(node.value).__name__}")
        elif isinstance(node, ast.Num): 
            return node.n
        elif isinstance(node, ast.BinOp):
            left = eval_node(node.left)
            right = eval_node(node.right)
            if type(node.op) not in operators:
                raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
            return operators[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = eval_node(node.operand)
            if type(node.op) not in operators:
                raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
            return operators[type(node.op)](operand)
        else:
            raise ValueError(f"Unsupported syntax: {type(node).__name__}")

    try:
        tree = ast.parse(expression, mode='eval')
        result = eval_node(tree.body)
        return str(result)
    except ZeroDivisionError:
        return "Error: Division by zero"
    except Exception as e:
        return f"Error: {e}"

CALCULATOR_FUNCTIONS = {
    "calculate": calculate
}

CALCULATOR_TOOLS = [
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
