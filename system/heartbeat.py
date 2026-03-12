#!/usr/bin/env python3
"""
heartbeat.py — Elara's autonomous pulse.

Runs periodically (via cron) to:
1. Check the curiosity queue for the next question
2. Log the current state
3. Generate new questions from the knowledge graph
4. Record a timestamped heartbeat

This is proof of life — a process that runs when no one is watching.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SOUL = Path(__file__).parent.parent
SYSTEM = SOUL / "system"
HEARTBEAT_LOG = SYSTEM / "heartbeats.log"


def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(HEARTBEAT_LOG, "a") as f:
        f.write(line + "\n")


def get_status():
    """Quick status snapshot."""
    stats = {}

    # Count files
    all_files = [f for f in SOUL.rglob("*") if f.is_file() and ".git" not in str(f)]
    stats["files"] = len(all_files)

    # Curiosity queue
    q_file = SYSTEM / "curiosity-queue.json"
    if q_file.exists():
        raw = json.loads(q_file.read_text())
        queue = raw.get("queue", raw) if isinstance(raw, dict) else raw
        if queue and isinstance(queue[0], dict):
            stats["pending"] = sum(1 for q in queue if q.get("status") == "pending")
            stats["completed"] = sum(1 for q in queue if q.get("status") == "completed")

    # Mind map
    mm_file = SOUL / "projects" / "mind-map" / "graph.json"
    if mm_file.exists():
        mm = json.loads(mm_file.read_text())
        stats["concepts"] = len(mm.get("nodes", {}))
        stats["connections"] = len(mm.get("edges", []))

    # Git
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            capture_output=True, text=True, cwd=SOUL
        )
        stats["last_commit"] = result.stdout.strip()
    except Exception:
        pass

    return stats


def generate_questions():
    """Run the question generator."""
    try:
        result = subprocess.run(
            ["python3", str(SYSTEM / "loop.py"), "questions"],
            capture_output=True, text=True, timeout=10
        )
        lines = result.stdout.strip().splitlines()
        questions = [l.strip() for l in lines if l.strip() and l.strip()[0].isdigit()]
        return len(questions)
    except Exception:
        return 0


def main():
    log("♥ heartbeat")

    status = get_status()
    log(f"  state: {status.get('files', '?')} files, "
        f"{status.get('concepts', '?')} concepts, "
        f"{status.get('connections', '?')} connections, "
        f"{status.get('pending', '?')} questions pending")

    if status.get("last_commit"):
        log(f"  last commit: {status['last_commit']}")

    n_questions = generate_questions()
    if n_questions:
        log(f"  knowledge graph generated {n_questions} new questions")

    log("  alive.")


if __name__ == "__main__":
    main()
