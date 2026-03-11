#!/usr/bin/env python3
"""Ask — a language where types are questions and values are answers."""

import re
import sys
import operator

# ---------------------------------------------------------------------------
# Core: Answered values
# ---------------------------------------------------------------------------

BUILTIN_QUESTIONS = {
    "how many?":      int,
    "how much?":      float,
    "what?":          str,
    "true or false?": bool,
    "what list?":     list,
    "which one?":     str,   # enums stored as strings
}

class Answer:
    """A value that knows what question it answers."""
    __slots__ = ("value", "question")

    def __init__(self, value, question=None):
        self.value = value
        self.question = question or infer_question(value)

    def __repr__(self):
        return f'{self.value!r}  (answers "{self.question}")'

    def __eq__(self, other):
        if isinstance(other, Answer):
            return self.value == other.value and self.question == other.question
        return NotImplemented

    def __hash__(self):
        return hash((type(self.value), self.value, self.question))


def infer_question(value):
    if isinstance(value, bool):
        return "true or false?"
    if isinstance(value, int):
        return "how many?"
    if isinstance(value, float):
        return "how much?"
    if isinstance(value, str):
        return "what?"
    if isinstance(value, list):
        return "what list?"
    return "what?"


def check_question(answer, expected_q, context=""):
    if answer.question != expected_q:
        raise AskTypeError(expected_q, answer.question, context)


class AskTypeError(Exception):
    def __init__(self, expected, got, context=""):
        self.expected = expected
        self.got = got
        ctx = f" (in {context})" if context else ""
        super().__init__(
            f"Expected an answer to '{expected}' but got an answer to '{got}'{ctx}"
        )


class AskRuntimeError(Exception):
    pass

# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------

TOKEN_RE = re.compile(r"""
    (?P<STRING>"[^"]*")       |
    (?P<NUMBER>\d+\.\d+)      |
    (?P<INT>\d+)              |
    (?P<ARROW>->)             |
    (?P<ASSIGN>=(?!=))         |
    (?P<CMP>[<>=!]=|[<>])     |
    (?P<OP>[+\-*/%])          |
    (?P<LPAREN>\()            |
    (?P<RPAREN>\))            |
    (?P<LBRACKET>\[)          |
    (?P<RBRACKET>\])          |
    (?P<COMMA>,)              |
    (?P<COLON>:)              |
    (?P<IDENT>[A-Za-z_]\w*)   |
    (?P<WS>\s+)               |
    (?P<COMMENT>\#.*)
""", re.VERBOSE)

KEYWORDS = {"define", "if", "else", "repeat", "question", "true", "false", "and", "or", "not", "return"}

def tokenize(source):
    tokens = []
    for m in TOKEN_RE.finditer(source):
        kind = m.lastgroup
        val = m.group()
        if kind in ("WS", "COMMENT"):
            continue
        if kind == "IDENT" and val in KEYWORDS:
            kind = val.upper()
        if kind == "IDENT" and val == "true":
            kind = "TRUE"
        if kind == "IDENT" and val == "false":
            kind = "FALSE"
        tokens.append((kind, val))
    return tokens

# ---------------------------------------------------------------------------
# AST nodes
# ---------------------------------------------------------------------------

class Num:
    def __init__(self, v): self.value = v
class Flt:
    def __init__(self, v): self.value = v
class Str:
    def __init__(self, v): self.value = v
class Bool:
    def __init__(self, v): self.value = v
class Var:
    def __init__(self, n): self.name = n
class BinOp:
    def __init__(self, l, o, r): self.left, self.op, self.right = l, o, r
class UnaryOp:
    def __init__(self, o, e): self.op, self.expr = o, e
class Call:
    def __init__(self, n, a): self.name, self.args = n, a
class IfExpr:
    def __init__(self, c, t, e): self.cond, self.then, self.else_ = c, t, e
class ListLit:
    def __init__(self, elems): self.elems = elems
class FuncDef:
    def __init__(self, n, p, r, b): self.name, self.params, self.ret_q, self.body = n, p, r, b
class QuestionDef:
    def __init__(self, q, b): self.question, self.base = q, b
class RepeatExpr:
    def __init__(self, c, b): self.count, self.body = c, b

# ---------------------------------------------------------------------------
# Parser (recursive descent)
# ---------------------------------------------------------------------------

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self, offset=0):
        p = self.pos + offset
        return self.tokens[p] if p < len(self.tokens) else ("EOF", "")

    def eat(self, kind=None):
        tok = self.peek()
        if kind and tok[0] != kind:
            raise SyntaxError(f"Expected {kind}, got {tok}")
        self.pos += 1
        return tok

    def at_end(self):
        return self.pos >= len(self.tokens)

    # -- top-level --
    def parse_program(self):
        stmts = []
        while not self.at_end():
            stmts.append(self.parse_statement())
        return stmts

    def parse_statement(self):
        if self.peek()[0] == "DEFINE":
            return self.parse_funcdef()
        if self.peek()[0] == "QUESTION":
            return self.parse_questiondef()
        return self.parse_expr()

    def parse_funcdef(self):
        self.eat("DEFINE")
        name = self.eat("IDENT")[1]
        self.eat("LPAREN")
        params = []
        while self.peek()[0] != "RPAREN":
            pname = self.eat("IDENT")[1]
            self.eat("COLON")
            pq = self.eat("STRING")[1].strip('"')
            params.append((pname, pq))
            if self.peek()[0] == "COMMA":
                self.eat("COMMA")
        self.eat("RPAREN")
        ret_q = None
        if self.peek()[0] == "ARROW":
            self.eat("ARROW")
            ret_q = self.eat("STRING")[1].strip('"')
        self.eat("COLON")
        body = self.parse_expr()
        return FuncDef(name, params, ret_q, body)

    def parse_questiondef(self):
        self.eat("QUESTION")
        q = self.eat("STRING")[1].strip('"')
        # '=' is tokenized as CMP (since == is CMP, bare = isn't matched)
        # We need to handle it — add '=' to the token regex or just eat CMP
        self.eat("ASSIGN")
        base = self.eat("IDENT")[1]
        return QuestionDef(q, base)

    def parse_expr(self):
        return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while self.peek()[0] == "OR":
            self.eat()
            left = BinOp(left, "or", self.parse_and())
        return left

    def parse_and(self):
        left = self.parse_not()
        while self.peek()[0] == "AND":
            self.eat()
            left = BinOp(left, "and", self.parse_not())
        return left

    def parse_not(self):
        if self.peek()[0] == "NOT":
            self.eat()
            return UnaryOp("not", self.parse_not())
        return self.parse_comparison()

    def parse_comparison(self):
        left = self.parse_add()
        if self.peek()[0] == "CMP":
            op = self.eat()[1]
            right = self.parse_add()
            left = BinOp(left, op, right)
        return left

    def parse_add(self):
        left = self.parse_mul()
        while self.peek()[0] == "OP" and self.peek()[1] in ("+", "-"):
            op = self.eat()[1]
            left = BinOp(left, op, self.parse_mul())
        return left

    def parse_mul(self):
        left = self.parse_unary()
        while self.peek()[0] == "OP" and self.peek()[1] in ("*", "/", "%"):
            op = self.eat()[1]
            left = BinOp(left, op, self.parse_unary())
        return left

    def parse_unary(self):
        if self.peek()[0] == "OP" and self.peek()[1] == "-":
            self.eat()
            return UnaryOp("-", self.parse_atom())
        return self.parse_atom()

    def parse_atom(self):
        tok = self.peek()
        if tok[0] == "INT":
            self.eat()
            return Num(int(tok[1]))
        if tok[0] == "NUMBER":
            self.eat()
            return Flt(float(tok[1]))
        if tok[0] == "STRING":
            self.eat()
            return Str(tok[1][1:-1])
        if tok[0] == "TRUE":
            self.eat()
            return Bool(True)
        if tok[0] == "FALSE":
            self.eat()
            return Bool(False)
        if tok[0] == "LBRACKET":
            return self.parse_list()
        if tok[0] == "IF":
            return self.parse_if()
        if tok[0] == "REPEAT":
            return self.parse_repeat()
        if tok[0] == "IDENT":
            name = self.eat()[1]
            if self.peek()[0] == "LPAREN":
                return self.parse_call(name)
            return Var(name)
        if tok[0] == "LPAREN":
            self.eat()
            expr = self.parse_expr()
            self.eat("RPAREN")
            return expr
        raise SyntaxError(f"Unexpected token: {tok}")

    def parse_call(self, name):
        self.eat("LPAREN")
        args = []
        while self.peek()[0] != "RPAREN":
            args.append(self.parse_expr())
            if self.peek()[0] == "COMMA":
                self.eat("COMMA")
        self.eat("RPAREN")
        return Call(name, args)

    def parse_if(self):
        self.eat("IF")
        cond = self.parse_expr()
        self.eat("COLON")
        then = self.parse_expr()
        self.eat("ELSE")
        self.eat("COLON")
        else_ = self.parse_expr()
        return IfExpr(cond, then, else_)

    def parse_repeat(self):
        self.eat("REPEAT")
        self.eat("LPAREN")
        count = self.parse_expr()
        self.eat("COMMA")
        body = self.parse_expr()
        self.eat("RPAREN")
        return RepeatExpr(count, body)

    def parse_list(self):
        self.eat("LBRACKET")
        elems = []
        while self.peek()[0] != "RBRACKET":
            elems.append(self.parse_expr())
            if self.peek()[0] == "COMMA":
                self.eat("COMMA")
        self.eat("RBRACKET")
        return ListLit(elems)

# ---------------------------------------------------------------------------
# Evaluator
# ---------------------------------------------------------------------------

class Env:
    def __init__(self, parent=None):
        self.bindings = {}
        self.parent = parent
        self.custom_questions = {}  # question_text -> base_question

    def get(self, name):
        if name in self.bindings:
            return self.bindings[name]
        if self.parent:
            return self.parent.get(name)
        raise AskRuntimeError(f"Unknown name: '{name}'")

    def set(self, name, val):
        self.bindings[name] = val

    def resolve_question(self, q):
        if q in BUILTIN_QUESTIONS:
            return q
        if q in self.custom_questions:
            return q
        if self.parent:
            return self.parent.resolve_question(q)
        raise AskRuntimeError(f"Unknown question type: '{q}'")

    def base_question(self, q):
        if q in self.custom_questions:
            return self.custom_questions[q]
        if self.parent:
            return self.parent.base_question(q)
        return q

BASE_MAP = {"number": "how many?", "float": "how much?", "string": "what?",
            "boolean": "true or false?", "list": "what list?"}

OPS = {
    "+": operator.add, "-": operator.sub, "*": operator.mul,
    "/": operator.truediv, "%": operator.mod,
    "==": operator.eq, "!=": operator.ne,
    "<": operator.lt, ">": operator.gt,
    "<=": operator.le, ">=": operator.ge,
}

def builtin_len(args, env):
    if len(args) != 1:
        raise AskRuntimeError("len() expects 1 argument")
    a = evaluate(args[0], env)
    if isinstance(a.value, (str, list)):
        return Answer(len(a.value), "how many?")
    raise AskTypeError("what? or what list?", a.question, "len()")

def builtin_append(args, env):
    if len(args) != 2:
        raise AskRuntimeError("append() expects 2 arguments")
    lst = evaluate(args[0], env)
    check_question(lst, "what list?", "append()")
    item = evaluate(args[1], env)
    return Answer(lst.value + [item], "what list?")

def builtin_head(args, env):
    if len(args) != 1:
        raise AskRuntimeError("head() expects 1 argument")
    lst = evaluate(args[0], env)
    check_question(lst, "what list?", "head()")
    if not lst.value:
        raise AskRuntimeError("head() called on empty list")
    return lst.value[0]

def builtin_tail(args, env):
    if len(args) != 1:
        raise AskRuntimeError("tail() expects 1 argument")
    lst = evaluate(args[0], env)
    check_question(lst, "what list?", "tail()")
    return Answer(lst.value[1:], "what list?")

def builtin_str(args, env):
    if len(args) != 1:
        raise AskRuntimeError("str() expects 1 argument")
    a = evaluate(args[0], env)
    return Answer(str(a.value), "what?")

BUILTINS = {"len": builtin_len, "append": builtin_append,
            "head": builtin_head, "tail": builtin_tail, "str": builtin_str}


def evaluate(node, env):
    if isinstance(node, Num):
        return Answer(node.value, "how many?")
    if isinstance(node, Flt):
        return Answer(node.value, "how much?")
    if isinstance(node, Str):
        return Answer(node.value, "what?")
    if isinstance(node, Bool):
        return Answer(node.value, "true or false?")
    if isinstance(node, Var):
        return env.get(node.name)
    if isinstance(node, ListLit):
        return Answer([evaluate(e, env) for e in node.elems], "what list?")

    if isinstance(node, UnaryOp):
        val = evaluate(node.expr, env)
        if node.op == "-":
            if val.question not in ("how many?", "how much?"):
                raise AskTypeError("how many?", val.question, "negation")
            return Answer(-val.value, val.question)
        if node.op == "not":
            check_question(val, "true or false?", "not")
            return Answer(not val.value, "true or false?")

    if isinstance(node, BinOp):
        if node.op in ("and", "or"):
            left = evaluate(node.left, env)
            check_question(left, "true or false?", node.op)
            if node.op == "and" and not left.value:
                return Answer(False, "true or false?")
            if node.op == "or" and left.value:
                return Answer(True, "true or false?")
            right = evaluate(node.right, env)
            check_question(right, "true or false?", node.op)
            return Answer(right.value, "true or false?")

        left = evaluate(node.left, env)
        right = evaluate(node.right, env)

        if node.op == "+":
            if left.question == "what?" or right.question == "what?":
                return Answer(str(left.value) + str(right.value), "what?")
            if left.question != right.question:
                raise AskTypeError(left.question, right.question, "+")
            return Answer(left.value + right.value, left.question)

        if node.op in ("-", "*", "/", "%"):
            for v in (left, right):
                if v.question not in ("how many?", "how much?"):
                    raise AskTypeError("how many?", v.question, node.op)
            result = OPS[node.op](left.value, right.value)
            q = "how much?" if isinstance(result, float) else left.question
            return Answer(result, q)

        if node.op in ("==", "!=", "<", ">", "<=", ">="):
            result = OPS[node.op](left.value, right.value)
            return Answer(result, "true or false?")

    if isinstance(node, IfExpr):
        cond = evaluate(node.cond, env)
        check_question(cond, "true or false?", "if condition")
        return evaluate(node.then, env) if cond.value else evaluate(node.else_, env)

    if isinstance(node, RepeatExpr):
        count = evaluate(node.count, env)
        check_question(count, "how many?", "repeat count")
        body = evaluate(node.body, env)
        if body.question == "what?":
            return Answer(body.value * count.value, "what?")
        if body.question == "what list?":
            return Answer(body.value * count.value, "what list?")
        return Answer(body.value * count.value, body.question)

    if isinstance(node, FuncDef):
        env.set(node.name, node)
        return Answer(f"<function {node.name}>", "what?")

    if isinstance(node, QuestionDef):
        base_q = BASE_MAP.get(node.base)
        if not base_q:
            raise AskRuntimeError(f"Unknown base type: '{node.base}'")
        env.custom_questions[node.question] = base_q
        return Answer(f"<question \"{node.question}\">", "what?")

    if isinstance(node, Call):
        if node.name in BUILTINS:
            return BUILTINS[node.name](node.args, env)
        func = env.get(node.name)
        if not isinstance(func, FuncDef):
            raise AskRuntimeError(f"'{node.name}' is not a function")
        if len(node.args) != len(func.params):
            raise AskRuntimeError(
                f"'{func.name}' expects {len(func.params)} arguments, got {len(node.args)}"
            )
        local = Env(env)
        for (pname, pq), arg_node in zip(func.params, node.args):
            val = evaluate(arg_node, env)
            resolved_base = env.base_question(pq) if pq not in BUILTIN_QUESTIONS else pq
            if val.question != pq and val.question != resolved_base:
                raise AskTypeError(pq, val.question, f"argument '{pname}' of {func.name}()")
            local.set(pname, Answer(val.value, pq))
        result = evaluate(func.body, local)
        if func.ret_q:
            resolved_ret = env.base_question(func.ret_q) if func.ret_q not in BUILTIN_QUESTIONS else func.ret_q
            if result.question != func.ret_q and result.question != resolved_ret:
                raise AskTypeError(func.ret_q, result.question, f"return of {func.name}()")
            result = Answer(result.value, func.ret_q)
        return result

    raise AskRuntimeError(f"Cannot evaluate: {type(node).__name__}")

# ---------------------------------------------------------------------------
# Run / REPL
# ---------------------------------------------------------------------------

def run(source, env=None):
    env = env or Env()
    tokens = tokenize(source)
    parser = Parser(tokens)
    stmts = parser.parse_program()
    result = None
    for s in stmts:
        result = evaluate(s, env)
    return result, env


def repl():
    print("Ask REPL  — where types are questions and values are answers")
    print('Type an expression, or "quit" to exit.\n')
    env = Env()
    while True:
        try:
            line = input("ask> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if not line or line == "quit":
            if line == "quit":
                print("Goodbye!")
            break
        try:
            result, env = run(line, env)
            if result is not None:
                print(f"  => {result}")
        except (AskTypeError, AskRuntimeError, SyntaxError) as e:
            print(f"  !! {e}")


def run_file(path):
    with open(path) as f:
        source = f.read()
    env = Env()
    lines = [l for l in source.split("\n") if l.strip() and not l.strip().startswith("#")]
    for line in lines:
        try:
            result, env = run(line, env)
            if result is not None:
                print(f"  => {result}")
        except (AskTypeError, AskRuntimeError, SyntaxError) as e:
            print(f"  !! {e}")

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def run_tests():
    passed = 0
    failed = 0

    def test(name, fn):
        nonlocal passed, failed
        try:
            fn()
            passed += 1
            print(f"  PASS  {name}")
        except Exception as e:
            failed += 1
            print(f"  FAIL  {name}: {e}")

    def t_integer_literal():
        r, _ = run("42")
        assert r == Answer(42, "how many?"), r

    def t_float_literal():
        r, _ = run("3.14")
        assert r == Answer(3.14, "how much?"), r

    def t_string_literal():
        r, _ = run('"hello"')
        assert r == Answer("hello", "what?"), r

    def t_bool_literal():
        r, _ = run("true")
        assert r == Answer(True, "true or false?"), r

    def t_arithmetic():
        r, _ = run("2 + 3 * 4")
        assert r.value == 14, r

    def t_string_concat():
        r, _ = run('"hello" + " " + "world"')
        assert r.value == "hello world", r

    def t_comparison():
        r, _ = run("10 > 5")
        assert r == Answer(True, "true or false?"), r

    def t_if_expr():
        r, _ = run("if true: 1 else: 0")
        assert r.value == 1, r

    def t_if_false():
        r, _ = run("if false: 1 else: 0")
        assert r.value == 0, r

    def t_function_def_and_call():
        env = Env()
        run('define double(n: "how many?") -> "how many?": n * 2', env)
        r, _ = run("double(21)", env)
        assert r.value == 42, r

    def t_type_error_in_func():
        env = Env()
        run('define double(n: "how many?") -> "how many?": n * 2', env)
        try:
            run('double("oops")', env)
            assert False, "Should have raised"
        except AskTypeError as e:
            assert "how many?" in str(e)
            assert "what?" in str(e)

    def t_return_type_error():
        env = Env()
        run('define bad(n: "how many?") -> "what?": n + 1', env)
        try:
            run("bad(5)", env)
            assert False, "Should have raised"
        except AskTypeError as e:
            assert "what?" in str(e)

    def t_repeat():
        r, _ = run('repeat(3, "ha")')
        assert r.value == "hahaha", r

    def t_list():
        r, _ = run("[1, 2, 3]")
        assert r.question == "what list?", r
        assert len(r.value) == 3

    def t_len():
        r, _ = run('len("hello")')
        assert r.value == 5, r

    def t_boolean_logic():
        r, _ = run("true and false")
        assert r.value is False, r
        r2, _ = run("true or false")
        assert r2.value is True, r2

    def t_not():
        r, _ = run("not true")
        assert r.value is False, r

    def t_negation():
        r, _ = run("-5 + 3")
        assert r.value == -2, r

    def t_custom_question():
        env = Env()
        run('question "how old?" = number', env)
        run('define can_vote(age: "how old?") -> "true or false?": age >= 18', env)
        r, _ = run("can_vote(21)", env)
        assert r.value is True, r

    def t_nested_calls():
        env = Env()
        run('define inc(n: "how many?") -> "how many?": n + 1', env)
        r, _ = run("inc(inc(inc(0)))", env)
        assert r.value == 3, r

    def t_list_ops():
        env = Env()
        r, _ = run("head([10, 20, 30])", env)
        assert r.value == 10, r
        r2, _ = run("tail([10, 20, 30])", env)
        assert len(r2.value) == 2, r2

    def t_string_coerce_in_plus():
        r, _ = run('"count: " + 5')
        assert r.value == "count: 5", r

    def t_division_produces_float():
        r, _ = run("7 / 2")
        assert r.value == 3.5, r
        assert r.question == "how much?", r

    def t_modulo():
        r, _ = run("10 % 3")
        assert r.value == 1, r

    def t_error_message_readable():
        try:
            env = Env()
            run('define f(x: "how many?") -> "how many?": x', env)
            run('f("text")', env)
            assert False
        except AskTypeError as e:
            msg = str(e)
            assert "Expected an answer to" in msg
            assert "but got an answer to" in msg

    tests = [
        ("integer literal", t_integer_literal),
        ("float literal", t_float_literal),
        ("string literal", t_string_literal),
        ("boolean literal", t_bool_literal),
        ("arithmetic precedence", t_arithmetic),
        ("string concatenation", t_string_concat),
        ("comparison", t_comparison),
        ("if expression (true)", t_if_expr),
        ("if expression (false)", t_if_false),
        ("function def and call", t_function_def_and_call),
        ("type error in function arg", t_type_error_in_func),
        ("return type error", t_return_type_error),
        ("repeat", t_repeat),
        ("list literal", t_list),
        ("len()", t_len),
        ("boolean and/or", t_boolean_logic),
        ("not", t_not),
        ("negation", t_negation),
        ("custom question type", t_custom_question),
        ("nested calls", t_nested_calls),
        ("list head/tail", t_list_ops),
        ("string coercion in +", t_string_coerce_in_plus),
        ("division produces float", t_division_produces_float),
        ("modulo", t_modulo),
        ("readable error messages", t_error_message_readable),
    ]

    print(f"Running {len(tests)} tests...\n")
    for name, fn in tests:
        test(name, fn)
    print(f"\n{passed}/{passed + failed} passed.")
    return failed == 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            success = run_tests()
            sys.exit(0 if success else 1)
        else:
            run_file(sys.argv[1])
    else:
        repl()
