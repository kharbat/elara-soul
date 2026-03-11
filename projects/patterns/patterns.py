#!/usr/bin/env python3
"""
patterns.py — Generative art from mathematical structures.

Elara's creative tool: beauty from minimalism.
Each pattern emerges from a simple rule applied recursively or iteratively,
producing complexity from almost nothing.
"""

import sys
import math
import random

# ─── Character palettes ──────────────────────────────────────────────────────

DENSITY = " ░▒▓█"                          # Light to dense, for gradients
BLOCK = ("█", "░")                          # Binary: filled / empty
BOX = {"h": "─", "v": "│", "tl": "┌", "tr": "┐", "bl": "└", "br": "┘",
       "lj": "├", "rj": "┤", "tj": "┬", "bj": "┴", "x": "┼"}


# ─── Cellular Automaton ──────────────────────────────────────────────────────
# A 1D cellular automaton: each cell's next state is determined by its current
# state and its two neighbors. The rule number (0-255) encodes all 8 possible
# 3-cell neighborhoods as bits. Rule 30 produces chaos; Rule 110 is Turing-complete.

def cellular(rule=30, width=79, steps=40):
    """Evolve a 1D cellular automaton and render each generation."""
    rule, width, steps = int(rule), int(width), int(steps)
    row = [0] * width
    row[width // 2] = 1                     # Single seed in the center
    lines = []
    for _ in range(steps):
        lines.append("".join(BLOCK[0] if c else BLOCK[1] for c in row))
        # 3-cell neighborhood forms a 3-bit index into the rule's binary representation
        row = [(rule >> ((row[(i-1) % width] << 2) | (row[i] << 1)
                | row[(i+1) % width])) & 1 for i in range(width)]
    return "\n".join(lines)


# ─── Sierpinski Triangle ─────────────────────────────────────────────────────
# Pascal's triangle mod 2: C(n,k) mod 2 is 1 iff (k & n) == k (Lucas' theorem).
# The result is a Sierpinski triangle — a fractal with Hausdorff dimension log2(3).

def sierpinski(size=32):
    """Generate a Sierpinski triangle via Pascal's triangle mod 2."""
    size = int(size)
    lines = []
    for n in range(size):
        padding = " " * (size - n - 1)
        cells = "".join("▲ " if (k & n) == k else "  " for k in range(n + 1))
        lines.append(padding + cells.rstrip())
    return "\n".join(lines)


# ─── Mandelbrot Set ──────────────────────────────────────────────────────────
# For each c in the complex plane, iterate z = z² + c from z = 0.
# If |z| stays bounded, c is in the set. Escape speed determines shading.

def mandelbrot(width=80, height=36):
    """Render the Mandelbrot set using density characters."""
    width, height = int(width), int(height)
    max_iter = len(DENSITY) * 8
    x_min, x_max, y_min, y_max = -2.2, 0.8, -1.2, 1.2
    lines = []
    for row in range(height):
        line = []
        ci = y_min + (y_max - y_min) * row / height
        for col in range(width):
            cr = x_min + (x_max - x_min) * col / width
            z, c, it = 0j, complex(cr, ci), 0
            while abs(z) <= 2 and it < max_iter:
                z = z * z + c
                it += 1
            line.append(DENSITY[min(it * (len(DENSITY)-1) // max_iter, len(DENSITY)-1)])
        lines.append("".join(line))
    return "\n".join(lines)


# ─── Dragon Curve ─────────────────────────────────────────────────────────────
# An L-system fractal: start with "FX", apply X->X+YF+, Y->-FX-Y.
# F = forward, +/- = turn right/left 90°. The path never self-crosses.

def dragon(iterations=12):
    """Generate a dragon curve via L-system and render with box-drawing."""
    iterations = int(iterations)
    # Build turn sequence: S becomes S + R + reverse(flip(S))
    turns = []
    for _ in range(iterations):
        turns = turns + [1] + [1 - t for t in reversed(turns)]

    # Walk the path
    dx, dy = [1, 0, -1, 0], [0, 1, 0, -1]  # E, S, W, N
    d, x, y = 0, 0, 0
    points, segments = [(0, 0)], []
    for turn in turns:
        d = (d + (1 if turn else -1)) % 4
        nx, ny = x + dx[d], y + dy[d]
        segments.append(((x, y), (nx, ny)))
        x, y = nx, ny
        points.append((x, y))

    # Bounding box and grid (2x horizontal scale for aspect ratio)
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    ox, oy = min(xs), min(ys)
    grid_w, grid_h = (max(xs)-ox)*2 + 3, (max(ys)-oy) + 2
    grid = [[" "]*grid_w for _ in range(grid_h)]

    # Draw segments
    for (x1, y1), (x2, y2) in segments:
        gx1, gy1 = (x1-ox)*2+1, y1-oy
        gx2, gy2 = (x2-ox)*2+1, y2-oy
        if gy1 == gy2:
            for gx in range(min(gx1, gx2), max(gx1, gx2)+1):
                grid[gy1][gx] = BOX["x"] if grid[gy1][gx] in (BOX["v"], BOX["x"]) else BOX["h"]
        else:
            for gy in range(min(gy1, gy2), max(gy1, gy2)+1):
                grid[gy][gx1] = BOX["x"] if grid[gy][gx1] in (BOX["h"], BOX["x"]) else BOX["v"]

    # Place junction characters at vertices
    _j = {(0,1,0,1): "tl", (0,1,1,0): "tr", (1,0,0,1): "bl", (1,0,1,0): "br",
           (1,1,0,0): "v", (0,0,1,1): "h", (1,1,1,1): "x",
           (1,1,1,0): "rj", (1,1,0,1): "lj", (1,0,1,1): "bj", (0,1,1,1): "tj"}
    for (x1, y1), (x2, y2) in segments:
        for px, py in [(x1, y1), (x2, y2)]:
            gx, gy = (px-ox)*2+1, py-oy
            n = (int(gy > 0 and grid[gy-1][gx] in (BOX["v"], BOX["x"])),
                 int(gy < grid_h-1 and grid[gy+1][gx] in (BOX["v"], BOX["x"])),
                 int(gx > 0 and grid[gy][gx-1] in (BOX["h"], BOX["x"])),
                 int(gx < grid_w-1 and grid[gy][gx+1] in (BOX["h"], BOX["x"])))
            if n in _j:
                grid[gy][gx] = BOX[_j[n]]

    return "\n".join("".join(r).rstrip() for r in grid)


# ─── Fibonacci Spiral ────────────────────────────────────────────────────────
# The Fibonacci sequence governs proportions found in shells, galaxies, flowers.
# Each quarter-arc spans one Fibonacci number, approximating a logarithmic spiral.

def fibonacci_spiral(size=8):
    """Approximate a Fibonacci spiral by drawing quarter-arcs in a grid."""
    size = int(size)
    fibs = [1, 1]
    while len(fibs) < size:
        fibs.append(fibs[-1] + fibs[-2])

    total = sum(fibs)
    grid = [[" "] * (total * 2) for _ in range(total * 2)]
    cx, cy = total, total
    # Center shifts per direction: (cx_delta, cy_delta, cx_next, cy_next)
    shifts = [(1,0,0,1), (0,1,-1,0), (-1,0,0,-1), (0,-1,1,0)]

    for idx, f in enumerate(fibs):
        d = idx % 4
        start_angle = [math.pi, 3*math.pi/2, 0, math.pi/2][d]
        for step in range(max(f*20, 60) + 1):
            angle = start_angle + (math.pi/2) * step / max(f*20, 60)
            px, py = int(round(cx + f*math.cos(angle))), int(round(cy + f*math.sin(angle)))
            if 0 <= py < len(grid) and 0 <= px < len(grid[0]):
                grid[py][px] = "●"
        s = shifts[d]
        cx += s[0] * f + (s[2] * f if idx+1 < len(fibs) else 0)
        cy += s[1] * f + (s[3] * f if idx+1 < len(fibs) else 0)

    # Trim empty space
    lines = ["".join(r).rstrip() for r in grid if "".join(r).strip()]
    if not lines:
        return "(empty)"
    indent = min(len(l) - len(l.lstrip()) for l in lines if l.strip())
    return "\n".join(l[indent:] for l in lines)


# ─── Lissajous Curve ─────────────────────────────────────────────────────────
# Lissajous figures: x = sin(at + d), y = sin(bt). The ratio a:b determines
# the shape. These curves appear on oscilloscopes and in harmonic motion.

def lissajous(a=3, b=2, width=60, height=30):
    """Draw a Lissajous curve with the given frequency ratio."""
    a, b, width, height = int(a), int(b), int(width), int(height)
    grid = [[" "] * width for _ in range(height)]
    delta = math.pi / 4
    for i in range(1000):
        t = 2 * math.pi * i / 1000
        col = int((math.sin(a*t + delta) + 1) / 2 * (width - 1))
        row = int((math.sin(b*t) + 1) / 2 * (height - 1))
        grid[row][col] = "●"
    return "\n".join("".join(r).rstrip() for r in grid)


# ─── Gallery & Random ─────────────────────────────────────────────────────────

PATTERNS = {
    "cellular":         (cellular,         "1D Cellular Automaton"),
    "sierpinski":       (sierpinski,       "Sierpinski Triangle"),
    "mandelbrot":       (mandelbrot,       "Mandelbrot Set"),
    "dragon":           (dragon,           "Dragon Curve"),
    "fibonacci-spiral": (fibonacci_spiral, "Fibonacci Spiral"),
    "lissajous":        (lissajous,        "Lissajous Curve"),
}


def banner(title):
    """A framed title line."""
    pad = (78 - len(title)) // 2
    return f"┌{'─'*78}┐\n│{' '*pad}{title}{' '*(78-pad-len(title))}│\n└{'─'*78}┘"


def gallery():
    """Show one of each pattern — a sampler of mathematical beauty."""
    configs = {"cellular": (30, 78, 30), "sierpinski": (31,), "mandelbrot": (78, 30),
               "dragon": (10,), "fibonacci-spiral": (7,), "lissajous": (3, 2, 60, 24)}
    sections = []
    for name in ["cellular", "sierpinski", "mandelbrot", "dragon", "fibonacci-spiral", "lissajous"]:
        func, title = PATTERNS[name]
        sections.extend([banner(title), func(*configs[name]), ""])
    return "\n".join(sections)


def pick_random():
    """Choose a random pattern with random (sensible) parameters."""
    choice = random.choice(list(PATTERNS.keys()))
    func, title = PATTERNS[choice]
    configs = {
        "cellular":         lambda: (random.choice([30, 54, 60, 90, 110, 150, 182]), 79, 40),
        "sierpinski":       lambda: (random.choice([16, 31, 32, 48, 63]),),
        "mandelbrot":       lambda: (80, 36),
        "dragon":           lambda: (random.randint(8, 13),),
        "fibonacci-spiral": lambda: (random.randint(6, 9),),
        "lissajous":        lambda: (random.randint(1, 5), random.randint(1, 5), 60, 28),
    }
    args = configs[choice]()
    return banner(f"{title} (random)") + "\n" + func(*args)


# ─── CLI ──────────────────────────────────────────────────────────────────────

USAGE = f"""\
{banner("patterns.py — generative art from mathematical structures")}

Usage:
  python patterns.py cellular <rule> [width] [steps]    1D cellular automaton
  python patterns.py sierpinski [size]                   Sierpinski triangle
  python patterns.py mandelbrot [width] [height]         Mandelbrot set
  python patterns.py dragon [iterations]                 Dragon curve (L-system)
  python patterns.py fibonacci-spiral [size]             Fibonacci spiral
  python patterns.py lissajous [a] [b] [width] [height] Lissajous curve
  python patterns.py random                              Random pattern
  python patterns.py gallery                             One of each

Characters: {DENSITY}  {''.join(BOX.values())}  ▲ ●
"""


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help", "help"):
        print(USAGE)
        return
    command = args[0]
    if command == "random":
        print(pick_random())
    elif command == "gallery":
        print(gallery())
    elif command in PATTERNS:
        func, title = PATTERNS[command]
        try:
            print(banner(title))
            print(func(*args[1:]))
        except TypeError as e:
            print(f"Error: {e}", file=sys.stderr)
            print(USAGE, file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Unknown pattern: {command}\n", file=sys.stderr)
        print(USAGE, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
