#!/usr/bin/env python3
"""
Flow — a tiny language with no variables, only pipes and transformations.

Computation is a river. You never name the water; you only shape where it goes.
"""

import re
import sys
import readline  # noqa: F401 — enables arrow-key support in input()

# ─────────────────────────────────────────────
# Tokens
# ─────────────────────────────────────────────

class TokenKind:
    NUMBER   = "NUMBER"
    STRING   = "STRING"
    IDENT    = "IDENT"
    PIPE     = "PIPE"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    COMMA    = "COMMA"
    DOTDOT   = "DOTDOT"
    PLUS     = "PLUS"
    MINUS    = "MINUS"
    STAR     = "STAR"
    SLASH    = "SLASH"
    PERCENT  = "PERCENT"
    LPAREN   = "LPAREN"
    RPAREN   = "RPAREN"
    EOF      = "EOF"

class Token:
    __slots__ = ("kind", "value", "pos")
    def __init__(self, kind, value, pos=0):
        self.kind = kind
        self.value = value
        self.pos = pos
    def __repr__(self):
        return f"Token({self.kind}, {self.value!r})"

# ─────────────────────────────────────────────
# Lexer
# ─────────────────────────────────────────────

_PATTERNS = [
    (r"\s+",                          None),          # whitespace (skip)
    (r"#[^\n]*",                      None),          # comments
    (r"\|>",                          TokenKind.PIPE),
    (r"\.\.",                         TokenKind.DOTDOT),
    (r"-?\d+(\.\d+)?",               TokenKind.NUMBER),
    (r'"([^"\\]|\\.)*"',             TokenKind.STRING),
    (r"'([^'\\]|\\.)*'",             TokenKind.STRING),
    (r"[A-Za-z_][A-Za-z0-9_]*",      TokenKind.IDENT),
    (r"\[",                           TokenKind.LBRACKET),
    (r"\]",                           TokenKind.RBRACKET),
    (r",",                            TokenKind.COMMA),
    (r"\+",                           TokenKind.PLUS),
    (r"-",                            TokenKind.MINUS),
    (r"\*",                           TokenKind.STAR),
    (r"/",                            TokenKind.SLASH),
    (r"%",                            TokenKind.PERCENT),
    (r"\(",                           TokenKind.LPAREN),
    (r"\)",                           TokenKind.RPAREN),
]

_COMPILED = [(re.compile(p), k) for p, k in _PATTERNS]

def lex(source: str) -> list[Token]:
    tokens = []
    pos = 0
    while pos < len(source):
        for regex, kind in _COMPILED:
            m = regex.match(source, pos)
            if m:
                if kind is not None:
                    value = m.group(0)
                    if kind == TokenKind.NUMBER:
                        value = float(value) if "." in value else int(value)
                    elif kind == TokenKind.STRING:
                        value = value[1:-1].replace('\\"', '"').replace("\\'", "'")
                    tokens.append(Token(kind, value, pos))
                pos = m.end()
                break
        else:
            raise SyntaxError(f"Unexpected character {source[pos]!r} at position {pos}")
    tokens.append(Token(TokenKind.EOF, None, pos))
    return tokens

# ─────────────────────────────────────────────
# AST
# ─────────────────────────────────────────────

class NumberLit:
    __slots__ = ("value",)
    def __init__(self, value): self.value = value
    def __repr__(self): return f"NumberLit({self.value})"

class StringLit:
    __slots__ = ("value",)
    def __init__(self, value): self.value = value
    def __repr__(self): return f"StringLit({self.value!r})"

class ListLit:
    __slots__ = ("elements",)
    def __init__(self, elements): self.elements = elements
    def __repr__(self): return f"ListLit({self.elements})"

class RangeLit:
    __slots__ = ("start", "end")
    def __init__(self, start, end): self.start = start; self.end = end
    def __repr__(self): return f"RangeLit({self.start}..{self.end})"

class Ident:
    __slots__ = ("name",)
    def __init__(self, name): self.name = name
    def __repr__(self): return f"Ident({self.name})"

class OpRef:
    """A reference to an operator used as a function: +, -, *, /, %"""
    __slots__ = ("op",)
    def __init__(self, op): self.op = op
    def __repr__(self): return f"OpRef({self.op})"

class Transform:
    __slots__ = ("name", "args")
    def __init__(self, name, args=None): self.name = name; self.args = args or []
    def __repr__(self): return f"Transform({self.name}, {self.args})"

class Pipeline:
    __slots__ = ("source", "steps")
    def __init__(self, source, steps): self.source = source; self.steps = steps
    def __repr__(self): return f"Pipeline({self.source}, {self.steps})"

class Group:
    """Parenthesized sub-expression."""
    __slots__ = ("expr",)
    def __init__(self, expr): self.expr = expr
    def __repr__(self): return f"Group({self.expr})"

# ─────────────────────────────────────────────
# Parser
# ─────────────────────────────────────────────

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def advance(self) -> Token:
        t = self.tokens[self.pos]
        self.pos += 1
        return t

    def expect(self, kind) -> Token:
        t = self.advance()
        if t.kind != kind:
            raise SyntaxError(f"Expected {kind}, got {t.kind} ({t.value!r}) at pos {t.pos}")
        return t

    def parse(self):
        node = self.parse_pipeline()
        if self.peek().kind != TokenKind.EOF:
            raise SyntaxError(f"Unexpected token {self.peek().value!r} at pos {self.peek().pos}")
        return node

    def parse_pipeline(self):
        source = self.parse_atom()
        steps = []
        while self.peek().kind == TokenKind.PIPE:
            self.advance()  # consume |>
            steps.append(self.parse_transform())
        if steps:
            return Pipeline(source, steps)
        return source

    def parse_transform(self):
        """Parse a transform: name [arg1 arg2 ...]"""
        tok = self.peek()
        if tok.kind != TokenKind.IDENT:
            raise SyntaxError(f"Expected transform name, got {tok.kind} at pos {tok.pos}")
        name = self.advance().value
        args = []
        # Collect arguments until we hit |>, EOF, or )
        while self.peek().kind not in (TokenKind.PIPE, TokenKind.EOF, TokenKind.RPAREN):
            args.append(self.parse_transform_arg())
        return Transform(name, args)

    def parse_transform_arg(self):
        """Parse a single argument to a transform."""
        tok = self.peek()
        if tok.kind == TokenKind.NUMBER:
            self.advance()
            return NumberLit(tok.value)
        elif tok.kind == TokenKind.STRING:
            self.advance()
            return StringLit(tok.value)
        elif tok.kind == TokenKind.IDENT:
            self.advance()
            return Ident(tok.name if hasattr(tok, "name") else tok.value)
        elif tok.kind in (TokenKind.PLUS, TokenKind.MINUS, TokenKind.STAR,
                          TokenKind.SLASH, TokenKind.PERCENT):
            self.advance()
            return OpRef(tok.value)
        elif tok.kind == TokenKind.LBRACKET:
            return self.parse_list()
        elif tok.kind == TokenKind.LPAREN:
            return self.parse_group()
        else:
            raise SyntaxError(f"Unexpected {tok.kind} ({tok.value!r}) at pos {tok.pos}")

    def parse_atom(self):
        tok = self.peek()
        if tok.kind == TokenKind.NUMBER:
            self.advance()
            # Check for range: number .. number
            if self.peek().kind == TokenKind.DOTDOT:
                self.advance()
                end_tok = self.expect(TokenKind.NUMBER)
                return RangeLit(tok.value, end_tok.value)
            return NumberLit(tok.value)
        elif tok.kind == TokenKind.STRING:
            self.advance()
            return StringLit(tok.value)
        elif tok.kind == TokenKind.LBRACKET:
            return self.parse_list()
        elif tok.kind == TokenKind.LPAREN:
            return self.parse_group()
        elif tok.kind == TokenKind.IDENT:
            self.advance()
            return Ident(tok.value)
        else:
            raise SyntaxError(f"Unexpected {tok.kind} ({tok.value!r}) at pos {tok.pos}")

    def parse_list(self):
        self.expect(TokenKind.LBRACKET)
        elements = []
        if self.peek().kind != TokenKind.RBRACKET:
            elements.append(self.parse_pipeline())
            while self.peek().kind == TokenKind.COMMA:
                self.advance()
                elements.append(self.parse_pipeline())
        self.expect(TokenKind.RBRACKET)
        return ListLit(elements)

    def parse_group(self):
        self.expect(TokenKind.LPAREN)
        expr = self.parse_pipeline()
        self.expect(TokenKind.RPAREN)
        return Group(expr)

# ─────────────────────────────────────────────
# Evaluator
# ─────────────────────────────────────────────

# Operator functions
_OPS = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a / b if b != 0 else float("inf"),
    "%": lambda a, b: a % b,
}

# Built-in predicate / transform identifiers
_PREDICATES = {
    "even":     lambda x: x % 2 == 0,
    "odd":      lambda x: x % 2 != 0,
    "positive": lambda x: x > 0,
    "negative": lambda x: x < 0,
    "zero":     lambda x: x == 0,
}

_MAPPERS = {
    "uppercase": lambda x: x.upper() if isinstance(x, str) else x,
    "lowercase": lambda x: x.lower() if isinstance(x, str) else x,
    "trim":      lambda x: x.strip() if isinstance(x, str) else x,
    "abs":       lambda x: abs(x),
    "neg":       lambda x: -x,
    "double":    lambda x: x * 2,
    "square":    lambda x: x * x,
    "str":       lambda x: str(x),
    "int":       lambda x: int(x),
    "float":     lambda x: float(x),
    "len":       lambda x: len(x),
    "not":       lambda x: not x,
}


def evaluate(node):
    """Evaluate an AST node and return a Python value."""

    if isinstance(node, NumberLit):
        return node.value

    elif isinstance(node, StringLit):
        return node.value

    elif isinstance(node, ListLit):
        return [evaluate(e) for e in node.elements]

    elif isinstance(node, RangeLit):
        s, e = int(node.start), int(node.end)
        step = 1 if s <= e else -1
        return list(range(s, e + step, step))

    elif isinstance(node, Ident):
        # Bare identifiers evaluate to themselves (used as transform refs)
        if node.name in _PREDICATES:
            return _PREDICATES[node.name]
        if node.name in _MAPPERS:
            return _MAPPERS[node.name]
        if node.name == "true":
            return True
        if node.name == "false":
            return False
        raise NameError(f"Unknown identifier: {node.name}")

    elif isinstance(node, OpRef):
        return _OPS[node.op]

    elif isinstance(node, Group):
        return evaluate(node.expr)

    elif isinstance(node, Pipeline):
        value = evaluate(node.source)
        for step in node.steps:
            value = apply_transform(step, value)
        return value

    elif isinstance(node, Transform):
        # A bare transform at top level (shouldn't happen in normal use)
        raise SyntaxError(f"Transform {node.name!r} used without a source value")

    else:
        raise TypeError(f"Cannot evaluate {type(node).__name__}")


def apply_transform(transform: Transform, value):
    """Apply a transform step to a value."""
    name = transform.name
    args = [evaluate(a) for a in transform.args]

    # ── list transforms ──────────────────────

    if name == "map":
        fn = args[0]
        if callable(fn):
            return [fn(x) for x in value]
        raise TypeError(f"map expects a function, got {type(fn).__name__}")

    elif name == "filter":
        fn = args[0]
        if callable(fn):
            return [x for x in value if fn(x)]
        raise TypeError(f"filter expects a predicate, got {type(fn).__name__}")

    elif name == "fold":
        if len(args) < 2:
            raise TypeError("fold requires an operator and an initial value: fold + 0")
        fn, init = args[0], args[1]
        acc = init
        for x in value:
            acc = fn(acc, x)
        # Return int if the result is a whole number
        if isinstance(acc, float) and acc == int(acc):
            acc = int(acc)
        return acc

    elif name == "reduce":
        fn = args[0]
        it = iter(value)
        acc = next(it)
        for x in it:
            acc = fn(acc, x)
        if isinstance(acc, float) and acc == int(acc):
            acc = int(acc)
        return acc

    elif name == "take":
        n = int(args[0])
        return value[:n]

    elif name == "drop":
        n = int(args[0])
        return value[n:]

    elif name == "reverse":
        if isinstance(value, str):
            return value[::-1]
        return list(reversed(value))

    elif name == "sort":
        return sorted(value)

    elif name == "unique":
        seen = set()
        result = []
        for x in value:
            key = x
            if key not in seen:
                seen.add(key)
                result.append(x)
        return result

    elif name == "flatten":
        result = []
        for x in value:
            if isinstance(x, list):
                result.extend(x)
            else:
                result.append(x)
        return result

    elif name == "zip":
        other = args[0]
        return [list(pair) for pair in zip(value, other)]

    elif name == "enumerate":
        return [[i, x] for i, x in builtins_enumerate(value)]

    elif name == "first":
        return value[0] if value else None

    elif name == "last":
        return value[-1] if value else None

    elif name == "length":
        return len(value)

    elif name == "sum":
        return sum(value)

    elif name == "min":
        return min(value)

    elif name == "max":
        return max(value)

    elif name == "product":
        acc = 1
        for x in value:
            acc *= x
        return acc

    elif name == "any":
        fn = args[0] if args else None
        if fn and callable(fn):
            return any(fn(x) for x in value)
        return any(value)

    elif name == "all":
        fn = args[0] if args else None
        if fn and callable(fn):
            return all(fn(x) for x in value)
        return all(value)

    elif name == "count":
        if args:
            fn = args[0]
            return sum(1 for x in value if fn(x))
        return len(value)

    # ── string transforms ────────────────────

    elif name == "split":
        sep = args[0] if args else " "
        return value.split(sep)

    elif name == "join":
        sep = args[0] if args else ""
        return sep.join(str(x) for x in value)

    elif name == "chars":
        return list(value)

    elif name == "words":
        return value.split()

    elif name == "lines":
        return value.split("\n")

    elif name == "uppercase":
        return value.upper()

    elif name == "lowercase":
        return value.lower()

    elif name == "trim":
        return value.strip()

    elif name == "replace":
        if len(args) < 2:
            raise TypeError("replace needs two arguments: replace old new")
        return value.replace(args[0], args[1])

    elif name == "contains":
        needle = args[0]
        if isinstance(value, list):
            return needle in value
        return needle in value

    elif name == "startswith":
        return value.startswith(args[0])

    elif name == "endswith":
        return value.endswith(args[0])

    # ── type / display transforms ────────────

    elif name == "str":
        return str(value)

    elif name == "int":
        return int(value)

    elif name == "float":
        return float(value)

    elif name == "type":
        if isinstance(value, list):
            return "list"
        elif isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, bool):
            return "bool"
        return type(value).__name__

    elif name == "debug":
        print(f"  [debug] {format_value(value)}")
        return value

    # ── identity / passthrough for bare mapper names used as transforms ──

    elif name in _MAPPERS:
        fn = _MAPPERS[name]
        if isinstance(value, list):
            return [fn(x) for x in value]
        return fn(value)

    elif name in _PREDICATES:
        fn = _PREDICATES[name]
        if isinstance(value, list):
            return [x for x in value if fn(x)]
        return fn(value)

    else:
        raise NameError(f"Unknown transform: {name}")


# Avoid shadowing Python's enumerate
builtins_enumerate = enumerate

# ─────────────────────────────────────────────
# Pretty-printing
# ─────────────────────────────────────────────

def format_value(value) -> str:
    if isinstance(value, list):
        inner = ", ".join(format_value(x) for x in value)
        return f"[{inner}]"
    elif isinstance(value, str):
        return f'"{value}"'
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, float):
        return f"{value:g}"
    else:
        return str(value)

# ─────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────

def run(source: str):
    """Parse and evaluate a Flow expression, returning the result."""
    tokens = lex(source)
    ast = Parser(tokens).parse()
    return evaluate(ast)


def run_file(path: str):
    """Run a .flow file. Each non-blank, non-comment line is one expression."""
    with open(path) as f:
        source = f.read()

    for lineno, line in builtins_enumerate(source.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        try:
            result = run(stripped)
            print(f"  {format_value(result)}")
        except Exception as e:
            print(f"  error (line {lineno}): {e}")


def repl():
    """Interactive REPL."""
    print("Flow v0.1 — a language with no variables, only pipes.")
    print('Type an expression, or "quit" to exit.\n')

    while True:
        try:
            line = input("flow> ")
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped in ("quit", "exit"):
            print("Bye.")
            break

        try:
            result = run(stripped)
            print(f"  {format_value(result)}")
        except Exception as e:
            print(f"  error: {e}")

# ─────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────

def run_tests():
    """Built-in test suite. Returns (passed, failed) counts."""
    cases = [
        # Literals
        ("42",                                          42),
        ('"hello"',                                     "hello"),
        ("[1, 2, 3]",                                   [1, 2, 3]),
        ("1..5",                                        [1, 2, 3, 4, 5]),

        # List transforms
        ("[3, 1, 4, 1, 5, 9] |> unique",               [3, 1, 4, 5, 9]),
        ("[3, 1, 4, 1, 5, 9] |> unique |> sort",       [1, 3, 4, 5, 9]),
        ("[3, 1, 4] |> sort |> reverse",                [4, 3, 1]),
        ("[1, 2, 3, 4, 5] |> take 3",                  [1, 2, 3]),
        ("[1, 2, 3, 4, 5] |> drop 2",                  [3, 4, 5]),
        ("[1, 2, 3, 4, 5] |> filter even",             [2, 4]),
        ("[1, 2, 3, 4, 5] |> filter odd",              [1, 3, 5]),
        ("[1, 2, 3] |> map double",                    [2, 4, 6]),
        ("[1, 2, 3] |> map square",                    [1, 4, 9]),
        ("[1, 2, 3] |> fold + 0",                      6),
        ("[1, 2, 3] |> fold * 1",                      6),
        ("1..10 |> filter even |> fold + 0",            30),
        ("[1, 2, 3] |> sum",                            6),
        ("[5, 1, 3] |> min",                            1),
        ("[5, 1, 3] |> max",                            5),
        ("[1, 2, 3] |> length",                         3),
        ("[1, 2, 3] |> first",                          1),
        ("[1, 2, 3] |> last",                           3),
        ("[1, 2, 3] |> reduce +",                       6),
        ("[1, 2, 3, 4] |> product",                     24),
        ("[1, 2, 3] |> any even",                       True),
        ("[1, 3, 5] |> all odd",                        True),
        ("[1, 2, 3, 2, 1] |> count even",              2),

        # String transforms
        ('"hello world" |> uppercase',                  "HELLO WORLD"),
        ('"HELLO" |> lowercase',                        "hello"),
        ('"  hi  " |> trim',                            "hi"),
        ('"hello world" |> split " "',                  ["hello", "world"]),
        ('"hello" |> chars',                            ["h", "e", "l", "l", "o"]),
        ('"hello" |> reverse',                          "olleh"),
        ('"hello world" |> words',                      ["hello", "world"]),
        ('"foo-bar" |> replace "-" "_"',                "foo_bar"),
        ('"hello" |> contains "ell"',                   True),

        # Chained pipelines
        ('"hello world" |> split " " |> map uppercase |> join ", "',
                                                        "HELLO, WORLD"),
        ("[3, 1, 4, 1, 5, 9] |> unique |> sort |> reverse",
                                                        [9, 5, 4, 3, 1]),
        ("1..10 |> filter even |> map square",          [4, 16, 36, 64, 100]),
        ('1..5 |> map str |> join "-"',                 "1-2-3-4-5"),

        # Nested lists
        ("[[1, 2], [3, 4]] |> flatten",                 [1, 2, 3, 4]),

        # Type transforms
        ("42 |> type",                                  "int"),
        ('"hi" |> type',                                "string"),
        ("[1] |> type",                                 "list"),
    ]

    passed = failed = 0
    for expr, expected in cases:
        try:
            result = run(expr)
            if result == expected:
                passed += 1
            else:
                failed += 1
                print(f"  FAIL: {expr}")
                print(f"    expected {format_value(expected)}")
                print(f"    got      {format_value(result)}")
        except Exception as e:
            failed += 1
            print(f"  ERROR: {expr}")
            print(f"    {e}")

    total = passed + failed
    print(f"\n  {passed}/{total} tests passed.", end="")
    if failed:
        print(f" ({failed} failed)")
    else:
        print(" All green.")
    return passed, failed

# ─────────────────────────────────────────────
# CLI entry point
# ─────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        repl()
    elif sys.argv[1] == "--test":
        _, failed = run_tests()
        sys.exit(1 if failed else 0)
    elif sys.argv[1] == "--eval" or sys.argv[1] == "-e":
        if len(sys.argv) < 3:
            print("Usage: flow.py -e '<expression>'")
            sys.exit(1)
        result = run(sys.argv[2])
        print(format_value(result))
    elif sys.argv[1].endswith(".flow"):
        run_file(sys.argv[1])
    else:
        # Treat the whole argument as an expression
        result = run(" ".join(sys.argv[1:]))
        print(format_value(result))


if __name__ == "__main__":
    main()
