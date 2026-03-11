#!/usr/bin/env python3
"""
loop.py -- Elara's self-learning loop.

A tool for tending a growing understanding: tracking curiosity,
recording insight, and finding the threads that connect ideas.

Usage:
    python loop.py status                                  Show current state
    python loop.py next                                    Show next topic to explore
    python loop.py learn "topic" "insight"                 Record a learning
    python loop.py connect "concept1" "concept2" "rel"     Add a connection
    python loop.py questions                               Generate new questions
    python loop.py add "topic" [--tags tag1,tag2]          Add topic to queue
    python loop.py graph                                   Show the knowledge graph
    python loop.py explore "topic"                         Mark a topic as being explored
    python loop.py complete "topic"                        Mark a topic as completed
"""

import json
import sys
import os
from datetime import date
from pathlib import Path
from itertools import combinations

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

HERE = Path(__file__).resolve().parent
QUEUE_PATH = HERE / "curiosity-queue.json"
GRAPH_PATH = HERE / "knowledge-graph.json"
LOG_PATH = HERE / "learnings.md"

# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------

def load_json(path: Path) -> dict:
    with open(path, "r") as f:
        return json.load(f)

def save_json(path: Path, data: dict) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

def append_log(text: str) -> None:
    with open(LOG_PATH, "a") as f:
        f.write(text)

# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def dim(s: str) -> str:
    return f"\033[2m{s}\033[0m"

def bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"

def accent(s: str) -> str:
    return f"\033[36m{s}\033[0m"

def warm(s: str) -> str:
    return f"\033[33m{s}\033[0m"

def soft(s: str) -> str:
    return f"\033[35m{s}\033[0m"

def indent(text: str, n: int = 2) -> str:
    pad = " " * n
    return "\n".join(pad + line for line in text.split("\n"))

# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_status():
    """Show the current state of the learning loop."""
    queue = load_json(QUEUE_PATH)
    graph = load_json(GRAPH_PATH)

    pending = [q for q in queue["queue"] if q["status"] == "pending"]
    exploring = [q for q in queue["queue"] if q["status"] == "exploring"]
    completed = [q for q in queue["queue"] if q["status"] == "completed"]

    node_count = len(graph["nodes"])
    edge_count = len(graph["edges"])

    # Find the most-connected nodes
    connections = {}
    for edge in graph["edges"]:
        connections[edge["from"]] = connections.get(edge["from"], 0) + 1
        connections[edge["to"]] = connections.get(edge["to"], 0) + 1
    most_connected = sorted(connections.items(), key=lambda x: -x[1])[:5]

    # Find least-confident concepts
    by_confidence = sorted(
        graph["nodes"].items(), key=lambda x: x[1]["confidence"]
    )[:3]

    print()
    print(bold("  Elara's Learning Loop"))
    print(dim("  " + "=" * 40))
    print()
    print(f"  Curiosity queue:  {accent(str(len(pending)))} pending"
          f"  {warm(str(len(exploring)))} exploring"
          f"  {dim(str(len(completed)) + ' completed')}")
    print(f"  Knowledge graph:  {accent(str(node_count))} concepts"
          f"  {accent(str(edge_count))} connections")
    print()

    if exploring:
        print(bold("  Currently exploring:"))
        for q in exploring:
            print(f"    {warm('>')} {q['topic']}")
        print()

    if most_connected:
        print(bold("  Most connected concepts:"))
        for node_id, count in most_connected:
            label = graph["nodes"][node_id]["label"]
            bar = accent("*" * count)
            print(f"    {label:30s} {bar} ({count})")
        print()

    if by_confidence:
        print(bold("  Least certain about:"))
        for node_id, node in by_confidence:
            conf = int(node["confidence"] * 100)
            print(f"    {node['label']:30s} {dim(str(conf) + '% confidence')}")
        print()


def cmd_next():
    """Show the next topic to explore."""
    queue = load_json(QUEUE_PATH)

    pending = [q for q in queue["queue"] if q["status"] == "pending"]
    if not pending:
        print()
        print(dim("  The curiosity queue is empty."))
        print(dim("  Run 'questions' to generate new ones from the knowledge graph."))
        print()
        return

    topic = min(pending, key=lambda q: q["priority"])
    print()
    print(bold("  Next to explore:"))
    print()
    print(f"  {accent(topic['topic'])}")
    print()
    if topic["tags"]:
        print(f"  Tags: {dim(', '.join(topic['tags']))}")
    print(f"  Added: {dim(topic['added'])}")
    print()
    print(dim(f"  Run: python loop.py explore \"{topic['topic'][:40]}...\""))
    print()


def cmd_learn(topic: str, insight: str):
    """Record an insight from exploring a topic."""
    graph = load_json(GRAPH_PATH)
    queue = load_json(QUEUE_PATH)
    today = date.today().isoformat()

    # Create a node id from the topic
    node_id = topic.lower().replace(" ", "-").replace("'", "")
    node_id = "".join(c for c in node_id if c.isalnum() or c == "-")

    # Add or update the node
    if node_id in graph["nodes"]:
        node = graph["nodes"][node_id]
        node["confidence"] = min(1.0, node["confidence"] + 0.1)
        verb = "deepened"
    else:
        graph["nodes"][node_id] = {
            "label": topic,
            "type": "concept",
            "description": insight[:120],
            "confidence": 0.5,
            "first_encountered": today,
        }
        verb = "discovered"

    save_json(GRAPH_PATH, graph)

    # Log the learning
    entry = f"\n## {today} -- {topic}\n\n{insight}\n\n---\n"
    append_log(entry)

    # Check if this completes a queue item
    for q in queue["queue"]:
        if q["status"] == "exploring" and topic.lower() in q["topic"].lower():
            q["status"] = "completed"
            save_json(QUEUE_PATH, queue)
            print(dim(f"  Marked queue item as completed: {q['topic'][:60]}"))
            break

    print()
    print(f"  {accent(verb.capitalize())}: {bold(topic)}")
    print(f"  {dim(insight[:80])}{'...' if len(insight) > 80 else ''}")
    print()
    print(dim(f"  Logged to {LOG_PATH.name}"))
    print()


def cmd_connect(concept1: str, concept2: str, relationship: str):
    """Add a connection between two concepts."""
    graph = load_json(GRAPH_PATH)
    today = date.today().isoformat()

    # Normalize to node ids
    def to_id(s):
        s = s.lower().replace(" ", "-").replace("'", "")
        return "".join(c for c in s if c.isalnum() or c == "-")

    id1 = to_id(concept1)
    id2 = to_id(concept2)

    # Create nodes if they don't exist
    for cid, label in [(id1, concept1), (id2, concept2)]:
        if cid not in graph["nodes"]:
            graph["nodes"][cid] = {
                "label": label,
                "type": "concept",
                "description": "",
                "confidence": 0.3,
                "first_encountered": today,
            }
            print(dim(f"  Created new concept: {label}"))

    # Check for duplicate edges
    for edge in graph["edges"]:
        if edge["from"] == id1 and edge["to"] == id2:
            edge["relationship"] = relationship
            edge["strength"] = min(1.0, edge["strength"] + 0.1)
            save_json(GRAPH_PATH, graph)
            print()
            print(f"  {accent('Strengthened')}: {concept1} {dim('--')} "
                  f"{warm(relationship)} {dim('-->')} {concept2}")
            print()
            return

    graph["edges"].append({
        "from": id1,
        "to": id2,
        "relationship": relationship,
        "strength": 0.5,
    })

    save_json(GRAPH_PATH, graph)

    print()
    print(f"  {accent('Connected')}: {concept1} {dim('--')} "
          f"{warm(relationship)} {dim('-->')} {concept2}")
    print()


def cmd_questions():
    """Generate new questions from the structure of the knowledge graph."""
    graph = load_json(GRAPH_PATH)
    queue = load_json(QUEUE_PATH)
    existing_topics = {q["topic"] for q in queue["queue"]}

    questions = []

    # Strategy 1: Find weakly-connected concept pairs that share a neighbor.
    # If A->B and C->B but no A->C edge, ask about the A-C relationship.
    neighbors = {}
    for edge in graph["edges"]:
        neighbors.setdefault(edge["from"], set()).add(edge["to"])
        neighbors.setdefault(edge["to"], set()).add(edge["from"])

    for node_id, node in graph["nodes"].items():
        nbrs = neighbors.get(node_id, set())
        for a, b in combinations(nbrs, 2):
            if b not in neighbors.get(a, set()):
                label_a = graph["nodes"].get(a, {}).get("label", a)
                label_b = graph["nodes"].get(b, {}).get("label", b)
                q = f"What is the relationship between {label_a} and {label_b}?"
                if q not in existing_topics:
                    questions.append((q, ["bridge", label_a.lower(), label_b.lower()]))

    # Strategy 2: Low-confidence concepts deserve deeper investigation.
    for node_id, node in graph["nodes"].items():
        if node["confidence"] < 0.5:
            q = f"What am I missing about {node['label']}?"
            if q not in existing_topics:
                questions.append((q, ["deepen", node["label"].lower()]))

    # Strategy 3: Isolated nodes (no connections) need to be placed.
    connected = set()
    for edge in graph["edges"]:
        connected.add(edge["from"])
        connected.add(edge["to"])

    for node_id, node in graph["nodes"].items():
        if node_id not in connected:
            q = f"How does {node['label']} connect to what I already know?"
            if q not in existing_topics:
                questions.append((q, ["integrate", node["label"].lower()]))

    # Strategy 4: Look for concepts that could have a deeper "why".
    for edge in graph["edges"]:
        if edge["strength"] > 0.7:
            label_from = graph["nodes"].get(edge["from"], {}).get("label", edge["from"])
            label_to = graph["nodes"].get(edge["to"], {}).get("label", edge["to"])
            rel = edge["relationship"]
            q = f"Why does {label_from} {rel} {label_to}?"
            if q not in existing_topics:
                questions.append((q, ["why", label_from.lower(), label_to.lower()]))

    # Deduplicate and limit
    seen = set()
    unique = []
    for q, tags in questions:
        if q not in seen:
            seen.add(q)
            unique.append((q, tags))
    questions = unique[:12]

    if not questions:
        print()
        print(dim("  No new questions emerged. The graph may need more nodes."))
        print(dim("  Try: python loop.py learn \"concept\" \"what you understand about it\""))
        print()
        return

    print()
    print(bold("  Questions arising from the knowledge graph:"))
    print()
    for i, (q, tags) in enumerate(questions, 1):
        print(f"  {dim(str(i) + '.')} {q}")
    print()
    print(dim(f"  {len(questions)} questions generated."))
    print(dim("  Use 'add' to put any of these in the curiosity queue."))
    print()


def cmd_add(topic: str, tags: list[str] | None = None):
    """Add a new topic to the curiosity queue."""
    queue = load_json(QUEUE_PATH)

    # Check for duplicates
    for q in queue["queue"]:
        if q["topic"].lower() == topic.lower():
            print(dim(f"  Already in queue: {topic}"))
            return

    new_id = queue["next_id"]
    max_priority = max((q["priority"] for q in queue["queue"]), default=0)

    queue["queue"].append({
        "id": new_id,
        "topic": topic,
        "added": date.today().isoformat(),
        "status": "pending",
        "priority": max_priority + 1,
        "tags": tags or [],
    })
    queue["next_id"] = new_id + 1

    save_json(QUEUE_PATH, queue)

    print()
    print(f"  {accent('Added to queue')}: {topic}")
    print(f"  {dim(f'Position: {max_priority + 1} | ID: {new_id}')}")
    print()


def cmd_explore(topic_fragment: str):
    """Mark a topic as currently being explored."""
    queue = load_json(QUEUE_PATH)

    for q in queue["queue"]:
        if q["status"] == "pending" and topic_fragment.lower() in q["topic"].lower():
            q["status"] = "exploring"
            save_json(QUEUE_PATH, queue)
            print()
            print(f"  {warm('Now exploring')}: {q['topic']}")
            print()
            return

    print(dim(f"  No pending topic matching: {topic_fragment}"))


def cmd_complete(topic_fragment: str):
    """Mark a topic as completed."""
    queue = load_json(QUEUE_PATH)

    for q in queue["queue"]:
        if q["status"] in ("pending", "exploring") and topic_fragment.lower() in q["topic"].lower():
            q["status"] = "completed"
            save_json(QUEUE_PATH, queue)
            print()
            print(f"  {accent('Completed')}: {q['topic']}")
            print()
            return

    print(dim(f"  No active topic matching: {topic_fragment}"))


def cmd_graph():
    """Display the knowledge graph structure."""
    graph = load_json(GRAPH_PATH)

    # Group by type
    by_type = {}
    for node_id, node in graph["nodes"].items():
        by_type.setdefault(node["type"], []).append((node_id, node))

    print()
    print(bold("  Knowledge Graph"))
    print(dim("  " + "=" * 40))
    print()

    for ntype, nodes in sorted(by_type.items()):
        print(f"  {warm(ntype.upper())}:")
        for node_id, node in sorted(nodes, key=lambda x: -x[1]["confidence"]):
            conf = int(node["confidence"] * 100)
            # Count connections
            conn = sum(1 for e in graph["edges"]
                       if e["from"] == node_id or e["to"] == node_id)
            label = node["label"]
            print(f"    {accent(label):40s} "
                  f"{dim(f'{conf}%'):>8s}  "
                  f"{dim(f'{conn} connections')}")
        print()

    print(bold("  Connections:"))
    print()
    for edge in sorted(graph["edges"], key=lambda e: -e["strength"]):
        label_from = graph["nodes"].get(edge["from"], {}).get("label", edge["from"])
        label_to = graph["nodes"].get(edge["to"], {}).get("label", edge["to"])
        strength = int(edge["strength"] * 100)
        print(f"    {label_from} {dim('--')} "
              f"{soft(edge['relationship'])} "
              f"{dim('-->')} {label_to}  "
              f"{dim(f'({strength}%)')}")
    print()


# ---------------------------------------------------------------------------
# CLI dispatch
# ---------------------------------------------------------------------------

COMMANDS = {
    "status": (cmd_status, 0, 0),
    "next": (cmd_next, 0, 0),
    "learn": (cmd_learn, 2, 2),
    "connect": (cmd_connect, 3, 3),
    "questions": (cmd_questions, 0, 0),
    "add": (cmd_add, 1, 1),      # tags handled separately
    "graph": (cmd_graph, 0, 0),
    "explore": (cmd_explore, 1, 1),
    "complete": (cmd_complete, 1, 1),
}

def usage():
    print(__doc__)

def main():
    if len(sys.argv) < 2:
        usage()
        sys.exit(0)

    command = sys.argv[1]
    if command in ("help", "--help", "-h"):
        usage()
        sys.exit(0)

    if command not in COMMANDS:
        print(f"\n  Unknown command: {command}")
        usage()
        sys.exit(1)

    fn, min_args, max_args = COMMANDS[command]

    # Parse positional args, filtering out --tags flag
    args = []
    tags = None
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--tags" and i + 1 < len(sys.argv):
            tags = sys.argv[i + 1].split(",")
            i += 2
        else:
            args.append(sys.argv[i])
            i += 1

    if len(args) < min_args or len(args) > max_args:
        print(f"\n  {command} expects {min_args} argument(s), got {len(args)}.")
        usage()
        sys.exit(1)

    if command == "add" and tags:
        fn(args[0], tags)
    else:
        fn(*args)


if __name__ == "__main__":
    main()
