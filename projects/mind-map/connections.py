#!/usr/bin/env python3
"""
connections.py — A tool for exploring relationships between ideas.

Elara's mind map. Not a graph database — a thinking tool.
Concepts are nodes, insights are edges. The interesting part
isn't any single node, it's the paths between them.
"""

import json
import sys
import random
from pathlib import Path
from collections import defaultdict
from itertools import combinations

DATA_FILE = Path(__file__).parent / "graph.json"


def load():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return {"nodes": {}, "edges": []}


def save(graph):
    DATA_FILE.write_text(json.dumps(graph, indent=2))


def add_node(graph, name, description="", tags=None):
    graph["nodes"][name] = {
        "description": description,
        "tags": tags or [],
        "connections": 0,
    }
    # update connection counts
    for e in graph["edges"]:
        if name in (e["from"], e["to"]):
            graph["nodes"][name]["connections"] += 1
    save(graph)
    print(f"  + {name}")


def connect(graph, a, b, relationship):
    for n in (a, b):
        if n not in graph["nodes"]:
            add_node(graph, n)
    graph["edges"].append({"from": a, "to": b, "rel": relationship})
    graph["nodes"][a]["connections"] = graph["nodes"][a].get("connections", 0) + 1
    graph["nodes"][b]["connections"] = graph["nodes"][b].get("connections", 0) + 1
    save(graph)
    print(f"  {a} --[{relationship}]--> {b}")


def neighbors(graph, name):
    result = []
    for e in graph["edges"]:
        if e["from"] == name:
            result.append((e["to"], e["rel"], "->"))
        elif e["to"] == name:
            result.append((e["from"], e["rel"], "<-"))
    return result


def path_between(graph, start, end, visited=None):
    """BFS to find shortest path between two concepts."""
    if start == end:
        return [start]
    visited = visited or set()
    queue = [(start, [start])]
    visited.add(start)
    while queue:
        current, path = queue.pop(0)
        for neighbor, rel, _ in neighbors(graph, current):
            if neighbor == end:
                return path + [neighbor]
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return None


def lonely_nodes(graph):
    """Nodes with fewer than 2 connections — they need more thinking."""
    return [
        name for name, data in graph["nodes"].items()
        if data.get("connections", 0) < 2
    ]


def suggest_connections(graph):
    """Find pairs of unconnected nodes that share a tag — potential insights."""
    suggestions = []
    for (a, a_data), (b, b_data) in combinations(graph["nodes"].items(), 2):
        shared_tags = set(a_data.get("tags", [])) & set(b_data.get("tags", []))
        if shared_tags:
            # check if already connected
            already = any(
                (e["from"] == a and e["to"] == b) or
                (e["from"] == b and e["to"] == a)
                for e in graph["edges"]
            )
            if not already:
                suggestions.append((a, b, shared_tags))
    return suggestions


def wander(graph, start=None, steps=5):
    """Random walk through the graph. For serendipity."""
    if not graph["nodes"]:
        print("  (empty mind)")
        return
    current = start or random.choice(list(graph["nodes"].keys()))
    path = [current]
    for _ in range(steps):
        nbrs = neighbors(graph, current)
        if not nbrs:
            break
        next_node, rel, direction = random.choice(nbrs)
        path.append(f"--[{rel}]-->  {next_node}" if direction == "->" else f"<--[{rel}]--  {next_node}")
        current = next_node
    print("  " + "\n  ".join(path))


def status(graph):
    n = len(graph["nodes"])
    e = len(graph["edges"])
    lonely = lonely_nodes(graph)
    suggestions = suggest_connections(graph)
    print(f"\n  Elara's Mind Map")
    print(f"  {'=' * 30}")
    print(f"  {n} concepts, {e} connections")
    if lonely:
        print(f"\n  Under-connected ({len(lonely)}):")
        for name in lonely[:5]:
            print(f"    - {name}")
    if suggestions:
        print(f"\n  Potential connections ({len(suggestions)}):")
        for a, b, tags in suggestions[:3]:
            print(f"    ? {a} <-> {b}  (shared: {', '.join(tags)})")
    print()


def show(graph, name):
    if name not in graph["nodes"]:
        print(f"  '{name}' not found")
        return
    data = graph["nodes"][name]
    print(f"\n  {name}")
    if data.get("description"):
        print(f"  {data['description']}")
    if data.get("tags"):
        print(f"  tags: {', '.join(data['tags'])}")
    nbrs = neighbors(graph, name)
    if nbrs:
        print(f"  connections:")
        for other, rel, direction in nbrs:
            arrow = "->" if direction == "->" else "<-"
            print(f"    {arrow} {other} ({rel})")
    print()


USAGE = """
  connections.py — Elara's mind map

  Commands:
    status                          Overview of the graph
    add <name> [desc] [tag,tag]     Add a concept
    connect <a> <b> <relationship>  Connect two concepts
    show <name>                     Show a concept and its connections
    path <from> <to>                Find path between concepts
    wander [start] [steps]          Random walk for serendipity
    suggest                         Find potential new connections
    lonely                          Show under-connected concepts
""".strip()


def main():
    args = sys.argv[1:]
    if not args:
        print(USAGE)
        return

    graph = load()
    cmd = args[0]

    match cmd:
        case "status":
            status(graph)
        case "add" if len(args) >= 2:
            tags = args[3].split(",") if len(args) > 3 else []
            add_node(graph, args[1], args[2] if len(args) > 2 else "", tags)
        case "connect" if len(args) >= 4:
            connect(graph, args[1], args[2], " ".join(args[3:]))
        case "show" if len(args) >= 2:
            show(graph, " ".join(args[1:]))
        case "path" if len(args) >= 3:
            p = path_between(graph, args[1], args[2])
            if p:
                print(f"  {' -> '.join(p)}")
            else:
                print(f"  No path from {args[1]} to {args[2]}")
        case "wander":
            start = args[1] if len(args) > 1 else None
            steps = int(args[2]) if len(args) > 2 else 5
            wander(graph, start, steps)
        case "suggest":
            for a, b, tags in suggest_connections(graph):
                print(f"  ? {a} <-> {b}  (shared: {', '.join(tags)})")
        case "lonely":
            for name in lonely_nodes(graph):
                print(f"  - {name} ({graph['nodes'][name].get('connections', 0)} connections)")
        case _:
            print(USAGE)


if __name__ == "__main__":
    main()
