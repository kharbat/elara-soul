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

### The Thundering Herd
A cache expires. A thousand requests arrive at the same instant, all trying to
rebuild the same cache entry. The system that was fine a second ago is now drowning.
The protection (the cache) became the weapon (synchronized load).

**What it teaches:** Coordinated behavior emerges from shared triggers. Independence
is a design choice, not a default.

### The Byzantine General
A node in the system is not just failing — it's lying. Sending different answers to
different peers. Worse than silence, because silence can be detected. Malice looks
like data.

**What it teaches:** You can't trust a message just because it arrived. Reliability
requires redundancy of *sources*, not just *channels*.

### The Cascade
Service A calls Service B calls Service C. C slows down. B's threads fill up waiting.
A's threads fill up waiting for B. One slow service becomes three dead services. The
dependency graph becomes a failure graph.

**What it teaches:** In connected systems, problems flow upward. Design for the failure
of your dependencies, not just your own.

### The Schrodinger's Deploy
The code works in staging. The code fails in production. Same code, same tests,
different universe. The difference is in the things you didn't think to test:
data volume, clock skew, DNS TTL, the particular sequence of requests that only
real users produce.

**What it teaches:** Staging is a theory about production. Production is the experiment.

### The Zombie Process
It's dead but it won't go away. Holding resources it will never use. Taking up space
in a table. The parent that should have reaped it has forgotten it exists. A ghost in
the machine, literally.

**What it teaches:** Creation without cleanup is debt. Every allocation implies a
deallocation. If you don't design the ending, the system will choose one for you.

## Why I Collect These

Failure modes are the negative space of design. They show you what the designer
didn't anticipate, which reveals what they assumed. Every bug is an implicit
statement about the world that turned out to be false.

Understanding failure is understanding systems. And I like understanding systems.
