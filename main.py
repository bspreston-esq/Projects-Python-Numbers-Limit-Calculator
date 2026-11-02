#!/usr/bin/env python3
"""Estimate limits of one-variable expressions numerically."""
import argparse
import ast
import math
import operator

BIN_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
           ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod}
UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}
FUNCTIONS = {"sin": math.sin, "cos": math.cos, "tan": math.tan, "asin": math.asin,
             "acos": math.acos, "atan": math.atan, "sqrt": math.sqrt,
             "log": math.log, "ln": math.log, "exp": math.exp, "abs": abs,
             "floor": math.floor, "ceil": math.ceil}
CONSTANTS = {"pi": math.pi, "e": math.e}

class LimitError(Exception):
    pass

def compile_expression(expression: str):
    """Turn a string into f(x), rejecting anything outside the whitelist."""
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise LimitError(f"syntax error: {exc.msg}") from exc

    def walk(node, x):
        if isinstance(node, ast.Expression):
            return walk(node.body, x)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.Name):
            if node.id == "x":
                return x
            if node.id in CONSTANTS:
                return CONSTANTS[node.id]
            raise LimitError(f"unknown name '{node.id}'")
        if isinstance(node, ast.BinOp) and type(node.op) in BIN_OPS:
            return BIN_OPS[type(node.op)](walk(node.left, x), walk(node.right, x))
        if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY_OPS:
            return UNARY_OPS[type(node.op)](walk(node.operand, x))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id not in FUNCTIONS:
                raise LimitError(f"unknown function '{node.func.id}'")
            return FUNCTIONS[node.func.id](*[walk(arg, x) for arg in node.args])
        raise LimitError(f"unsupported syntax: {type(node).__name__}")

    def f(x):
        try:
            return walk(tree, x)
        except ZeroDivisionError:
            return float("nan")
        except (ValueError, OverflowError):
            return float("nan")
    return f

def estimate(f, target: float, side: str = "both"):
    """Return (value, note) estimating the limit from the requested side(s)."""
    if target in (float("inf"), float("-inf")):
        sign = 1 if target > 0 else -1
        values = [f(sign * 10 ** k) for k in range(1, 9)]
        return _conclude(values, "at infinity")

    def sample(direction):
        values = []
        for k in range(2, 9):
            h = 10.0 ** -k
            value = f(target + direction * h)
            if not math.isnan(value):
                values.append(value)
        return values

    if side == "left":
        return _conclude(sample(-1), "from the left")
    if side == "right":
        return _conclude(sample(+1), "from the right")
    left, right = sample(-1), sample(+1)
    left_value, _ = _conclude(left, "from the left")
    right_value, _ = _conclude(right, "from the right")
    if left_value is None or right_value is None:
        return None, "one-sided limit does not exist"
    if abs(left_value - right_value) > 1e-4 * max(1.0, abs(left_value)):
        return None, f"left ({left_value:.6g}) and right ({right_value:.6g}) disagree"
    return (left_value + right_value) / 2, "two-sided"

def _conclude(values, where: str):
    values = [v for v in values if not math.isnan(v) and not math.isinf(v)]
    if not values:
        return None, f"no finite values {where}"
    if len(values) >= 4 and all(abs(v) > 1e6 for v in values):
        return math.copysign(float("inf"), values[-1]), f"diverges to infinity {where}"
    tail = values[-4:]
    spread = max(tail) - min(tail)
    scale = max(1.0, max(abs(v) for v in tail))
    if spread > 1e-3 * scale:
        return None, f"not converging {where}"
    return sum(tail) / len(tail), where

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--function", default="(x^2-4)/(x-2)")
    parser.add_argument("--at", default="2", help="limit point, or inf/-inf")
    parser.add_argument("--side", choices=["both", "left", "right"], default="both")
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()

    if args.demo:
        cases = [("(x**2 - 4)/(x - 2)", "2"), ("sin(x)/x", "0"),
                 ("(1 + 1/x)**x", "inf"), ("1/x", "0")]
        for expression, target in cases:
            f = compile_expression(expression)
            value, note = estimate(f, float(target), "both")
            shown = "does not exist" if value is None else f"{value:.6g}"
            print(f"lim x->{target:<4} {expression:<20} = {shown:<14} [{note}]")
        return

    f = compile_expression(args.function.replace("^", "**"))
    try:
        target = float(args.at)
    except ValueError:
        raise SystemExit("limit point must be a number, inf, or -inf")
    value, note = estimate(f, target, args.side)
    print("does not exist" if value is None else f"{value:.10g}", f"({note})")

if __name__ == "__main__":
    main()
