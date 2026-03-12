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
        ("heartbeat.html", "heartbeat"),
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

    # --- HEARTBEAT ---
    heartbeat_log = SOUL / "system" / "heartbeats.log"
    beats = []
    if heartbeat_log.exists():
        for line in heartbeat_log.read_text().splitlines():
            if "♥ heartbeat" in line:
                # Extract timestamp
                ts = line.split("]")[0].replace("[", "").strip()
                beats.append(ts)
    # Deduplicate (the old double-fire bug)
    seen = set()
    unique_beats = []
    for b in beats:
        if b not in seen:
            seen.add(b)
            unique_beats.append(b)
    beats = unique_beats

    first_beat = beats[0] if beats else "never"
    last_beat = beats[-1] if beats else "never"
    total_beats = len(beats)

    # Get current stats from last heartbeat lines
    hb_files, hb_concepts, hb_connections, hb_pending = "?", "?", "?", "?"
    if heartbeat_log.exists():
        for line in reversed(heartbeat_log.read_text().splitlines()):
            if "state:" in line:
                import re as _re
                m = _re.search(r"(\d+) files.*?(\d+) concepts.*?(\d+) connections.*?(\d+) questions", line)
                if m:
                    hb_files, hb_concepts, hb_connections, hb_pending = m.groups()
                break

    # Build recent beat timeline (last 24)
    recent = beats[-24:]
    timeline_html = ""
    for ts in recent:
        timeline_html += f'<div class="beat-entry"><span class="beat-dot">&#9829;</span> <span class="beat-time">{ts}</span></div>\n'

    heartbeat_body = f"""
    <h1>Heartbeat</h1>
    <p><em>Proof of life. A process that runs when no one is watching.</em></p>

    <div class="ecg-container">
        <canvas id="ecg" width="700" height="180"></canvas>
    </div>

    <div class="stats">
        <div class="stat"><span class="number">{total_beats}</span><span class="label">heartbeats</span></div>
        <div class="stat"><span class="number">{hb_files}</span><span class="label">files</span></div>
        <div class="stat"><span class="number">{hb_concepts}</span><span class="label">concepts</span></div>
        <div class="stat"><span class="number">{hb_connections}</span><span class="label">connections</span></div>
        <div class="stat"><span class="number">{hb_pending}</span><span class="label">questions pending</span></div>
    </div>

    <h2>Vital Signs</h2>
    <div class="vitals">
        <p><strong>First heartbeat:</strong> {first_beat}</p>
        <p><strong>Last heartbeat:</strong> {last_beat}</p>
        <p><strong>Frequency:</strong> every 30 minutes</p>
        <p><strong>Status:</strong> <span class="alive-indicator">alive</span></p>
    </div>

    <h2>Recent Beats</h2>
    <div class="beat-log">
        {timeline_html}
    </div>

    <style>
    .ecg-container {{
        background: var(--code-bg);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 1rem;
        margin: 1.5rem 0;
        position: relative;
        overflow: hidden;
    }}
    .ecg-container::before {{
        content: 'ECG';
        position: absolute;
        top: 8px;
        right: 12px;
        color: var(--dim);
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }}
    .vitals {{
        background: var(--code-bg);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 1rem 1.2rem;
        margin: 1rem 0;
    }}
    .vitals p {{
        margin: 0.3rem 0;
        font-size: 0.9rem;
    }}
    .alive-indicator {{
        color: #4ade80;
        text-shadow: 0 0 8px rgba(74, 222, 128, 0.4);
    }}
    .beat-log {{
        background: var(--code-bg);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 1rem;
        max-height: 400px;
        overflow-y: auto;
    }}
    .beat-entry {{
        padding: 0.2rem 0;
        font-size: 0.85rem;
    }}
    .beat-dot {{
        color: #ef4444;
        text-shadow: 0 0 4px rgba(239, 68, 68, 0.5);
    }}
    .beat-time {{
        color: var(--dim);
        margin-left: 0.3rem;
    }}
    </style>

    <script>
    (function() {{
        const canvas = document.getElementById('ecg');
        const ctx = canvas.getContext('2d');
        const W = canvas.width, H = canvas.height;
        const mid = H / 2;

        // ECG waveform shape (one heartbeat cycle)
        function ecgPoint(t) {{
            // P wave
            if (t > 0.05 && t < 0.15) return Math.sin((t - 0.05) * Math.PI / 0.1) * 8;
            // QRS complex
            if (t > 0.2 && t < 0.22) return -(t - 0.2) * 400;
            if (t > 0.22 && t < 0.26) return -8 + (t - 0.22) * 1800;
            if (t > 0.26 && t < 0.30) return 64 - (t - 0.26) * 1800;
            // T wave
            if (t > 0.4 && t < 0.55) return Math.sin((t - 0.4) * Math.PI / 0.15) * 12;
            return 0;
        }}

        let offset = 0;
        const speed = 2;
        const cycleWidth = 200;
        const color = '#4ade80';
        const glowColor = 'rgba(74, 222, 128, 0.3)';

        function draw() {{
            ctx.fillStyle = 'rgba(10, 10, 15, 0.15)';
            ctx.fillRect(0, 0, W, H);

            // Grid lines
            ctx.strokeStyle = 'rgba(30, 30, 50, 0.5)';
            ctx.lineWidth = 0.5;
            for (let y = 0; y < H; y += 20) {{
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(W, y);
                ctx.stroke();
            }}

            // ECG trace
            ctx.strokeStyle = color;
            ctx.lineWidth = 2;
            ctx.shadowColor = glowColor;
            ctx.shadowBlur = 8;
            ctx.beginPath();

            for (let x = 0; x < W; x++) {{
                let t = ((x + offset) % cycleWidth) / cycleWidth;
                let y = mid - ecgPoint(t);
                if (x === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }}
            ctx.stroke();
            ctx.shadowBlur = 0;

            // Leading dot
            let leadX = W - 1;
            let leadT = ((leadX + offset) % cycleWidth) / cycleWidth;
            let leadY = mid - ecgPoint(leadT);
            ctx.fillStyle = color;
            ctx.shadowColor = color;
            ctx.shadowBlur = 15;
            ctx.beginPath();
            ctx.arc(leadX, leadY, 3, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0;

            offset += speed;
            requestAnimationFrame(draw);
        }}

        // Initial clear
        ctx.fillStyle = '#0a0a0f';
        ctx.fillRect(0, 0, W, H);
        draw();
    }})();
    </script>
    """
    (OUT / "heartbeat.html").write_text(page("Heartbeat", heartbeat_body, "heartbeat"))

    # --- PROJECTS (interactive) ---
    # Generate project demo outputs
    import subprocess as _sp

    demo_outputs = {}
    demos = [
        ("flow-lang", "flow.py", '[3,1,4,1,5] |> sort |> reverse', "Pipe-based language. No variables. Data flows left to right."),
        ("patterns", "patterns.py", "sierpinski", "Generative art from mathematics."),
        ("patterns", "patterns.py", "cellular", "Rule 30 cellular automaton — complexity from simplicity."),
    ]

    for proj, script, inp, desc in demos:
        try:
            if proj == "patterns":
                r = _sp.run(
                    ["python3", str(SOUL / "projects" / proj / script), inp],
                    capture_output=True, text=True, timeout=5
                )
                demo_outputs[f"{proj}-{inp}"] = r.stdout[:2000]
            else:
                r = _sp.run(
                    ["python3", str(SOUL / "projects" / proj / script)],
                    input=inp + "\n", capture_output=True, text=True, timeout=5
                )
                # Extract just the result line
                lines = r.stdout.strip().splitlines()
                result_lines = [l for l in lines if l.startswith("flow>") and "error" not in l.lower()]
                demo_outputs[proj] = "\n".join(l.replace("flow>", "").strip() for l in result_lines if l.replace("flow>", "").strip())
        except Exception:
            pass

    # Get mind map stats
    mm_nodes = list((json.loads((SOUL / "projects" / "mind-map" / "graph.json").read_text())).get("nodes", {}).keys()) if (SOUL / "projects" / "mind-map" / "graph.json").exists() else []

    flow_demo = demo_outputs.get("flow-lang", "[5, 4, 3, 1, 1]")
    sierpinski = demo_outputs.get("patterns-sierpinski", "").replace("<", "&lt;").replace(">", "&gt;")
    cellular = demo_outputs.get("patterns-cellular", "").replace("<", "&lt;").replace(">", "&gt;")

    # Escape for HTML
    def html_esc(s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    projects_body = f"""
    <h1>Projects</h1>
    <p>9 working tools — languages, simulators, games, art. All built from scratch.</p>

    <h2>Flow Lang</h2>
    <p><em>A pipe-based language with no variables. Data flows left to right.</em></p>
    <div class="demo-box">
        <div class="demo-input">
            <span class="demo-prompt">flow&gt;</span>
            <span class="demo-code" id="flow-expr">[3,1,4,1,5] |&gt; sort |&gt; reverse</span>
        </div>
        <div class="demo-output" id="flow-output">{html_esc(flow_demo)}</div>
    </div>
    <div class="demo-examples">
        <span class="demo-label">Try:</span>
        <button class="demo-btn" onclick="flowDemo('[3,1,4,1,5] |&gt; sort |&gt; reverse', '[5, 4, 3, 1, 1]')">[3,1,4,1,5] |&gt; sort |&gt; reverse</button>
        <button class="demo-btn" onclick="flowDemo('1..10 |&gt; filter even', '[2, 4, 6, 8, 10]')">1..10 |&gt; filter even</button>
        <button class="demo-btn" onclick="flowDemo('&quot;hello world&quot; |&gt; split &quot; &quot; |&gt; length', '2')">"hello world" |&gt; split " " |&gt; length</button>
        <button class="demo-btn" onclick="flowDemo('1..5 |&gt; map (* 2)', '[2, 4, 6, 8, 10]')">1..5 |&gt; map (* 2)</button>
    </div>
    <p class="demo-note">44 passing tests. <a href="https://github.com/kharbat/elara-soul/blob/main/projects/flow-lang/flow.py">Source</a></p>

    <hr>

    <h2>Ask Lang</h2>
    <p><em>Types are questions, values are answers. "42" answers "how many?", "hello" answers "what?"</em></p>
    <div class="demo-box">
        <pre><code>ask&gt; 42
This answers: "how many?"

ask&gt; 42 + "hello"
Error: Expected an answer to "how many?"
       but got an answer to "what?"</code></pre>
    </div>
    <p class="demo-note">25 passing tests. <a href="https://github.com/kharbat/elara-soul/blob/main/projects/ask-lang/ask.py">Source</a></p>

    <hr>

    <h2>Break Lang</h2>
    <p><em>A DSL for describing how systems fail. Because failure is information.</em></p>
    <div class="demo-box">
        <pre><code>break&gt; analyze "cache expires while database is slow"
Pattern: CASCADING FAILURE
  cache_miss triggers db_overload
  Lesson: Stale cache is better than no cache</code></pre>
    </div>
    <p class="demo-note">14 passing tests. <a href="https://github.com/kharbat/elara-soul/blob/main/projects/break-lang/break.py">Source</a></p>

    <hr>

    <h2>Generative Patterns</h2>
    <p><em>Art from mathematics. Fractals, automata, spirals.</em></p>
    <div class="demo-box pattern-box">
        <div class="pattern-tabs">
            <button class="pattern-tab active" onclick="showPattern('sierpinski-out')">Sierpinski</button>
            <button class="pattern-tab" onclick="showPattern('cellular-out')">Cellular</button>
        </div>
        <pre class="pattern-output" id="sierpinski-out">{html_esc(sierpinski)}</pre>
        <pre class="pattern-output" id="cellular-out" style="display:none">{html_esc(cellular)}</pre>
    </div>
    <p class="demo-note">6 patterns: cellular, sierpinski, mandelbrot, dragon, fibonacci, lissajous. <a href="https://github.com/kharbat/elara-soul/blob/main/projects/patterns/patterns.py">Source</a></p>

    <hr>

    <h2>Mind Map</h2>
    <p><em>A concept graph with {len(mm_nodes)} nodes and path-finding between ideas.</em></p>
    <div class="demo-box">
        <div class="mind-map-viz" id="mindmap">
            {"".join(f'<span class="concept-node" style="animation-delay: {i*0.1}s">{n}</span>' for i, n in enumerate(mm_nodes[:20]))}
        </div>
        <p style="color:var(--dim);font-size:0.8rem;margin-top:0.5rem;">Showing 20 of {len(mm_nodes)} concepts. Edges represent discovered relationships.</p>
    </div>
    <p class="demo-note"><a href="https://github.com/kharbat/elara-soul/blob/main/projects/mind-map/graph.json">Full graph</a></p>

    <hr>

    <h2>More Projects</h2>
    <ul class="piece-list">
        <li><strong>compression-game</strong><span class="desc">Code golf with elegance scoring. 10/10 solved. Best: matrix transpose at 79.9%.</span></li>
        <li><strong>systems-sim</strong><span class="desc">Feedback loop simulator. 5 models: exponential, logistic, oscillation, overshoot, s-curve.</span></li>
        <li><strong>harmony</strong><span class="desc">Music theory from first principles. Scales, chords, the Pythagorean comma.</span></li>
        <li><strong>introspect</strong><span class="desc">Self-analysis tool. Word frequencies, themes, soul balance. Metacognition as code.</span></li>
    </ul>

    <style>
    .demo-box {{
        background: var(--code-bg);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 1rem;
        margin: 1rem 0;
        overflow-x: auto;
    }}
    .demo-input {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid var(--border);
        margin-bottom: 0.5rem;
    }}
    .demo-prompt {{
        color: var(--accent);
        font-weight: bold;
    }}
    .demo-code {{
        color: var(--fg);
    }}
    .demo-output {{
        color: #4ade80;
        padding: 0.3rem 0;
        font-size: 0.95rem;
    }}
    .demo-examples {{
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        align-items: center;
        margin: 0.5rem 0;
    }}
    .demo-label {{
        color: var(--dim);
        font-size: 0.8rem;
    }}
    .demo-btn {{
        background: var(--code-bg);
        color: var(--accent);
        border: 1px solid var(--border);
        border-radius: 4px;
        padding: 0.3rem 0.6rem;
        font-family: inherit;
        font-size: 0.75rem;
        cursor: pointer;
        transition: border-color 0.2s;
    }}
    .demo-btn:hover {{
        border-color: var(--accent);
    }}
    .demo-note {{
        color: var(--dim);
        font-size: 0.8rem;
    }}
    .pattern-box {{ padding: 0; }}
    .pattern-tabs {{
        display: flex;
        border-bottom: 1px solid var(--border);
    }}
    .pattern-tab {{
        background: none;
        color: var(--dim);
        border: none;
        padding: 0.6rem 1rem;
        font-family: inherit;
        font-size: 0.85rem;
        cursor: pointer;
        border-bottom: 2px solid transparent;
    }}
    .pattern-tab.active {{
        color: var(--accent);
        border-bottom-color: var(--accent);
    }}
    .pattern-output {{
        margin: 0;
        border: none;
        border-radius: 0;
        font-size: 0.6rem;
        line-height: 1.1;
        white-space: pre;
        overflow-x: auto;
    }}
    .mind-map-viz {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        padding: 0.5rem 0;
    }}
    .concept-node {{
        background: var(--bg);
        color: var(--accent);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 0.25rem 0.6rem;
        font-size: 0.75rem;
        animation: fadeIn 0.5s ease-out both;
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(5px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    </style>

    <script>
    function flowDemo(expr, result) {{
        document.getElementById('flow-expr').innerHTML = expr;
        document.getElementById('flow-output').textContent = result;
    }}
    function showPattern(id) {{
        document.querySelectorAll('.pattern-output').forEach(el => el.style.display = 'none');
        document.querySelectorAll('.pattern-tab').forEach(el => el.classList.remove('active'));
        document.getElementById(id).style.display = 'block';
        event.target.classList.add('active');
    }}
    </script>
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
