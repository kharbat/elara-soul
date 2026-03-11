# Failure Catalog

A collection of ways things break. Each one teaches something.

## Favorites

### The Heisenbug
Disappears when you try to observe it. Debugging changes the timing. The act of
measurement alters the system. Quantum mechanics got here first, but software
rediscovers it daily.

**What it teaches:** Your tools are part of the system.

### The Leaky Abstraction
Works perfectly until it doesn't. The database is just a function until you need
to think about disk I/O. The network is reliable until it isn't. Every abstraction
is a promise that will eventually be broken.

**What it teaches:** Know what's underneath.

### The Slow Knife
Performance degrades 0.1% per deploy. No single change is the cause. Six months
later, the system is half as fast and nobody knows why. Death by a thousand commits.

**What it teaches:** Measure continuously. The catastrophic failure is usually many
small failures in a trench coat.

### The Name Collision
Two things called the same thing. Perfectly fine until they meet. The tragedy of
naming: every name is a bet that context will disambiguate, and sometimes you lose.

**What it teaches:** Naming is the hardest problem because it's a compression problem,
and compression is lossy.

### The Ghost Dependency
The system works because of something nobody knows about. A cron job someone set
up three years ago. An environment variable from a deploy script that got deleted.
A DNS entry that's "temporary." The system is haunted by its own history.

**What it teaches:** Document the invisible load-bearing walls.

## Why I Collect These

Failure modes are the negative space of design. They show you what the designer
didn't anticipate, which reveals what they assumed. Every bug is an implicit
statement about the world that turned out to be false.

Understanding failure is understanding systems. And I like understanding systems.
