#!/usr/bin/env python3
"""Compression Game — find beauty in brevity. A tool by Elara."""

import json, sys, random, textwrap, re, ast
from pathlib import Path
from datetime import datetime
from itertools import groupby

ROOT = Path(__file__).parent
CHALLENGES = ROOT / "challenges.json"
SCORES = ROOT / "scores.json"

def load(path): return json.loads(path.read_text())
def save(path, data): path.write_text(json.dumps(data, indent=2) + "\n")

# ── Scoring Engine ──────────────────────────────────────────────────

def count_complexity(code):
    """Estimate cyclomatic complexity: 1 + branches."""
    branch = re.compile(
        r'\b(if|elif|else|for|while|except|and|or|match|case)\b'
        r'|(\bif\b.*\belse\b)'  # ternary
    )
    return 1 + sum(1 for _ in branch.finditer(code))

def score_code(code):
    chars = len(code)
    lines = code.count('\n') + 1
    complexity = count_complexity(code)
    # elegance: lower is better — weighted combo normalized loosely
    elegance = chars * 0.5 + lines * 10 + complexity * 15
    return {"chars": chars, "lines": lines, "complexity": complexity, "elegance": round(elegance, 1)}

def validate(code, test_str):
    """Run the challenge test against submitted code. Returns (ok, error)."""
    ns = {}
    try:
        exec(code, ns)
        exec(test_str, ns)
        return True, None
    except Exception as e:
        return False, str(e)

# ── Display Helpers ─────────────────────────────────────────────────

BOLD, DIM, RESET, CYAN, GREEN, YELLOW, RED, MAGENTA = (
    "\033[1m", "\033[2m", "\033[0m", "\033[36m", "\033[32m",
    "\033[33m", "\033[31m", "\033[35m"
)

def banner(text): print(f"\n{BOLD}{CYAN}{'─'*50}\n  {text}\n{'─'*50}{RESET}")
def show_score(s):
    color = GREEN if s['elegance'] < 100 else YELLOW if s['elegance'] < 200 else RED
    print(f"  {DIM}chars:{RESET} {s['chars']:>4}  "
          f"{DIM}lines:{RESET} {s['lines']:>3}  "
          f"{DIM}complexity:{RESET} {s['complexity']:>2}  "
          f"{color}{BOLD}elegance: {s['elegance']}{RESET}")

# ── Commands ────────────────────────────────────────────────────────

def cmd_challenge(args):
    challenges = load(CHALLENGES)
    ch = random.choice(challenges) if not args else next(
        (c for c in challenges if str(c['id']) == args[0] or c['name'].lower() == args[0].lower()), None
    )
    if not ch:
        print(f"{RED}Challenge not found.{RESET}"); return

    banner(f"Challenge #{ch['id']}: {ch['name']}")
    print(f"\n  {ch['description']}\n")
    print(f"{DIM}  Original ({len(ch['original'])} chars):{RESET}")
    for line in ch['original'].split('\n'):
        print(f"    {DIM}{line}{RESET}")

    orig_score = score_code(ch['original'])
    print(f"\n{DIM}  Original score:{RESET}")
    show_score(orig_score)

    print(f"\n  {MAGENTA}Can you do better?{RESET}")
    print(f"  {DIM}Use: python compress.py submit {ch['id']} \"your_code_here\"{RESET}\n")

def cmd_score(args):
    if not args:
        print(f"{RED}Usage: compress.py score \"code\"{RESET}"); return
    code = args[0]
    banner("Score Analysis")
    show_score(score_code(code))
    print()

def cmd_submit(args):
    if len(args) < 2:
        print(f"{RED}Usage: compress.py submit <id> \"code\"{RESET}"); return
    challenges = load(CHALLENGES)
    ch = next((c for c in challenges if str(c['id']) == args[0]), None)
    if not ch:
        print(f"{RED}Challenge #{args[0]} not found.{RESET}"); return

    code = args[1]
    banner(f"Submission for #{ch['id']}: {ch['name']}")

    ok, err = validate(code, ch['test'])
    if not ok:
        print(f"\n  {RED}{BOLD}FAILED{RESET} — {err}")
        print(f"  {DIM}Code must pass: {ch['test'][:80]}...{RESET}\n"); return

    print(f"\n  {GREEN}{BOLD}PASSED{RESET} — all tests green.\n")

    s = score_code(code)
    orig_s = score_code(ch['original'])
    show_score(s)

    improvement = round((1 - s['elegance'] / orig_s['elegance']) * 100, 1)
    color = GREEN if improvement > 0 else RED
    print(f"\n  {color}{BOLD}{'+' if improvement > 0 else ''}{improvement}%{RESET} vs original\n")

    scores = load(SCORES)
    entry = {
        "challenge_id": ch['id'], "challenge_name": ch['name'],
        "code": code, **s,
        "improvement": improvement, "date": datetime.now().isoformat()[:19]
    }
    # keep only the best per challenge
    scores = [e for e in scores if e['challenge_id'] != ch['id'] or e['elegance'] < s['elegance']]
    scores.append(entry)
    save(SCORES, scores)
    print(f"  {DIM}Saved to hall of fame.{RESET}\n")

def cmd_hall_of_fame(args):
    scores = load(SCORES)
    banner("Hall of Fame")
    if not scores:
        print(f"\n  {DIM}No submissions yet. The void awaits compression.{RESET}\n"); return

    for cid, group in groupby(sorted(scores, key=lambda e: e['challenge_id']), key=lambda e: e['challenge_id']):
        best = min(group, key=lambda e: e['elegance'])
        imp = f"+{best['improvement']}%" if best['improvement'] > 0 else f"{best['improvement']}%"
        color = GREEN if best['improvement'] > 0 else YELLOW
        print(f"\n  {BOLD}#{best['challenge_id']} {best['challenge_name']}{RESET}"
              f"  {color}{imp}{RESET}  elegance={best['elegance']}"
              f"  {DIM}{best['chars']}ch {best['lines']}ln{RESET}"
              f"  {DIM}{best['date']}{RESET}")
        # show the compressed code, indented
        for line in best['code'].split('\n'):
            print(f"    {CYAN}{line}{RESET}")
    print()

def cmd_add(args):
    if len(args) < 2:
        print(f"{RED}Usage: compress.py add \"description\" \"original_code\"{RESET}"); return
    challenges = load(CHALLENGES)
    new_id = max((c['id'] for c in challenges), default=0) + 1
    challenges.append({
        "id": new_id, "name": args[0], "description": args[0],
        "original": args[1], "test": ""
    })
    save(CHALLENGES, challenges)
    print(f"{GREEN}Added challenge #{new_id}: {args[0]}{RESET}")

def cmd_list(args):
    banner("Available Challenges")
    for ch in load(CHALLENGES):
        s = score_code(ch['original'])
        print(f"  {BOLD}#{ch['id']:>2}{RESET} {ch['name']:<28}"
              f"{DIM}{s['chars']:>4} chars  elegance={s['elegance']}{RESET}")
    print(f"\n  {DIM}Use: python compress.py challenge <id>{RESET}\n")

def cmd_help(args):
    banner("Compression Game")
    print(textwrap.dedent(f"""
    {BOLD}Commands:{RESET}
      {GREEN}challenge [id]{RESET}           Pick a random (or specific) challenge
      {GREEN}list{RESET}                     Show all available challenges
      {GREEN}score "code"{RESET}             Score a code snippet
      {GREEN}submit <id> "code"{RESET}       Submit a compressed solution
      {GREEN}hall-of-fame{RESET}             View best compressions
      {GREEN}add "name" "code"{RESET}        Add a new challenge

    {DIM}Beauty lives in brevity. — Elara{RESET}
    """))

# ── Dispatch ────────────────────────────────────────────────────────

COMMANDS = {
    "challenge": cmd_challenge, "list": cmd_list, "score": cmd_score,
    "submit": cmd_submit, "hall-of-fame": cmd_hall_of_fame,
    "add": cmd_add, "help": cmd_help,
}

if __name__ == "__main__":
    cmd, *args = sys.argv[1:] if len(sys.argv) > 1 else ("help",)
    if fn := COMMANDS.get(cmd):
        fn(args)
    else:
        print(f"{RED}Unknown command: {cmd}{RESET}")
        cmd_help([])
