import math
import re
from os import system


class ExpressionError(ValueError):
    """Raised when a numeric expression is invalid or unsupported."""
_TOKEN_RE = re.compile(
    r"\s*(?:(?P<number>(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)"
    r"|(?P<name>[A-Za-z_]+|π)"
    r"|(?P<operator>\*\*|[+\-*/^(),]))"
)
def _nth_root(value, degree):
    if degree == 0:
        raise ExpressionError("A root degree cannot be zero.")

    # Python would make a negative base with a fractional exponent complex.
    # Keep all calculator results real and support negative odd roots explicitly.
    if value < 0:
        rounded_degree = round(degree)
        if not math.isclose(degree, rounded_degree) or rounded_degree % 2 == 0:
            raise ExpressionError("A negative number only has a real odd root.")
        return -((-value) ** (1 / rounded_degree))
    return value ** (1 / degree)
class _ExpressionParser:
    """Parser for a deliberately small and safe numeric-expression language."""

    def __init__(self, expression):
        self.tokens = self._tokenize(expression)
        self.position = 0

    @staticmethod
    def _tokenize(expression):
        tokens = []
        position = 0
        while position < len(expression):
            match = _TOKEN_RE.match(expression, position)
            if not match:
                raise ExpressionError(
                    f"Unexpected character {expression[position]!r} at position {position + 1}."
                )
            kind = "number" if match.group("number") else "name" if match.group("name") else "operator"
            value = match.group(kind)
            if value == "**":
                value = "^"
            tokens.append((kind, value))
            position = match.end()

        if not tokens:
            raise ExpressionError("Please enter a number or expression.")
        tokens.append(("end", ""))
        return tokens

    def current(self):
        return self.tokens[self.position]

    def accept(self, value):
        if self.current()[1] == value:
            self.position += 1
            return True
        return False

    def expect(self, value):
        if not self.accept(value):
            found = self.current()[1] or "end of input"
            raise ExpressionError(f"Expected {value!r}, but found {found!r}.")

    def parse(self):
        try:
            result = self.parse_expression()
        except (OverflowError, ZeroDivisionError) as error:
            raise ExpressionError(str(error)) from error

        if self.current()[0] != "end":
            raise ExpressionError(f"Unexpected {self.current()[1]!r}.")
        if isinstance(result, complex) or not math.isfinite(result):
            raise ExpressionError("The expression must produce a finite real number.")
        return result

    def parse_expression(self):
        value = self.parse_term()
        while self.current()[1] in ("+", "-"):
            operator = self.current()[1]
            self.position += 1
            right = self.parse_term()
            value = value + right if operator == "+" else value - right
        return value

    def parse_term(self):
        value = self.parse_unary()
        while True:
            operator = self.current()[1]
            if operator in ("*", "/"):
                self.position += 1
                right = self.parse_unary()
                value = value * right if operator == "*" else value / right
            elif self.current()[0] in ("number", "name") or operator == "(":
                # Adjacent values imply multiplication: 2pi, 2sqrt(pi), (1/2)(3).
                value *= self.parse_unary()
            else:
                break
        return value

    def parse_unary(self):
        if self.accept("+"):
            return self.parse_unary()
        if self.accept("-"):
            return -self.parse_unary()
        return self.parse_power()

    def parse_power(self):
        value = self.parse_primary()
        if self.accept("^"):
            # Calling parse_unary makes powers right-associative and permits 2^-3.
            value **= self.parse_unary()
        return value

    def parse_primary(self):
        kind, value = self.current()
        if kind == "number":
            self.position += 1
            return float(value)

        if kind == "name":
            self.position += 1
            name = value.lower()
            if name in ("pi", "π"):
                return math.pi
            if name == "e":
                return math.e
            if name == "sqrt":
                self.expect("(")
                argument = self.parse_expression()
                self.expect(")")
                if argument < 0:
                    raise ExpressionError("sqrt() requires a non-negative number.")
                return math.sqrt(argument)
            if name == "root":
                self.expect("(")
                argument = self.parse_expression()
                self.expect(",")
                degree = self.parse_expression()
                self.expect(")")
                return _nth_root(argument, degree)
            raise ExpressionError(f"Unknown name {value!r}.")

        if self.accept("("):
            value = self.parse_expression()
            self.expect(")")
            return value

        found = value or "end of input"
        raise ExpressionError(f"Expected a number, constant, or function; found {found!r}.")
def parse_number(expression):
    """Convert a supported numeric expression to a real floating-point number."""
    return _ExpressionParser(expression.strip()).parse()
def expression_input(prompt):
    while True:
        expression = input(prompt).strip()
        try:
            return parse_number(expression)
        except ExpressionError as error:
            print(f"Invalid expression: {error}")
def print_number_syntax():
    print("You may use ^ or **, /, sqrt(x), root(x, n), pi, and e.")
    print("Multiplication can be explicit or implicit: 2*pi or 2pi.\n")
def poly_deg_input():
    system("cls||clear")
    poly_degree = input("Enter the polynomial degree: ").strip()
    while poly_degree.isdigit()==False:
        system("cls||clear")
        poly_degree = input("Enter the polynomial degree IN THE NATURAL: ").strip()
    return int(poly_degree)
def poly_coeff_input(nth_degree):
    system("cls||clear")
    print_number_syntax()
    return expression_input(
        f"Enter the {nth_degree}th coefficient (x^{nth_degree}): "
    )
def poly_eq_input(poly_degree):
    return [poly_coeff_input(poly_degree-i) for i in range(poly_degree+1)]
def get_limit():
    system("cls||clear")
    print_number_syntax()
    return expression_input("Input x->")
def eval_poly(x,poly):
    sum_pol = 0
    for i in range(len(poly)):
        sum_pol += (x**(len(poly)-1-i))*poly[i]
    return sum_pol
def poly_division(x,poly):
    copy_poly = poly.copy()
    result_poly = [0]*(len(poly)-1)
    for i in range(len(poly)-1):
        result_poly[i] = copy_poly[i]
        copy_poly[i+1] -= result_poly[i]*(-x)
    return result_poly
def calc_delta(x,poly):
    poly_at_x = eval_poly(x,poly)
    zero_poly = poly.copy()
    zero_poly[-1] -= poly_at_x
    result_poly = poly_division(x,zero_poly)
    system("cls||clear")
    print(f"You inputed {poly}->{poly_at_x} at x->{x}.")
    print(f"The resulting polynomial is {result_poly}.")
    delta = eval_poly(abs(x)+1,[abs(v) for v in result_poly])
    print(f"{abs(x)+1=},{[abs(v) for v in result_poly]=}")
    print(f"The delta = min{{1,epsilon/{delta}}}")
    return delta

def main():
    poly_degree = poly_deg_input()
    poly_eq = poly_eq_input(poly_degree)
    print(poly_eq)
    x = get_limit()
    calc_delta(x,poly_eq)

if __name__ == "__main__":
    main()
