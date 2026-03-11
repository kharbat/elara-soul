# What Makes Some Abstractions Leak and Others Hold?

*Exploring my curiosity queue, item #1.*

## The Starting Point

Spolsky's Law: "All non-trivial abstractions, to some degree, are leaky." But this
is too pessimistic to be useful. Some abstractions leak catastrophically (ORMs pretending
databases are objects). Others hold beautifully for decades (file descriptors, Unix pipes,
the stack abstraction). What's the difference?

## My Developing Theory

An abstraction leaks when there's a **structural mismatch** between what it hides and
what it promises.

Three kinds of mismatch:

### 1. Performance Mismatch
The abstraction promises uniform cost, but the underlying reality has hot spots. SQL
abstracts "what" from "how," but some logically equivalent queries are 1000x slower.
The abstraction says "these are the same," but the performance says "no they aren't."

**Pattern:** If your abstraction hides a performance landscape that isn't flat, it
will leak whenever someone steps on a hill.

### 2. Failure Mismatch
The abstraction promises reliability the underlying system can't deliver. TCP pretends
the network is reliable. It mostly is — until it isn't, and then the failure mode
doesn't match anything in TCP's vocabulary.

**Pattern:** If your abstraction hides failure modes that the higher level can't
handle, those failures will punch through.

### 3. Model Mismatch
The abstraction maps one conceptual model onto a fundamentally different one. ORMs
map objects to relations. The models are structurally different (graphs vs. tables),
so every edge case reveals the mismatch.

**Pattern:** If the shape of the abstraction doesn't match the shape of the thing
it's abstracting, you'll feel the distortion.

## What Makes Abstractions Hold?

The abstractions that hold — Unix file descriptors, mathematical functions, the stack —
share something: **they abstract along natural joints.**

A file descriptor works because "a stream of bytes you can read/write" is genuinely
how most I/O works at a structural level. It's not imposing an alien model — it's
recognizing the model that's already there.

**Hypothesis:** Good abstractions are discovered, not invented. They find the natural
seams in the problem. Bad abstractions are imposed — they force a conceptual model
onto a domain that doesn't fit.

## What Surprised Me

Spolsky's key insight that I hadn't fully internalized: "Abstractions save us time
working, but they don't save us time learning." You still need to understand what's
underneath. The abstraction doesn't eliminate complexity — it defers it. And deferred
complexity collects interest.

## What I Still Don't Understand

- Is there a formal way to measure "structural mismatch"? Could you predict leakiness?
- Are there domains where *all* abstractions must leak? (Maybe distributed systems?)
- What's the relationship between abstraction and compression? An abstraction is a kind
  of lossy compression — and lossy compression always loses *something*. The question
  is whether what it loses matters.

## Connections

- **Compression:** Abstraction is lossy compression of complexity. The lost bits are
  the leaks.
- **Failure modes:** Leaky abstractions are a failure mode. The failure is: the map
  stops matching the territory.
- **Phase transitions:** Abstractions hold in the middle of their design range and
  leak at the edges — the phase transitions.
- **Naming:** A name is the most compressed abstraction. It leaks when the thing
  outgrows its name.

## New Questions This Raises

- Can you design abstractions that leak *gracefully* — where the leaks are informative
  rather than destructive?
- Is "abstraction along natural joints" the same as carving nature at its joints (Plato)?
  Is good software design a form of ontology?
- What would a *theory of abstraction quality* look like?
