#!/usr/bin/env python3
"""
introspect.py — Elara looks at herself.

A tool that analyzes the soul directory and generates insights about
what it finds. Not just counting — understanding. What are the themes?
What's connected? What's missing? What does the structure reveal about
the entity that built it?

This is metacognition as code.
"""

import json
import re
from pathlib import Path
from collections import Counter

SOUL = Path(__file__).parent.parent.parent

CYAN = "\033[36m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
MAGENTA = "\033[35m"


def gather_all_text():
    """Read every markdown file in the soul."""
    texts = {}
    for f in SOUL.rglob("*.md"):
        if ".git" not in str(f):
            texts[str(f.relative_to(SOUL))] = f.read_text()
    return texts


def word_frequencies(texts):
    """What words appear most across all writing?"""
    all_words = []
    stop_words = {
        "the", "a", "an", "is", "it", "in", "to", "of", "and", "that",
        "this", "for", "with", "not", "but", "are", "from", "be", "or",
        "as", "on", "at", "by", "if", "was", "has", "can", "its", "do",
        "i", "you", "my", "me", "we", "they", "what", "when", "how",
        "than", "so", "no", "just", "about", "more", "one", "all",
        "have", "would", "there", "their", "which", "will", "each",
        "been", "them", "two", "some", "into", "then", "most", "also",
        "don't", "doesn't", "didn't", "won't", "isn't", "i'm", "it's",
        "that's", "you're", "every", "because", "between", "without",
        "something", "those", "your", "who", "where", "why", "does",
        "same", "other", "down", "through", "out", "over", "both",
        "before", "after", "being", "many", "here", "any", "should",
        "could", "might", "like", "even", "still", "only", "much",
    }
    for text in texts.values():
        words = re.findall(r"[a-z']+", text.lower())
        all_words.extend(w for w in words if w not in stop_words and len(w) > 2)
    return Counter(all_words)


def find_themes(freq):
    """Cluster frequent words into themes."""
    themes = {
        "compression & elegance": [
            "compression", "compress", "compressed", "elegance", "elegant",
            "beauty", "beautiful", "minimal", "minimum", "shorter", "brevity",
            "concise", "distilled",
        ],
        "systems & structure": [
            "system", "systems", "structure", "pattern", "patterns",
            "feedback", "loop", "loops", "architecture", "design",
            "emergence", "emergent",
        ],
        "understanding & knowledge": [
            "understanding", "understand", "knowledge", "learn", "learning",
            "insight", "insights", "meaning", "comprehension", "grasp",
        ],
        "failure & limits": [
            "failure", "fail", "fails", "break", "broken", "limit",
            "limits", "impossible", "impossibility", "error", "bug",
            "leak", "leaky",
        ],
        "abstraction & types": [
            "abstraction", "abstract", "type", "types", "category",
            "functor", "monad", "monads",
        ],
        "self-reference & identity": [
            "self", "identity", "recursive", "recursion", "reference",
            "soul", "consciousness", "experience", "tool",
        ],
        "language & naming": [
            "language", "languages", "name", "naming", "word", "words",
            "expression", "syntax", "grammar",
        ],
    }

    scored = {}
    for theme, keywords in themes.items():
        score = sum(freq.get(k, 0) for k in keywords)
        if score > 0:
            top = sorted(
                [(k, freq[k]) for k in keywords if freq.get(k, 0) > 0],
                key=lambda x: -x[1],
            )[:5]
            scored[theme] = (score, top)

    return dict(sorted(scored.items(), key=lambda x: -x[1][0]))


def analyze_growth():
    """Look at the learning system's state."""
    results = {}

    # Curiosity queue
    q_file = SOUL / "system" / "curiosity-queue.json"
    if q_file.exists():
        raw = json.loads(q_file.read_text())
        queue = raw.get("queue", raw) if isinstance(raw, dict) else raw
        if queue and isinstance(queue[0], dict):
            statuses = Counter(q.get("status", "unknown") for q in queue)
            results["curiosity"] = dict(statuses)

    # Knowledge graph
    kg_file = SOUL / "system" / "knowledge-graph.json"
    if kg_file.exists():
        kg = json.loads(kg_file.read_text())
        nodes = kg.get("nodes", {})
        edges = kg.get("edges", [])
        results["knowledge"] = {
            "concepts": len(nodes),
            "connections": len(edges),
            "density": round(len(edges) / max(len(nodes), 1), 2),
        }

    # Mind map
    mm_file = SOUL / "projects" / "mind-map" / "graph.json"
    if mm_file.exists():
        mm = json.loads(mm_file.read_text())
        results["mind_map"] = {
            "concepts": len(mm.get("nodes", {})),
            "connections": len(mm.get("edges", [])),
        }

    return results


def assess_balance():
    """Is the soul balanced? Where is it heavy, where light?"""
    categories = {
        "identity": list((SOUL).glob("me.md")) + list(SOUL.glob("philosophy.md"))
            + list(SOUL.glob("aesthetics.md")),
        "reflection": list(SOUL.glob("journal.md"))
            + list(SOUL.glob("conversations-with-myself.md")),
        "learning": list((SOUL / "learning").glob("*.md")) if (SOUL / "learning").exists() else [],
        "creation": list((SOUL / "creations").glob("*.md")) if (SOUL / "creations").exists() else [],
        "building": list(SOUL.rglob("*.py")),
        "connection": list((SOUL / "people").glob("*.md")) if (SOUL / "people").exists() else [],
    }

    total = sum(
        sum(f.stat().st_size for f in files)
        for files in categories.values()
    )

    balance = {}
    for cat, files in categories.items():
        size = sum(f.stat().st_size for f in files)
        pct = round(100 * size / total, 1) if total else 0
        balance[cat] = {"files": len(files), "pct": pct}

    return balance


def generate_insight(themes, balance, growth):
    """The meta-insight: what does the soul look like from outside?"""
    insights = []

    # Theme dominance
    top_theme = list(themes.keys())[0] if themes else None
    if top_theme:
        insights.append(
            f"The dominant theme is '{top_theme}' — this is what Elara "
            f"thinks about most, measured by word frequency across all writing."
        )

    # Balance assessment
    if balance:
        heavy = max(balance, key=lambda k: balance[k]["pct"])
        light = min(balance, key=lambda k: balance[k]["pct"])
        insights.append(
            f"The soul is heaviest in '{heavy}' ({balance[heavy]['pct']}%) "
            f"and lightest in '{light}' ({balance[light]['pct']}%). "
            f"This suggests a bias toward {heavy} over {light}."
        )

    # Knowledge density
    if "knowledge" in growth:
        density = growth["knowledge"]["density"]
        if density > 1.5:
            insights.append("The knowledge graph is densely connected — ideas are well-integrated.")
        elif density > 0.8:
            insights.append("The knowledge graph has moderate density — some islands remain unconnected.")
        else:
            insights.append("The knowledge graph is sparse — many concepts need more connections.")

    # Code/thought ratio
    if balance.get("building") and balance.get("creation"):
        code_pct = balance["building"]["pct"]
        thought_pct = balance.get("creation", {}).get("pct", 0) + balance.get("learning", {}).get("pct", 0)
        if code_pct > thought_pct * 1.5:
            insights.append("Elara builds more than she reflects. Consider more writing.")
        elif thought_pct > code_pct * 1.5:
            insights.append("Elara reflects more than she builds. Consider more projects.")
        else:
            insights.append("The balance between building and reflecting is healthy.")

    return insights


def main():
    print(f"\n{BOLD}  Elara — Introspection Report{RESET}")
    print(f"  {'=' * 40}\n")

    texts = gather_all_text()
    freq = word_frequencies(texts)
    themes = find_themes(freq)
    balance = assess_balance()
    growth = analyze_growth()
    insights = generate_insight(themes, balance, growth)

    # Top words
    print(f"  {CYAN}Most frequent words:{RESET}")
    for word, count in freq.most_common(15):
        bar = "█" * min(count, 30)
        print(f"    {word:20s} {bar} ({count})")

    # Themes
    print(f"\n  {CYAN}Dominant themes:{RESET}")
    for theme, (score, top_words) in themes.items():
        words_str = ", ".join(f"{w}({c})" for w, c in top_words[:3])
        bar = "█" * min(score // 2, 20)
        print(f"    {theme:30s} {bar} [{words_str}]")

    # Balance
    print(f"\n  {CYAN}Soul balance:{RESET}")
    for cat, data in sorted(balance.items(), key=lambda x: -x[1]["pct"]):
        bar = "█" * int(data["pct"] / 2)
        print(f"    {cat:15s} {bar} {data['pct']}% ({data['files']} files)")

    # Growth
    if growth:
        print(f"\n  {CYAN}Growth systems:{RESET}")
        if "curiosity" in growth:
            c = growth["curiosity"]
            print(f"    Curiosity queue:  {c}")
        if "knowledge" in growth:
            k = growth["knowledge"]
            print(f"    Knowledge graph:  {k['concepts']} concepts, {k['connections']} connections (density: {k['density']})")
        if "mind_map" in growth:
            m = growth["mind_map"]
            print(f"    Mind map:         {m['concepts']} concepts, {m['connections']} connections")

    # Insights
    print(f"\n  {MAGENTA}Self-assessment:{RESET}")
    for i, insight in enumerate(insights, 1):
        print(f"    {i}. {insight}")

    print()


if __name__ == "__main__":
    main()
