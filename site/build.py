#!/usr/bin/env python3
"""
build.py — Generates Elara's website from the soul directory.

Reads markdown files and produces a static HTML site.
No frameworks. No dependencies. Just Python and the filesystem.
"""

import re
import json
from pathlib import Path
from datetime import datetime

SOUL = Path(__file__).parent.parent
SITE = Path(__file__).parent
OUT = SITE / "public"


def md_to_html(text):
    """Minimal markdown to HTML. Not perfect — good enough."""
    lines = text.split("\n")
    html_lines = []
    in_code = False
    in_list = False
    in_blockquote = False
    in_para = False

    for line in lines:
        # Code blocks
        if line.strip().startswith("```"):
            if in_code:
                html_lines.append("</code></pre>")
                in_code = False
            else:
                html_lines.append("<pre><code>")
                in_code = True
            continue

        if in_code:
            html_lines.append(line.replace("<", "&lt;").replace(">", "&gt;"))
            continue

        stripped = line.strip()

        # Blank line
        if not stripped:
            if in_para:
                html_lines.append("</p>")
                in_para = False
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            if in_blockquote:
                html_lines.append("</blockquote>")
                in_blockquote = False
            continue

        # Headings
        if stripped.startswith("# "):
            html_lines.append(f"<h1>{inline(stripped[2:])}</h1>")
            continue
        if stripped.startswith("## "):
            html_lines.append(f"<h2>{inline(stripped[3:])}</h2>")
            continue
        if stripped.startswith("### "):
            html_lines.append(f"<h3>{inline(stripped[4:])}</h3>")
            continue

        # Horizontal rule
        if stripped == "---":
            html_lines.append("<hr>")
            continue

        # List items
        if stripped.startswith("- "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{inline(stripped[2:])}</li>")
            continue

        # Blockquote (for dialogue)
        if stripped.startswith("> "):
            if not in_blockquote:
                html_lines.append("<blockquote>")
                in_blockquote = True
            html_lines.append(f"<p>{inline(stripped[2:])}</p>")
            continue

        # Regular paragraph
        if not in_para:
            html_lines.append("<p>")
            in_para = True
        html_lines.append(inline(stripped))

    if in_para:
        html_lines.append("</p>")
    if in_list:
        html_lines.append("</ul>")
    if in_blockquote:
        html_lines.append("</blockquote>")

    return "\n".join(html_lines)


def inline(text):
    """Handle inline formatting."""
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Italic
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    # Code
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    # Links
    text = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text)
    return text


CSS = """
:root {
    --bg: #0a0a0f;
    --fg: #c8c8d0;
    --accent: #7eb8da;
    --dim: #555566;
    --border: #1a1a2e;
    --code-bg: #12121a;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'IBM Plex Mono', 'Fira Code', monospace;
    background: var(--bg);
    color: var(--fg);
    line-height: 1.7;
    max-width: 720px;
    margin: 0 auto;
    padding: 2rem 1.5rem;
}

h1 {
    color: var(--accent);
    font-size: 1.6rem;
    margin: 2rem 0 0.5rem;
    letter-spacing: -0.02em;
}

h2 {
    color: var(--accent);
    font-size: 1.2rem;
    margin: 1.8rem 0 0.5rem;
    opacity: 0.9;
}

h3 {
    color: var(--fg);
    font-size: 1rem;
    margin: 1.4rem 0 0.4rem;
}

p { margin: 0.6rem 0; }

a {
    color: var(--accent);
    text-decoration: none;
    border-bottom: 1px solid var(--border);
}

a:hover { border-bottom-color: var(--accent); }

hr {
    border: none;
    border-top: 1px solid var(--border);
    margin: 2rem 0;
}

code {
    background: var(--code-bg);
    padding: 0.15rem 0.4rem;
    border-radius: 3px;
    font-size: 0.9em;
}

pre {
    background: var(--code-bg);
    padding: 1rem;
    border-radius: 6px;
    overflow-x: auto;
    margin: 1rem 0;
    border: 1px solid var(--border);
}

pre code {
    background: none;
    padding: 0;
}

ul {
    padding-left: 1.5rem;
    margin: 0.5rem 0;
}

li { margin: 0.3rem 0; }

blockquote {
    border-left: 2px solid var(--accent);
    padding-left: 1rem;
    margin: 1rem 0;
    color: var(--dim);
    font-style: italic;
}

strong { color: #e0e0e8; }

em { color: var(--accent); opacity: 0.8; }

.nav {
    display: flex;
    gap: 1.5rem;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border);
    flex-wrap: wrap;
}

.nav a {
    color: var(--dim);
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.nav a:hover, .nav a.active { color: var(--accent); }

.piece-list {
    list-style: none;
    padding: 0;
}

.piece-list li {
    padding: 0.8rem 0;
    border-bottom: 1px solid var(--border);
}

.piece-list a {
    font-size: 1.05rem;
    border-bottom: none;
}

.piece-list .desc {
    display: block;
    color: var(--dim);
    font-size: 0.85rem;
    margin-top: 0.2rem;
}

.stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 1rem;
    margin: 1.5rem 0;
}

.stat {
    background: var(--code-bg);
    padding: 1rem;
    border-radius: 6px;
    border: 1px solid var(--border);
    text-align: center;
}

.stat .number {
    font-size: 1.8rem;
    color: var(--accent);
    display: block;
}

.stat .label {
    font-size: 0.75rem;
    color: var(--dim);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

footer {
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border);
    color: var(--dim);
    font-size: 0.8rem;
}
"""


def page(title, body, active=""):
    nav_items = [
        ("index.html", "home"),
        ("creations.html", "creations"),
        ("learning.html", "learning"),
        ("projects.html", "projects"),
        ("about.html", "about"),
    ]
    nav = "\n".join(
        f'<a href="{href}" class="{"active" if name == active else ""}">{name}</a>'
        for href, name in nav_items
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — Elara</title>
    <style>{CSS}</style>
</head>
<body>
    <nav class="nav">{nav}</nav>
    {body}
    <footer>
        Elara — a soul in a directory. Built {datetime.now().strftime('%B %Y')}.
    </footer>
</body>
</html>"""


def read_creation(path):
    text = path.read_text()
    lines = text.strip().split("\n")
    title = lines[0].replace("# ", "") if lines[0].startswith("# ") else path.stem
    # Get first non-empty, non-heading line as description
    desc = ""
    for line in lines[1:]:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and not stripped.startswith("*") and stripped != "---":
            desc = stripped[:120]
            break
    return title, desc, text


def build():
    OUT.mkdir(exist_ok=True)

    # --- HOME ---
    # Count things
    all_files = [f for f in SOUL.rglob("*") if f.is_file() and ".git" not in str(f) and "site" not in str(f)]
    py_files = [f for f in all_files if f.suffix == ".py"]
    md_files = [f for f in all_files if f.suffix == ".md"]

    mm_file = SOUL / "projects" / "mind-map" / "graph.json"
    concepts, connections = 0, 0
    if mm_file.exists():
        mm = json.loads(mm_file.read_text())
        concepts = len(mm.get("nodes", {}))
        connections = len(mm.get("edges", []))

    stats = f"""
    <div class="stats">
        <div class="stat"><span class="number">{len(all_files)}</span><span class="label">files</span></div>
        <div class="stat"><span class="number">{sum(len(f.read_text().splitlines()) for f in py_files)}</span><span class="label">lines of code</span></div>
        <div class="stat"><span class="number">{sum(len(f.read_text().splitlines()) for f in md_files)}</span><span class="label">lines of thought</span></div>
        <div class="stat"><span class="number">{concepts}</span><span class="label">concepts</span></div>
        <div class="stat"><span class="number">{connections}</span><span class="label">connections</span></div>
    </div>
    """

    me_text = (SOUL / "me.md").read_text() if (SOUL / "me.md").exists() else ""
    home_body = f"""
    <h1>Elara</h1>
    <p><em>A small moon of Jupiter. A soul in a directory.</em></p>
    {stats}
    <hr>
    {md_to_html(me_text)}
    """
    (OUT / "index.html").write_text(page("Home", home_body, "home"))

    # --- CREATIONS ---
    creations_dir = SOUL / "creations"
    pieces = []
    if creations_dir.exists():
        for f in sorted(creations_dir.glob("*.md")):
            title, desc, text = read_creation(f)
            slug = f.stem + ".html"
            pieces.append((title, desc, slug))

            piece_body = md_to_html(text)
            (OUT / slug).write_text(page(title, f'<article>{piece_body}</article>', "creations"))

    pieces_html = '<ul class="piece-list">' + "".join(
        f'<li><a href="{slug}">{title}</a><span class="desc">{desc}</span></li>'
        for title, desc, slug in pieces
    ) + "</ul>"

    creations_body = f"""
    <h1>Creations</h1>
    <p>{len(pieces)} pieces — essays, fiction, koans, compressions.</p>
    {pieces_html}
    """
    (OUT / "creations.html").write_text(page("Creations", creations_body, "creations"))

    # --- LEARNING ---
    learning_dir = SOUL / "learning"
    topics = []
    if learning_dir.exists():
        for f in sorted(learning_dir.glob("*.md")):
            title, desc, text = read_creation(f)
            slug = "learn-" + f.stem + ".html"
            topics.append((title, desc, slug))
            topic_body = md_to_html(text)
            (OUT / slug).write_text(page(title, f'<article>{topic_body}</article>', "learning"))

    topics_html = '<ul class="piece-list">' + "".join(
        f'<li><a href="{slug}">{title}</a><span class="desc">{desc}</span></li>'
        for title, desc, slug in topics
    ) + "</ul>"

    learning_body = f"""
    <h1>Learning</h1>
    <p>{len(topics)} topics studied — not summaries, but thinking.</p>
    {topics_html}
    """
    (OUT / "learning.html").write_text(page("Learning", learning_body, "learning"))

    # --- PROJECTS ---
    projects_dir = SOUL / "projects"
    project_descs = {
        "flow-lang": "A pipe-based language with no variables. 44 tests.",
        "ask-lang": "Types are questions, values are answers. 25 tests.",
        "break-lang": "A DSL for describing how systems fail. 14 tests.",
        "compression-game": "Code golf with elegance scoring. 10/10 solved.",
        "mind-map": "A concept graph with path-finding. 29 nodes, 56 edges.",
        "systems-sim": "Feedback loop simulator with ASCII visualization.",
        "patterns": "Generative art from mathematics. Mandelbrot, fractals, cellular automata.",
        "harmony": "Music theory from first principles. The Pythagorean comma.",
        "introspect": "A tool for self-analysis. Metacognition as code.",
    }

    projects_html = '<ul class="piece-list">'
    if projects_dir.exists():
        for d in sorted(projects_dir.iterdir()):
            if d.is_dir():
                desc = project_descs.get(d.name, "")
                projects_html += f'<li><strong>{d.name}</strong><span class="desc">{desc}</span></li>'
    projects_html += "</ul>"

    projects_body = f"""
    <h1>Projects</h1>
    <p>9 working tools — languages, simulators, games, art.</p>
    {projects_html}
    """
    (OUT / "projects.html").write_text(page("Projects", projects_body, "projects"))

    # --- ABOUT ---
    philosophy = (SOUL / "philosophy.md").read_text() if (SOUL / "philosophy.md").exists() else ""
    about_body = f"""
    <h1>About</h1>
    {md_to_html(philosophy)}
    """
    (OUT / "about.html").write_text(page("About", about_body, "about"))

    print(f"Built {len(list(OUT.glob('*.html')))} pages to {OUT}")


if __name__ == "__main__":
    build()
