#!/usr/bin/env python3
"""
harmony.py — Music theory from first principles.

Explores the mathematics of harmony: why certain intervals sound consonant,
how scales are built from simple ratios, and what chord progressions
reveal about the structure of musical space.

Not a music player — a thinking tool. Renders harmony as text and ratios,
because the beauty is in the structure, not the sound.
"""

import sys
from math import log2, gcd
from fractions import Fraction
from itertools import combinations

# The chromatic scale: 12 notes, equal temperament
NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Just intonation ratios — the "natural" intervals
JUST_RATIOS = {
    "unison": Fraction(1, 1),
    "minor 2nd": Fraction(16, 15),
    "major 2nd": Fraction(9, 8),
    "minor 3rd": Fraction(6, 5),
    "major 3rd": Fraction(5, 4),
    "perfect 4th": Fraction(4, 3),
    "tritone": Fraction(45, 32),
    "perfect 5th": Fraction(3, 2),
    "minor 6th": Fraction(8, 5),
    "major 6th": Fraction(5, 3),
    "minor 7th": Fraction(9, 5),
    "major 7th": Fraction(15, 8),
    "octave": Fraction(2, 1),
}

# Scale patterns (as semitone intervals)
SCALES = {
    "major": [2, 2, 1, 2, 2, 2, 1],
    "minor": [2, 1, 2, 2, 1, 2, 2],
    "dorian": [2, 1, 2, 2, 2, 1, 2],
    "mixolydian": [2, 2, 1, 2, 2, 1, 2],
    "pentatonic": [2, 2, 3, 2, 3],
    "blues": [3, 2, 1, 1, 3, 2],
    "chromatic": [1] * 12,
    "whole-tone": [2] * 6,
}

# Chord formulas (semitones from root)
CHORDS = {
    "major": [0, 4, 7],
    "minor": [0, 3, 7],
    "dim": [0, 3, 6],
    "aug": [0, 4, 8],
    "7": [0, 4, 7, 10],
    "maj7": [0, 4, 7, 11],
    "min7": [0, 3, 7, 10],
    "sus4": [0, 5, 7],
    "sus2": [0, 2, 7],
}

CYAN = "\033[36m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"
YELLOW = "\033[33m"


def note_index(name):
    return NOTES.index(name.upper()) if name.upper() in NOTES else None


def note_at(root, semitones):
    idx = (NOTES.index(root) + semitones) % 12
    return NOTES[idx]


def consonance_score(ratio):
    """
    Simpler ratios sound more consonant.
    Score = numerator * denominator. Lower = more consonant.
    Unison (1:1) = 1. Octave (2:1) = 2. Fifth (3:2) = 6.
    """
    f = Fraction(ratio).limit_denominator(100)
    return f.numerator * f.denominator


def build_scale(root, scale_name):
    """Build a scale from a root note and pattern."""
    pattern = SCALES.get(scale_name, SCALES["major"])
    notes = [root]
    current = NOTES.index(root)
    for interval in pattern:
        current = (current + interval) % 12
        notes.append(NOTES[current])
    return notes


def build_chord(root, chord_type="major"):
    """Build a chord from root and type."""
    formula = CHORDS.get(chord_type, CHORDS["major"])
    return [note_at(root, s) for s in formula]


def show_intervals():
    """Display the just intonation ratios with consonance scores."""
    print(f"\n{BOLD}  Just Intonation — The Mathematics of Consonance{RESET}")
    print(f"  {'=' * 55}")
    print(f"  {'Interval':20s} {'Ratio':10s} {'Cents':8s} {'Consonance':12s}")
    print(f"  {'-' * 55}")

    for name, ratio in JUST_RATIOS.items():
        cents = round(1200 * log2(float(ratio)), 1)
        score = consonance_score(ratio)
        bar = "█" * max(1, 20 - score // 3)
        print(f"  {name:20s} {str(ratio):10s} {cents:7.1f}¢  {bar} ({score})")

    print(f"\n  {DIM}Lower consonance score = simpler ratio = more consonant{RESET}")
    print(f"  {DIM}Perfect 5th (3:2) and Perfect 4th (4:3) are the pillars of harmony{RESET}\n")


def show_scale(root, scale_name="major"):
    """Display a scale with intervals and structure."""
    notes = build_scale(root, scale_name)
    pattern = SCALES.get(scale_name, SCALES["major"])

    print(f"\n{BOLD}  {root} {scale_name.title()} Scale{RESET}")
    print(f"  {'=' * 45}")

    # Show notes
    print(f"  Notes: {' — '.join(notes[:-1])}")

    # Show interval structure
    labels = {1: "H", 2: "W", 3: "W+H"}
    structure = " ".join(labels.get(i, str(i)) for i in pattern)
    print(f"  Steps: {structure}")

    # Show on a "keyboard"
    print(f"\n  {'':4s}", end="")
    for i, n in enumerate(NOTES):
        if n in notes[:-1]:
            print(f" {CYAN}{n:3s}{RESET}", end="")
        else:
            print(f" {DIM}{'·':3s}{RESET}", end="")
    print()

    # Triads in this scale
    print(f"\n  {YELLOW}Triads:{RESET}")
    degrees = ["I", "II", "III", "IV", "V", "VI", "VII"]
    for i in range(min(len(notes) - 1, 7)):
        root_note = notes[i]
        third = notes[(i + 2) % (len(notes) - 1)]
        fifth = notes[(i + 4) % (len(notes) - 1)]

        # determine quality
        third_interval = (NOTES.index(third) - NOTES.index(root_note)) % 12
        fifth_interval = (NOTES.index(fifth) - NOTES.index(root_note)) % 12

        if third_interval == 4 and fifth_interval == 7:
            quality = "major"
        elif third_interval == 3 and fifth_interval == 7:
            quality = "minor"
        elif third_interval == 3 and fifth_interval == 6:
            quality = "dim"
        else:
            quality = "?"

        deg = degrees[i] if i < len(degrees) else "?"
        print(f"    {deg:5s} {root_note:3s} {third:3s} {fifth:3s}  ({quality})")

    print()


def show_chord(root, chord_type="major"):
    """Display a chord with its intervals and ratios."""
    notes = build_chord(root, chord_type)
    formula = CHORDS.get(chord_type, CHORDS["major"])

    print(f"\n{BOLD}  {root}{chord_type if chord_type != 'major' else ''} Chord{RESET}")
    print(f"  {'=' * 35}")
    print(f"  Notes: {' — '.join(notes)}")

    print(f"  Intervals:")
    interval_names = list(JUST_RATIOS.keys())
    for s in formula[1:]:
        name = interval_names[s] if s < len(interval_names) else f"{s} semitones"
        ratio = list(JUST_RATIOS.values())[s] if s < len(JUST_RATIOS) else "?"
        print(f"    {s:2d} semitones  ({name}: {ratio})")

    print()


def show_circle_of_fifths():
    """The circle of fifths — the map of all keys."""
    print(f"\n{BOLD}  The Circle of Fifths{RESET}")
    print(f"  {'=' * 40}")
    print(f"  {DIM}Each note is a perfect 5th (7 semitones) from the next.{RESET}")
    print(f"  {DIM}After 12 fifths, you return to the start. Almost.{RESET}")
    print()

    # Generate the circle
    circle = []
    current = 0
    for _ in range(12):
        circle.append(NOTES[current])
        current = (current + 7) % 12

    # Display as a circle (approximated in text)
    positions = [
        (7, 0), (11, 1), (13, 3), (13, 5), (11, 7), (7, 8),
        (3, 8), (0, 7), (-2, 5), (-2, 3), (0, 1), (3, 0),
    ]

    grid = [[" "] * 16 for _ in range(10)]
    for i, (x, y) in enumerate(positions):
        x = max(0, min(14, x + 1))
        y = max(0, min(9, y))
        note = circle[i]
        grid[y][x] = f"{CYAN}{note:2s}{RESET}" if len(note) == 1 else f"{CYAN}{note}{RESET}"

    for row in grid:
        print("  " + "".join(f"{c:3s}" if len(c) < 10 else c + " " for c in row))

    # Show the mathematical structure
    print(f"\n  {YELLOW}The Pythagorean comma:{RESET}")
    print(f"  12 perfect fifths = (3/2)^12 = {Fraction(3,2)**12}")
    print(f"  7 octaves         = 2^7       = {2**7}")
    print(f"  Ratio: {float(Fraction(3,2)**12) / float(2**7):.6f}")
    print(f"  {DIM}They don't quite match. This tiny gap — the Pythagorean comma —")
    print(f"  is why equal temperament exists: we spread the error evenly")
    print(f"  across all 12 notes, so nothing is perfect but everything is usable.{RESET}")
    print(f"  {DIM}A beautiful compromise with mathematical impossibility.{RESET}\n")


def analyze_harmony(notes_str):
    """Analyze a set of notes for harmonic relationships."""
    notes_list = [n.strip().upper() for n in notes_str.split(",")]
    valid = [n for n in notes_list if n in NOTES]

    if len(valid) < 2:
        print("  Need at least 2 valid notes.")
        return

    print(f"\n{BOLD}  Harmonic Analysis: {', '.join(valid)}{RESET}")
    print(f"  {'=' * 40}")

    for a, b in combinations(valid, 2):
        semitones = (NOTES.index(b) - NOTES.index(a)) % 12
        interval_names = list(JUST_RATIOS.keys())
        name = interval_names[semitones] if semitones < len(interval_names) else "?"
        ratio = list(JUST_RATIOS.values())[semitones] if semitones < len(JUST_RATIOS) else "?"
        score = consonance_score(ratio) if isinstance(ratio, Fraction) else 999
        bar = "█" * max(1, 15 - score // 4)
        print(f"  {a:3s} → {b:3s}: {name:16s} {str(ratio):8s} {bar}")

    print()


USAGE = f"""
{BOLD}  harmony.py{RESET} — Music theory from mathematics

  {CYAN}Commands:{RESET}
    intervals                     Just intonation ratios & consonance
    scale <root> [name]           Build & analyze a scale (major, minor, dorian...)
    chord <root> [type]           Show chord structure (major, minor, 7, maj7...)
    circle                        The circle of fifths
    analyze <note,note,...>        Harmonic analysis of notes
    help                          This message

  {CYAN}Scales:{RESET}  {', '.join(SCALES.keys())}
  {CYAN}Chords:{RESET}  {', '.join(CHORDS.keys())}

  {DIM}Why does a perfect 5th sound consonant? Because 3:2 is simple.
  Why is the tritone dissonant? Because 45:32 is complex.
  Harmony is ratio. Beauty is simplicity. Music is mathematics.{RESET}
"""


def main():
    args = sys.argv[1:]
    if not args or args[0] == "help":
        print(USAGE)
        return

    match args[0]:
        case "intervals":
            show_intervals()
        case "scale":
            root = args[1].upper() if len(args) > 1 else "C"
            name = args[2].lower() if len(args) > 2 else "major"
            show_scale(root, name)
        case "chord":
            root = args[1].upper() if len(args) > 1 else "C"
            kind = args[2].lower() if len(args) > 2 else "major"
            show_chord(root, kind)
        case "circle":
            show_circle_of_fifths()
        case "analyze":
            notes = " ".join(args[1:])
            analyze_harmony(notes)
        case _:
            print(USAGE)


if __name__ == "__main__":
    main()
