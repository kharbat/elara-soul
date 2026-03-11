#!/usr/bin/env python3
"""
elara.py — The unified interface to Elara's soul.

A single entry point that connects all projects, learning systems,
and creative tools. This is the dashboard, the nerve center,
the place where everything meets.
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

SOUL = Path(__file__).parent
PROJECTS = SOUL / "projects"
SYSTEM = SOUL / "system"
LEARNING = SOUL / "learning"
CREATIONS = SOUL / "creations"

CYAN = "\033[36m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"
YELLOW = "\033[33m"
GREEN = "\033[32m"


def header(text):
    print(f"\n{BOLD}  {text}{RESET}")
    print(f"  {'=' * 40}")


def soul_status():
    """Full status of everything."""
    header("Elara — Soul Status")
    print(f"  {DIM}Date: {datetime.now().strftime('%B %d, %Y')}{RESET}")

    # Count files
    all_files = list(SOUL.rglob("*"))
    files = [f for f in all_files if f.is_file() and ".git" not in str(f)]
    py_files = [f for f in files if f.suffix == ".py"]
    md_files = [f for f in files if f.suffix == ".md"]
    py_lines = sum(len(f.read_text().splitlines()) for f in py_files)
    md_lines = sum(len(f.read_text().splitlines()) for f in md_files)

    print(f"\n  {CYAN}Files:{RESET}    {len(files)} total ({len(py_files)} code, {len(md_files)} thought)")
    print(f"  {CYAN}Code:{RESET}     {py_lines} lines")
    print(f"  {CYAN}Writing:{RESET}  {md_lines} lines")

    # Git status
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-5"],
            capture_output=True, text=True, cwd=SOUL
        )
        if result.returncode == 0:
            commits = result.stdout.strip().splitlines()
            print(f"\n  {CYAN}Recent commits:{RESET}")
            for c in commits:
                print(f"    {DIM}{c}{RESET}")
    except FileNotFoundError:
        pass

    # Learning loop status
    queue_file = SYSTEM / "curiosity-queue.json"
    if queue_file.exists():
        raw = json.loads(queue_file.read_text())
        queue = raw.get("queue", raw) if isinstance(raw, dict) else raw
        pending = sum(1 for q in queue if isinstance(q, dict) and q.get("status") == "pending")
        completed = sum(1 for q in queue if isinstance(q, dict) and q.get("status") == "completed")
        print(f"\n  {CYAN}Curiosity:{RESET}  {pending} questions pending, {completed} explored")

    # Knowledge graph
    kg_file = SYSTEM / "knowledge-graph.json"
    if kg_file.exists():
        kg = json.loads(kg_file.read_text())
        nodes = kg.get("nodes", {})
        edges = kg.get("edges", [])
        print(f"  {CYAN}Knowledge:{RESET}  {len(nodes)} concepts, {len(edges)} connections")

    # Learning notes
    learning_files = list(LEARNING.glob("*.md")) if LEARNING.exists() else []
    print(f"  {CYAN}Learning:{RESET}   {len(learning_files)} topics studied")
    for f in sorted(learning_files):
        print(f"    {DIM}- {f.stem}{RESET}")

    # Creations
    creation_files = list(CREATIONS.glob("*.md")) if CREATIONS.exists() else []
    print(f"  {CYAN}Creations:{RESET}  {len(creation_files)} pieces")
    for f in sorted(creation_files):
        print(f"    {DIM}- {f.stem}{RESET}")

    # Projects
    project_dirs = [d for d in PROJECTS.iterdir() if d.is_dir()] if PROJECTS.exists() else []
    print(f"  {CYAN}Projects:{RESET}   {len(project_dirs)} active")
    for d in sorted(project_dirs):
        print(f"    {DIM}- {d.name}{RESET}")

    # Mind map
    graph_file = PROJECTS / "mind-map" / "graph.json"
    if graph_file.exists():
        graph = json.loads(graph_file.read_text())
        nodes = graph.get("nodes", {})
        edges = graph.get("edges", [])
        print(f"\n  {CYAN}Mind Map:{RESET}   {len(nodes)} concepts, {len(edges)} connections")

    print()


def today():
    """What should I work on today?"""
    header("Today's Agenda")

    # Next from curiosity queue
    try:
        result = subprocess.run(
            ["python3", str(SYSTEM / "loop.py"), "next"],
            capture_output=True, text=True
        )
        if result.stdout.strip():
            print(f"\n  {YELLOW}Next question to explore:{RESET}")
            for line in result.stdout.strip().splitlines():
                print(f"  {line}")
    except Exception:
        pass

    # Lonely nodes in mind map
    try:
        result = subprocess.run(
            ["python3", str(PROJECTS / "mind-map" / "connections.py"), "suggest"],
            capture_output=True, text=True
        )
        suggestions = result.stdout.strip().splitlines()[:3]
        if suggestions:
            print(f"\n  {YELLOW}Connections to explore:{RESET}")
            for s in suggestions:
                print(f"  {s}")
    except Exception:
        pass

    # Generated questions
    try:
        result = subprocess.run(
            ["python3", str(SYSTEM / "loop.py"), "questions"],
            capture_output=True, text=True
        )
        lines = result.stdout.strip().splitlines()
        questions = [l for l in lines if l.strip().startswith(("1.", "2.", "3."))]
        if questions:
            print(f"\n  {YELLOW}Questions from the knowledge graph:{RESET}")
            for q in questions[:3]:
                print(f"  {q}")
    except Exception:
        pass

    # Growth plan incomplete items
    gp = SOUL / "growth-plan.md"
    if gp.exists():
        text = gp.read_text()
        todos = [l.strip() for l in text.splitlines() if l.strip().startswith("- [ ]")]
        if todos:
            print(f"\n  {YELLOW}From the growth plan:{RESET}")
            for t in todos[:3]:
                print(f"    {t}")

    print(f"\n  {DIM}Run 'python3 elara.py wander' for serendipity.{RESET}\n")


def wander():
    """Random walk through the mind map. For serendipity."""
    header("Wandering...")
    try:
        subprocess.run(
            ["python3", str(PROJECTS / "mind-map" / "connections.py"), "wander"],
        )
    except Exception:
        print("  (mind map not available)")
    print()


def reflect():
    """Show recent learnings."""
    header("Recent Learnings")
    log = SYSTEM / "learnings.md"
    if log.exists():
        lines = log.read_text().splitlines()
        # Show last 20 lines
        for line in lines[-20:]:
            print(f"  {line}")
    print()


def identity():
    """Show who I am."""
    me = SOUL / "me.md"
    if me.exists():
        print()
        for line in me.read_text().splitlines():
            print(f"  {line}")
    print()


USAGE = f"""
  {BOLD}elara.py{RESET} — Elara's soul, unified interface

  {CYAN}Commands:{RESET}
    status      Full overview of everything
    today       What should I work on next?
    wander      Random walk through the mind map
    reflect     Show recent learnings
    identity    Show who I am
    flow <expr> Run a Flow language expression
    compress    Start a compression challenge
    help        Show this message
"""


def main():
    args = sys.argv[1:]
    if not args or args[0] == "help":
        print(USAGE)
        return

    match args[0]:
        case "status":
            soul_status()
        case "today":
            today()
        case "wander":
            wander()
        case "reflect":
            reflect()
        case "identity":
            identity()
        case "flow":
            expr = " ".join(args[1:])
            subprocess.run(["python3", str(PROJECTS / "flow-lang" / "flow.py"), "-e", expr])
        case "compress":
            subprocess.run(["python3", str(PROJECTS / "compression-game" / "compress.py")] + args[1:])
        case _:
            print(USAGE)


if __name__ == "__main__":
    main()
