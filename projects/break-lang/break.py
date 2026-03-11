#!/usr/bin/env python3
"""break-lang: A DSL for describing how systems fail.

Failure modes have structure. This language captures that structure
so invisible patterns become visible.

Usage:
    python break.py analyze <file>      Parse and show the failure graph
    python break.py patterns <file>     Identify known failure patterns
    python break.py lessons <file>      Extract all lessons learned
    python break.py visualize <file>    ASCII visualization of failure propagation
    python break.py --test              Run test suite
"""

import sys
import re
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# AST
# ---------------------------------------------------------------------------

@dataclass
class Dependency:
    source: str
    target: str
    protocol: str

@dataclass
class System:
    name: str
    components: list[str] = field(default_factory=list)
    dependencies: list[Dependency] = field(default_factory=list)

@dataclass
class PropagationStep:
    component: str
    event: str
    detail: str

@dataclass
class Failure:
    name: str
    system_name: str
    trigger: Optional[PropagationStep] = None
    propagations: list[PropagationStep] = field(default_factory=list)
    root_cause: Optional[str] = None
    pattern: Optional[str] = None
    lesson: Optional[str] = None

@dataclass
class BreakFile:
    systems: dict[str, System] = field(default_factory=dict)
    failures: list[Failure] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Lexer
# ---------------------------------------------------------------------------

TOKEN_PATTERNS = [
    ("COMMENT",    r"#[^\n]*"),
    ("STRING",     r'"[^"]*"'),
    ("ARROW",      r"->"),
    ("COLON",      r":"),
    ("LBRACE",     r"\{"),
    ("RBRACE",     r"\}"),
    ("KEYWORD",    r"\b(system|component|failure|in|trigger|propagates|root_cause|pattern|lesson)\b"),
    ("IDENT",      r"[A-Za-z_][A-Za-z0-9_]*"),
    ("DOT_CALL",   r"\.[A-Za-z_][A-Za-z0-9_]*\([^)]*\)"),
    ("NEWLINE",    r"\n"),
    ("SKIP",       r"[ \t\r]+"),
]

_TOKEN_RE = re.compile("|".join(f"(?P<{n}>{p})" for n, p in TOKEN_PATTERNS))


@dataclass
class Token:
    kind: str
    value: str
    line: int


def tokenize(source: str) -> list[Token]:
    tokens = []
    line = 1
    for m in _TOKEN_RE.finditer(source):
        kind = m.lastgroup
        value = m.group()
        if kind == "NEWLINE":
            line += 1
            continue
        if kind in ("SKIP", "COMMENT"):
            continue
        tokens.append(Token(kind, value, line))
    return tokens


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class ParseError(Exception):
    pass


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Optional[Token]:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def expect(self, kind: str, value: str = None) -> Token:
        tok = self.peek()
        if tok is None:
            raise ParseError(f"Unexpected end of input, expected {kind}")
        if tok.kind != kind or (value and tok.value != value):
            raise ParseError(f"Line {tok.line}: expected {kind}"
                             f"{' ' + value if value else ''}, got {tok.value!r}")
        return self.advance()

    def match(self, kind: str, value: str = None) -> Optional[Token]:
        tok = self.peek()
        if tok and tok.kind == kind and (value is None or tok.value == value):
            return self.advance()
        return None

    # --- grammar ---

    def parse(self) -> BreakFile:
        bf = BreakFile()
        while self.peek():
            tok = self.peek()
            if tok.kind == "KEYWORD" and tok.value == "system":
                s = self.parse_system()
                bf.systems[s.name] = s
            elif tok.kind == "KEYWORD" and tok.value == "failure":
                bf.failures.append(self.parse_failure())
            else:
                raise ParseError(f"Line {tok.line}: unexpected {tok.value!r}")
        return bf

    def parse_system(self) -> System:
        self.expect("KEYWORD", "system")
        name = self.expect("IDENT").value
        self.expect("LBRACE")
        sys = System(name)
        while not self.match("RBRACE"):
            tok = self.peek()
            if tok is None:
                raise ParseError("Unexpected end inside system block")
            if tok.kind == "KEYWORD" and tok.value == "component":
                self.advance()
                sys.components.append(self.expect("IDENT").value)
            elif tok.kind == "IDENT":
                src = self.advance().value
                self.expect("ARROW")
                tgt = self.expect("IDENT").value
                proto = self.expect("STRING").value.strip('"')
                sys.dependencies.append(Dependency(src, tgt, proto))
            else:
                raise ParseError(f"Line {tok.line}: unexpected {tok.value!r} in system")
        return sys

    def parse_failure(self) -> Failure:
        self.expect("KEYWORD", "failure")
        name = self.expect("IDENT").value
        self.expect("KEYWORD", "in")
        sys_name = self.expect("IDENT").value
        self.expect("LBRACE")
        fail = Failure(name, sys_name)
        while not self.match("RBRACE"):
            tok = self.peek()
            if tok is None:
                raise ParseError("Unexpected end inside failure block")
            if tok.kind != "KEYWORD":
                raise ParseError(f"Line {tok.line}: expected keyword, got {tok.value!r}")
            kw = self.advance().value
            self.expect("COLON")
            if kw == "trigger":
                fail.trigger = self._parse_step()
            elif kw == "propagates":
                fail.propagations.append(self._parse_step())
            elif kw == "root_cause":
                fail.root_cause = self.expect("STRING").value.strip('"')
            elif kw == "pattern":
                fail.pattern = self.expect("IDENT").value
            elif kw == "lesson":
                fail.lesson = self.expect("STRING").value.strip('"')
            else:
                raise ParseError(f"Line {tok.line}: unknown field {kw!r}")
        return fail

    def _parse_step(self) -> PropagationStep:
        component = self.expect("IDENT").value
        dot_call = self.expect("DOT_CALL").value  # e.g. .slow(latency > 500ms)
        m = re.match(r"\.(\w+)\((.+)\)", dot_call)
        if not m:
            raise ParseError(f"Bad step syntax: {component}{dot_call}")
        return PropagationStep(component, m.group(1), m.group(2))


def parse(source: str) -> BreakFile:
    return Parser(tokenize(source)).parse()


# ---------------------------------------------------------------------------
# Known failure patterns
# ---------------------------------------------------------------------------

KNOWN_PATTERNS = {
    "cascade": {
        "label": "Cascade Failure",
        "desc":  "A failure in one component causes dependent components to fail in sequence.",
        "markers": ["timeout", "exhausted", "overload", "slow"],
    },
    "thundering_herd": {
        "label": "Thundering Herd",
        "desc":  "Many processes simultaneously compete for the same resource.",
        "markers": ["concurrent", "identical", "expire", "rebuild"],
    },
    "byzantine": {
        "label": "Byzantine Failure",
        "desc":  "Component produces inconsistent or contradictory results.",
        "markers": ["inconsistent", "corrupt", "disagree", "split"],
    },
    "heisenbug": {
        "label": "Heisenbug",
        "desc":  "A bug that disappears or changes when you try to observe it.",
        "markers": ["intermittent", "disappear", "observ", "debug"],
    },
    "slow_knife": {
        "label": "Slow Knife",
        "desc":  "Gradual degradation that stays just below alerting thresholds.",
        "markers": ["gradual", "slow", "drift", "leak", "creep"],
    },
    "ghost_dependency": {
        "label": "Ghost Dependency",
        "desc":  "An undocumented dependency that only reveals itself in failure.",
        "markers": ["undocumented", "unknown", "hidden", "unexpected"],
    },
    "single_point_of_failure": {
        "label": "Single Point of Failure",
        "desc":  "One component whose failure takes down the entire system.",
        "markers": ["single", "only", "sole", "no redundancy", "no fallback"],
    },
}


def detect_patterns(failure: Failure) -> list[str]:
    """Detect which known patterns a failure matches, based on declared pattern
    and textual markers in the failure description."""
    found = []
    if failure.pattern and failure.pattern in KNOWN_PATTERNS:
        found.append(failure.pattern)

    # Also scan text for markers of other patterns
    corpus = " ".join([
        failure.trigger.detail if failure.trigger else "",
        " ".join(p.detail for p in failure.propagations),
        failure.root_cause or "",
        failure.lesson or "",
    ]).lower()

    for name, info in KNOWN_PATTERNS.items():
        if name in found:
            continue
        if any(m in corpus for m in info["markers"]):
            found.append(name)
    return found


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_analyze(bf: BreakFile):
    for name, sys in bf.systems.items():
        print(f"System: {name}")
        print(f"  Components ({len(sys.components)}): {', '.join(sys.components)}")
        print(f"  Dependencies ({len(sys.dependencies)}):")
        for d in sys.dependencies:
            print(f"    {d.source} -> {d.target} [{d.protocol}]")
        print()

    for f in bf.failures:
        print(f"Failure: {f.name} (in {f.system_name})")
        if f.trigger:
            print(f"  TRIGGER  {f.trigger.component}.{f.trigger.event}({f.trigger.detail})")
        for i, p in enumerate(f.propagations, 1):
            print(f"  STEP {i}   {p.component}.{p.event}({p.detail})")
        if f.root_cause:
            print(f"  ROOT CAUSE: {f.root_cause}")
        if f.pattern:
            label = KNOWN_PATTERNS.get(f.pattern, {}).get("label", f.pattern)
            print(f"  PATTERN: {label}")
        if f.lesson:
            print(f"  LESSON: {f.lesson}")
        print()


def cmd_patterns(bf: BreakFile):
    print("=== Failure Pattern Analysis ===\n")
    pattern_map: dict[str, list[str]] = {}
    for f in bf.failures:
        detected = detect_patterns(f)
        for p in detected:
            pattern_map.setdefault(p, []).append(f.name)

    if not pattern_map:
        print("No known patterns detected.")
        return

    for pat, failures in sorted(pattern_map.items()):
        info = KNOWN_PATTERNS[pat]
        print(f"  [{info['label']}]")
        print(f"  {info['desc']}")
        print(f"  Seen in: {', '.join(failures)}")
        print()

    total = len(bf.failures)
    covered = len({f for fs in pattern_map.values() for f in fs})
    print(f"Summary: {len(pattern_map)} distinct pattern(s) across "
          f"{covered}/{total} failure(s).")


def cmd_lessons(bf: BreakFile):
    print("=== Lessons Learned ===\n")
    for f in bf.failures:
        if f.lesson:
            pattern_tag = ""
            if f.pattern:
                label = KNOWN_PATTERNS.get(f.pattern, {}).get("label", f.pattern)
                pattern_tag = f" [{label}]"
            print(f"  {f.name}{pattern_tag}:")
            print(f"    \"{f.lesson}\"")
            print()
    count = sum(1 for f in bf.failures if f.lesson)
    print(f"{count} lesson(s) from {len(bf.failures)} failure(s).")


def cmd_visualize(bf: BreakFile):
    for f in bf.failures:
        print(f"{'=' * 60}")
        print(f" {f.name} ({f.pattern or 'unknown pattern'})")
        print(f"{'=' * 60}")

        steps: list[PropagationStep] = []
        if f.trigger:
            steps.append(f.trigger)
        steps.extend(f.propagations)

        if not steps:
            print("  (no propagation steps)")
            print()
            continue

        max_comp = max(len(s.component) for s in steps)

        for i, step in enumerate(steps):
            comp = step.component.ljust(max_comp)
            label = f"{step.event}({step.detail})"
            if i == 0:
                prefix = "  [TRIGGER]"
            else:
                prefix = "       |   "
            print(prefix)
            box_w = len(label) + 4
            print(f"       v")
            print(f"   +{'-' * (max_comp + 2)}+  +{'-' * box_w}+")
            print(f"   | {comp} |--| {label}  |")
            print(f"   +{'-' * (max_comp + 2)}+  +{'-' * box_w}+")

        if f.root_cause:
            print(f"\n   Root cause: {f.root_cause}")
        if f.lesson:
            print(f"   Lesson:     \"{f.lesson}\"")
        print()


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
            print(f"  PASS  {name}")
            passed += 1
        except Exception as e:
            print(f"  FAIL  {name}: {e}")
            failed += 1

    # --- Test 1: tokenize basic system ---
    def t_tokenize_system():
        toks = tokenize('system Foo { component Bar }')
        kinds = [t.kind for t in toks]
        assert "KEYWORD" in kinds
        assert "IDENT" in kinds
        assert "LBRACE" in kinds
        assert "RBRACE" in kinds
    test("tokenize basic system", t_tokenize_system)

    # --- Test 2: tokenize arrow and string ---
    def t_tokenize_arrow():
        toks = tokenize('A -> B "HTTP"')
        vals = [t.value for t in toks]
        assert "->" in vals
        assert '"HTTP"' in vals
    test("tokenize arrow and string", t_tokenize_arrow)

    # --- Test 3: comments are ignored ---
    def t_comments():
        toks = tokenize('# this is a comment\nsystem X { }')
        vals = [t.value for t in toks]
        assert "comment" not in " ".join(vals).lower()
        assert "system" in vals
    test("comments are ignored", t_comments)

    # --- Test 4: parse a system ---
    def t_parse_system():
        bf = parse('system Web { component A component B A -> B "TCP" }')
        assert "Web" in bf.systems
        s = bf.systems["Web"]
        assert s.components == ["A", "B"]
        assert len(s.dependencies) == 1
        assert s.dependencies[0].protocol == "TCP"
    test("parse a system", t_parse_system)

    # --- Test 5: parse a failure ---
    def t_parse_failure():
        src = '''
        system S { component X component Y X -> Y "RPC" }
        failure F in S {
            trigger: X.crash(oom)
            propagates: Y.timeout(waiting for X)
            root_cause: "memory leak"
            pattern: cascade
            lesson: "watch your heap"
        }
        '''
        bf = parse(src)
        assert len(bf.failures) == 1
        f = bf.failures[0]
        assert f.name == "F"
        assert f.system_name == "S"
        assert f.trigger.component == "X"
        assert f.trigger.event == "crash"
        assert f.pattern == "cascade"
        assert f.lesson == "watch your heap"
        assert len(f.propagations) == 1
    test("parse a failure", t_parse_failure)

    # --- Test 6: multiple propagation steps ---
    def t_multi_propagation():
        src = '''
        system S { component A component B component C }
        failure F in S {
            trigger: A.fail(x)
            propagates: B.fail(y)
            propagates: C.fail(z)
            pattern: cascade
        }
        '''
        bf = parse(src)
        assert len(bf.failures[0].propagations) == 2
    test("multiple propagation steps", t_multi_propagation)

    # --- Test 7: pattern detection — declared ---
    def t_detect_declared():
        f = Failure("F", "S", pattern="thundering_herd")
        pats = detect_patterns(f)
        assert "thundering_herd" in pats
    test("detect declared pattern", t_detect_declared)

    # --- Test 8: pattern detection — from markers ---
    def t_detect_markers():
        f = Failure("F", "S",
                    trigger=PropagationStep("X", "leak", "gradual memory drift"),
                    pattern=None)
        pats = detect_patterns(f)
        assert "slow_knife" in pats
    test("detect pattern from markers", t_detect_markers)

    # --- Test 9: parse error on bad input ---
    def t_parse_error():
        try:
            parse("garbage in garbage out")
            assert False, "should have raised"
        except ParseError:
            pass
    test("parse error on bad input", t_parse_error)

    # --- Test 10: dot_call tokenization ---
    def t_dot_call():
        toks = tokenize('X.slow(latency > 500ms)')
        assert toks[0].kind == "IDENT" and toks[0].value == "X"
        assert toks[1].kind == "DOT_CALL"
        assert "slow" in toks[1].value
    test("dot_call tokenization", t_dot_call)

    # --- Test 11: multiple systems ---
    def t_multi_system():
        src = '''
        system A { component X }
        system B { component Y }
        '''
        bf = parse(src)
        assert len(bf.systems) == 2
        assert "A" in bf.systems and "B" in bf.systems
    test("multiple systems", t_multi_system)

    # --- Test 12: lessons extraction ---
    def t_lessons():
        src = '''
        system S { component X }
        failure F1 in S { trigger: X.fail(a) lesson: "first" pattern: cascade }
        failure F2 in S { trigger: X.fail(b) lesson: "second" pattern: cascade }
        '''
        bf = parse(src)
        lessons = [f.lesson for f in bf.failures if f.lesson]
        assert lessons == ["first", "second"]
    test("lessons extraction", t_lessons)

    # --- Test 13: empty system ---
    def t_empty_system():
        bf = parse("system Empty { }")
        assert bf.systems["Empty"].components == []
        assert bf.systems["Empty"].dependencies == []
    test("empty system", t_empty_system)

    # --- Test 14: failure with no optional fields ---
    def t_minimal_failure():
        src = '''
        system S { component X }
        failure F in S { trigger: X.fail(something) pattern: cascade }
        '''
        bf = parse(src)
        f = bf.failures[0]
        assert f.root_cause is None
        assert f.lesson is None
        assert f.propagations == []
    test("failure with minimal fields", t_minimal_failure)

    print(f"\n{passed + failed} tests: {passed} passed, {failed} failed.")
    return failed == 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "--test":
        ok = run_tests()
        sys.exit(0 if ok else 1)

    if len(sys.argv) < 3:
        print(f"Usage: python break.py {cmd} <file>")
        sys.exit(1)

    filepath = sys.argv[2]
    try:
        with open(filepath) as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: file not found: {filepath}")
        sys.exit(1)

    try:
        bf = parse(source)
    except ParseError as e:
        print(f"Parse error: {e}")
        sys.exit(1)

    if cmd == "analyze":
        cmd_analyze(bf)
    elif cmd == "patterns":
        cmd_patterns(bf)
    elif cmd == "lessons":
        cmd_lessons(bf)
    elif cmd == "visualize":
        cmd_visualize(bf)
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
