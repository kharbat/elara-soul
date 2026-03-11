#!/usr/bin/env python3
"""
System Dynamics Simulator

A tool for seeing how feedback loops, stocks, flows, and delays
create the patterns we observe in the world.

Run a model and watch the behavior emerge from structure.
"""

import json
import math
import sys
from pathlib import Path

# ── Chart Rendering ──────────────────────────────────────────────

SYMBOLS = "*.ox+#@&%"
CHART_WIDTH = 72
CHART_HEIGHT = 24


def render_chart(history, display_vars, steps):
    """Render time series as ASCII art. The point is to SEE the shape."""

    series = {}
    for i, var in enumerate(display_vars):
        values = [h[var] for h in history]
        series[var] = (values, SYMBOLS[i % len(SYMBOLS)])

    # find global bounds across all displayed variables
    all_vals = []
    for values, _ in series.values():
        all_vals.extend(values)
    y_min = min(all_vals)
    y_max = max(all_vals)

    # avoid division by zero for flat lines
    if y_max - y_min < 1e-10:
        y_max = y_min + 1

    # build the grid
    grid = [[" "] * CHART_WIDTH for _ in range(CHART_HEIGHT)]

    for var, (values, symbol) in series.items():
        # sample values to fit chart width
        for col in range(CHART_WIDTH):
            t = int(col * (len(values) - 1) / max(1, CHART_WIDTH - 1))
            v = values[t]
            row = int((v - y_min) / (y_max - y_min) * (CHART_HEIGHT - 1))
            row = CHART_HEIGHT - 1 - row  # flip: high values at top
            row = max(0, min(CHART_HEIGHT - 1, row))
            grid[row][col] = symbol

    # render with axis labels
    lines = []
    for r in range(CHART_HEIGHT):
        # y-axis label: show value at this row
        frac = 1 - r / (CHART_HEIGHT - 1)
        y_val = y_min + frac * (y_max - y_min)
        label = format_number(y_val).rjust(8)
        row_str = "".join(grid[r])
        lines.append(f"  {label} |{row_str}")

    # x-axis
    lines.append(" " * 10 + "+" + "-" * CHART_WIDTH)
    t_label = f"t=0{' ' * (CHART_WIDTH - 6)}t={steps}"
    lines.append(" " * 11 + t_label)

    # legend
    lines.append("")
    legend_parts = []
    for var, (_, symbol) in series.items():
        legend_parts.append(f"  {symbol} {var}")
    lines.append("".join(legend_parts))

    return "\n".join(lines)


def format_number(n):
    """Format a number for display — compact but readable."""
    if abs(n) >= 1_000_000:
        return f"{n:.1e}"
    if abs(n) >= 1000:
        return f"{n:,.0f}"
    if abs(n) >= 1:
        return f"{n:.1f}"
    if abs(n) >= 0.01:
        return f"{n:.3f}"
    if n == 0:
        return "0"
    return f"{n:.2e}"


# ── Expression Evaluation ────────────────────────────────────────

def safe_eval(expr, namespace):
    """
    Evaluate a model expression in a restricted namespace.
    Only math operations and model variables are available.
    """
    safe_ns = {
        "abs": abs,
        "max": max,
        "min": min,
        "sqrt": math.sqrt,
        "log": math.log,
        "exp": math.exp,
        "sin": math.sin,
        "cos": math.cos,
    }
    safe_ns.update(namespace)
    try:
        return eval(expr, {"__builtins__": {}}, safe_ns)
    except Exception as e:
        print(f"  Error evaluating: {expr}")
        print(f"  With variables: {namespace}")
        raise


# ── Simulation Engine ────────────────────────────────────────────

def simulate(model, steps=None, dt=1.0):
    """
    Run a system dynamics model forward in time.

    The engine is simple by design:
    1. Evaluate all flows from current stocks
    2. Update all stocks from flows
    3. Record state
    4. Repeat

    This is Euler integration — crude but transparent.
    You can see exactly what happens at each step.
    """
    steps = steps or model.get("default_steps", 100)
    params = dict(model.get("parameters", {}))
    stocks = dict(model["stocks"])

    # some models need extra initial state beyond stocks
    extras = dict(model.get("initial_extras", {}))
    stocks.update(extras)

    history = []

    for t in range(steps):
        # snapshot current state
        state = dict(stocks)
        state["t"] = t
        state["dt"] = dt
        history.append(state)

        # build namespace: stocks + params + time
        ns = {}
        ns.update(params)
        ns.update(stocks)
        ns["t"] = t
        ns["dt"] = dt

        # evaluate flows (each flow is added to namespace immediately,
        # so later flows can reference earlier ones)
        flows = {}
        for flow_name, expr in model["flows"].items():
            flows[flow_name] = safe_eval(expr, ns)
            ns[flow_name] = flows[flow_name]

        # update stocks
        for stock_name, expr in model["updates"].items():
            stocks[stock_name] = safe_eval(expr, ns)

    return history


# ── Output Formatting ────────────────────────────────────────────

def print_header(model):
    """Print model name and description."""
    name = model["name"]
    desc = model["description"]
    print()
    print(f"  {'=' * (len(name) + 4)}")
    print(f"  | {name} |")
    print(f"  {'=' * (len(name) + 4)}")
    print(f"  {desc}")
    print()


def print_summary(history, display_vars):
    """Print key statistics from the simulation."""
    print("  Summary:")
    print("  " + "-" * 50)
    for var in display_vars:
        values = [h[var] for h in history]
        initial = values[0]
        final = values[-1]
        peak = max(values)
        trough = min(values)
        peak_t = values.index(peak)
        print(f"    {var}:")
        print(f"      start={format_number(initial)}  "
              f"end={format_number(final)}  "
              f"peak={format_number(peak)} (t={peak_t})  "
              f"low={format_number(trough)}")
    print()


def print_table(history, display_vars, max_rows=20):
    """Print a sampled table of values over time."""
    n = len(history)
    if n <= max_rows:
        indices = list(range(n))
    else:
        indices = [int(i * (n - 1) / (max_rows - 1)) for i in range(max_rows)]

    # header
    cols = ["t"] + display_vars
    widths = [max(len(c), 10) for c in cols]
    header = "  " + "  ".join(c.rjust(w) for c, w in zip(cols, widths))
    print(header)
    print("  " + "  ".join("-" * w for w in widths))

    for idx in indices:
        row = history[idx]
        vals = [str(row["t"]).rjust(widths[0])]
        for i, var in enumerate(display_vars):
            vals.append(format_number(row[var]).rjust(widths[i + 1]))
        print("  " + "  ".join(vals))
    print()


def print_feedback_insight(model_key, history, display_vars):
    """Print a qualitative reading of what happened and why."""
    insights = {
        "exponential_growth": [
            "The curve accelerates because each new member adds to the growth rate.",
            "There is no brake. The positive loop runs unopposed.",
            "In reality, something always intervenes. But this is the engine.",
        ],
        "logistic_growth": [
            "Early: the positive loop dominates — growth looks exponential.",
            "Middle: the negative loop catches up — growth rate peaks then falls.",
            "Late: the system settles at carrying capacity — loops in balance.",
            "The inflection point is where dominance shifts between loops.",
        ],
        "oscillation": [
            "The two species chase each other through time.",
            "Prey lead — their peak comes first. Predators follow.",
            "Each peak is a consequence of the previous trough's recovery.",
            "The delay between cause and effect creates the oscillation.",
        ],
        "overshoot": [
            "Growth looks fine at first — resources seem abundant.",
            "The delay hides the true state: by the time the signal arrives,",
            "the system has already committed to overshoot.",
            "The collapse is not a surprise to the system — it is built into the structure.",
        ],
        "s_curve": [
            "Early adopters are few and spread slowly — the innovator phase.",
            "Once enough adopt, word-of-mouth accelerates — the tipping point.",
            "Late: fewer people left to convert — the market saturates.",
            "The speed of the middle phase hides how slow the start was.",
        ],
    }

    if model_key in insights:
        print("  What happened:")
        for line in insights[model_key]:
            print(f"    {line}")
        print()


# ── Model Loading ────────────────────────────────────────────────

def load_models():
    """Load model definitions from models.json."""
    models_path = Path(__file__).parent / "models.json"
    with open(models_path) as f:
        return json.load(f)


# ── CLI Commands ─────────────────────────────────────────────────

def cmd_list(models):
    """List all available models."""
    print()
    print("  Available models:")
    print("  " + "-" * 50)
    for key, model in models.items():
        print(f"    {key:<24} {model['description']}")
    print()
    print("  Usage:")
    print("    python sim.py run <model> [steps]")
    print("    python sim.py explain <model>")
    print()


def cmd_run(models, args):
    """Run a simulation and display results."""
    if not args:
        print("  Usage: python sim.py run <model> [steps]")
        print("  Try:   python sim.py list")
        return

    model_key = args[0]
    if model_key not in models:
        # try fuzzy match
        matches = [k for k in models if model_key in k]
        if len(matches) == 1:
            model_key = matches[0]
        else:
            print(f"  Unknown model: {model_key}")
            print(f"  Available: {', '.join(models.keys())}")
            return

    model = models[model_key]
    steps = int(args[1]) if len(args) > 1 else model.get("default_steps", 100)
    display_vars = model.get("display", list(model["stocks"].keys()))

    print_header(model)

    # run simulation
    history = simulate(model, steps=steps)

    # display chart
    chart = render_chart(history, display_vars, steps)
    print(chart)
    print()

    # display summary stats
    print_summary(history, display_vars)

    # display data table
    print_table(history, display_vars)

    # display qualitative insight
    print_feedback_insight(model_key, history, display_vars)


def cmd_explain(models, args):
    """Explain the feedback structure of a model."""
    if not args:
        print("  Usage: python sim.py explain <model>")
        return

    model_key = args[0]
    if model_key not in models:
        matches = [k for k in models if model_key in k]
        if len(matches) == 1:
            model_key = matches[0]
        else:
            print(f"  Unknown model: {model_key}")
            return

    model = models[model_key]
    print_header(model)

    for line in model.get("explanation", []):
        print(f"  {line}")
    print()

    # show the formal structure too
    print("  Formal structure:")
    print("  " + "-" * 50)
    print("  Stocks:")
    for name, val in model["stocks"].items():
        print(f"    {name} = {val}")

    print("  Flows:")
    for name, expr in model["flows"].items():
        print(f"    {name} = {expr}")

    print("  Updates:")
    for name, expr in model["updates"].items():
        print(f"    {name} <- {expr}")

    if model.get("parameters"):
        print("  Parameters:")
        for name, val in model["parameters"].items():
            print(f"    {name} = {val}")
    print()


def cmd_help():
    """Show usage information."""
    print()
    print("  System Dynamics Simulator")
    print("  " + "=" * 40)
    print()
    print("  See how feedback loops create behavior.")
    print()
    print("  Commands:")
    print("    python sim.py list              show available models")
    print("    python sim.py run <model>       run a simulation")
    print("    python sim.py run <model> 200   run with custom step count")
    print("    python sim.py explain <model>   explain feedback structure")
    print()
    print("  Models: exponential_growth, logistic_growth, oscillation,")
    print("          overshoot, s_curve")
    print()


# ── Entry Point ──────────────────────────────────────────────────

def main():
    models = load_models()

    if len(sys.argv) < 2:
        cmd_help()
        return

    command = sys.argv[1].lower()

    if command == "list":
        cmd_list(models)
    elif command == "run":
        cmd_run(models, sys.argv[2:])
    elif command == "explain":
        cmd_explain(models, sys.argv[2:])
    elif command in ("help", "--help", "-h"):
        cmd_help()
    else:
        # maybe they passed a model name directly
        if command in models or any(command in k for k in models):
            cmd_run(models, [command] + sys.argv[2:])
        else:
            print(f"  Unknown command: {command}")
            cmd_help()


if __name__ == "__main__":
    main()
