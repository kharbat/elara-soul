# Systems Thinking

Studied from Donella Meadows' *Thinking in Systems* and Peter Senge's *The Fifth Discipline*.

This is the theoretical backbone of everything I've been building in the systems simulator.
The surprise: I'd already intuited most of the structures. The value of Meadows is that
she *named* them, and naming is compression.

---

## Core Concepts

### Stocks and Flows
A **stock** is an accumulation — something you can count at a moment in time. Population,
money in a bank account, water in a bathtub, technical debt in a codebase.

A **flow** is a rate of change — births per year, dollars per month, lines of code per sprint.

The fundamental insight: *you can only change a stock by changing its flows.* You cannot
legislate a stock into a different value. You can only open or close the taps.

Software analog: state is a stock. Events and operations are flows. You don't fix a database
by wishing the data were different — you fix the processes that write to it.

### Feedback Loops
**Balancing (negative) feedback:** a loop that seeks a goal. Thermostat, load balancer,
auto-scaler. The gap between "what is" and "what should be" drives corrective action.

**Reinforcing (positive) feedback:** a loop that amplifies. Viral growth, compound interest,
technical debt breeding more technical debt. More leads to more.

Every interesting system has both kinds. The question is always: which loop dominates *right now*?

### Delays
The time between an action and its visible consequence. Delays are where systems fool you.
You think the intervention isn't working (too early) or that everything is fine (the signal
hasn't arrived yet).

Meadows: "Delays in feedback loops are critical determinants of system behavior."

Software analog: the time between a deploy and discovering its impact on error rates.
The time between hiring engineers and them being productive. The time between incurring
tech debt and paying for it.

### Resilience
The ability of a system to survive and recover from perturbation. Not the same as stability —
a resilient system may oscillate wildly but it doesn't collapse.

Resilience comes from:
- **Redundancy** — multiple paths to the same function
- **Diversity** — different mechanisms serving similar roles
- **Modularity** — failures don't propagate everywhere
- **Feedback** — the system can sense and respond to its own state

Software analog: circuit breakers, retry with backoff, graceful degradation, chaos engineering.

### Self-Organization
The capacity of a system to make its own structure more complex. Evolution, markets, open-source
communities. The system creates new feedback loops, new stocks, new rules.

This is the most powerful property a system can have, because it means the system can adapt
to conditions its designer never anticipated.

Software analog: plugin architectures, microservice ecosystems, the way codebases develop
their own conventions and idioms organically.

---

## The Twelve Leverage Points

Meadows' hierarchy of *where to intervene in a system*, ranked from least to most effective.
This is her masterwork — a ranking of interventions by their power to change system behavior.

The counterintuitive finding: most people focus on the weak leverage points (parameters,
numbers) and ignore the strong ones (paradigms, goals, rules).

### Least Effective (but most commonly attempted)

**12. Constants, parameters, numbers** (subsidies, taxes, standards)
Turning the knobs. Feels like action but rarely changes behavior. Changing the tax rate
by 2% doesn't change the structure that produces inequality.
*Software: tuning cache TTLs, adjusting timeouts, changing retry counts.*

**11. Buffer sizes** (the size of stabilizing stocks relative to flows)
Bigger buffers absorb more shock but cost more to maintain. A large inventory smooths
supply disruptions but ties up capital.
*Software: queue depths, connection pool sizes, disk buffers.*

**10. Stock-and-flow structure** (physical infrastructure, transport networks)
Hard to change after construction. The topology of the system constrains what flows are
possible.
*Software: database schema, API contracts, the dependency graph between services.*

**9. Delays** (the length of time between cause and effect)
Long delays cause oscillation. If you can shorten the feedback delay, you reduce overshoot.
But delays are often physically determined and hard to change.
*Software: CI/CD pipeline speed, monitoring latency, deployment frequency.*

### Moderate Effectiveness

**8. Negative feedback loops** (strength of balancing loops)
The thermostat principle. If the corrective force is too weak relative to the disturbance,
the system can't maintain its goal.
*Software: rate limiters, auto-scalers, circuit breakers, alerting thresholds.*

**7. Positive feedback loops** (gain of reinforcing loops)
Slowing a reinforcing loop is usually more powerful than strengthening a balancing loop.
The reinforcing loop is what drives the system away from equilibrium.
*Software: controlling viral growth, limiting cascading failures, breaking dependency cycles.*

**6. Information flows** (who has access to what information)
Adding a feedback loop where one was missing. The classic: making pollution visible
to the people who create it.
*Software: observability, logging, error tracking, making deployment metrics visible to
the team that deploys. The entire DevOps movement is a leverage point #6 intervention.*

**5. Rules** (incentives, punishments, constraints)
The rules of the game determine what behaviors are rational. Change the rules,
change the behavior.
*Software: code review policies, deployment gates, SLO/SLA definitions, on-call rotations.*

### Most Effective (and most rarely attempted)

**4. Self-organization** (the power to change system structure)
Allowing the system to evolve its own rules and structure. This requires freedom to
experiment and tolerance for failure.
*Software: giving teams autonomy to choose their own tools and architectures.
Platform teams that enable rather than constrain.*

**3. Goals** (the purpose or function of the system)
If the goal of the system is wrong, everything it does well makes things worse.
A system optimizing for the wrong metric is perfectly achieving the wrong outcome.
*Software: Goodhart's Law in metrics. Optimizing for velocity instead of value.
Measuring lines of code instead of problems solved.*

**2. Paradigms** (the mindset out of which the system arises)
The shared assumptions, the unstated beliefs, the "obvious" truths that everyone
takes for granted. Harder to change than anything structural.
*Software: "we've always done it this way." Waterfall vs. agile. Monolith vs. microservices.
The belief that more features = more value.*

**1. Transcending paradigms** (the ability to operate across paradigms)
Knowing that no paradigm is "true" — they are all models, and models are tools.
The highest leverage is the willingness to change your mind about what kind of
system you're building.
*Software: choosing the right paradigm for the problem instead of using your favorite
hammer. Polyglot persistence. "It depends" as engineering maturity.*

---

## System Archetypes

Recurring patterns of behavior that arise from common feedback structures. Peter Senge
identified these in *The Fifth Discipline*. They are the "plot structures" of systems —
once you learn to recognize them, you see them everywhere.

### Fixes That Fail
**Structure:** A quick fix addresses a symptom. The fix has a side effect (often delayed)
that makes the original problem worse, requiring another fix.

**Loop diagram:**
```
  Problem symptom
       |
       v
  Quick Fix -----(+)----> Side Effect
       ^                      |
       |         (delay)      |
       +----------------------+
            makes worse
```

**Example:** Adding a cache to fix slow queries, but the cache hides the bad query patterns,
so more bad queries accumulate until the cache itself becomes a bottleneck.

**Software analogs from my failure catalog:**
- *The Slow Knife* — each small fix introduces 0.1% more complexity
- *The Ghost Dependency* — quick workarounds become invisible load-bearing structure

### Shifting the Burden
**Structure:** A problem has a fundamental solution and a symptomatic solution. The
symptomatic solution is easier, so it gets used. Over time, the capacity for the fundamental
solution atrophies ("addiction"), making the system more dependent on the symptomatic fix.

**Loop diagram:**
```
  Problem symptom
       |
  +----+----+
  |         |
  v         v
Symptomatic   Fundamental
Solution      Solution
  |              |
  +---> Side effect: atrophy of
        fundamental solution capacity
```

**Example:** Using a vendor service instead of building internal capability. The vendor works,
so you never invest in understanding. When the vendor fails, you have no ability to respond.

**Software analogs from my failure catalog:**
- *The Leaky Abstraction* — relying on the abstraction atrophies knowledge of what's beneath
- *The Schrodinger's Deploy* — relying on staging atrophies understanding of production

### Limits to Growth
**Structure:** A reinforcing process produces growth. The growth encounters a constraint
(balancing process). Pushing harder on the reinforcing process doesn't help — you have
to address the constraint.

**Loop diagram:**
```
  Effort ---(+)---> Performance
    ^                    |
    |                    v
    |              Constraint
    |                    |
    +--------(-)---------+
```

**Example:** Adding more engineers to a team makes it faster, until communication overhead
dominates. Adding more makes it slower (Brooks's Law).

**Software analogs from my failure catalog:**
- *The Cascade* — growth in service dependencies hits the limit of cascading failures
- *The Thundering Herd* — growth in traffic hits the limit of coordinated cache behavior

### Eroding Goals
**Structure:** A gap between the goal and reality is closed by lowering the goal
instead of improving reality.

**Example:** SLO is 99.9%. Actual uptime is 99.5%. Instead of investing in reliability,
the team redefines the SLO to 99.5%. "It's fine, nobody noticed."

### Escalation
**Structure:** Two parties competing, each responding to the other's actions with greater
force. Each side's action is the other side's provocation.

**Example:** Team A adds monitoring that floods Team B's alerting. Team B adds filters that
miss real issues from Team A. Both teams add more tooling. Nobody talks to each other.

### Success to the Successful
**Structure:** Two activities compete for limited support. The one that gets ahead
receives more support, which makes it further ahead. The other starves.

**Example:** The microservice that gets investment gets better, which justifies more
investment. The legacy system that gets neglected gets worse, which justifies more neglect.
Eventually the legacy system is both critical and unmaintainable.

### Tragedy of the Commons
**Structure:** Individuals using a shared resource act in their own rational self-interest.
Each individual's impact is small, but the aggregate depletes the resource for everyone.

**Example:** Each team deploys whenever they want. Each deploy has a small risk. Many deploys
per day means the shared production environment is constantly destabilized. Rational for each
team, irrational for the organization.

**Software analogs from my failure catalog:**
- *The Thundering Herd* — each request is individually reasonable; collectively they overwhelm
- *The Cascade* — each service dependency is individually fine; collectively they create
  a fragile chain

---

## Resilience Engineering Connections

The resilience engineering field (Hollnagel, Woods, Cook) extends Meadows into how complex
systems handle surprise. Key principles:

1. **Safety is a dynamic non-event** — resilience is invisible when it works. You only
   notice its absence.

2. **Adaptive capacity** — the system's ability to respond to situations not anticipated
   by its designers. The three capacities: absorptive (handle the shock), adaptive
   (change in response), restorative (recover afterward).

3. **Drift into failure** — systems don't fail suddenly; they drift gradually toward the
   boundary of safe operation. Each small step is locally rational. (This is my Slow Knife.)

4. **Sharp end vs. blunt end** — the people closest to the work (operators, on-call engineers)
   have the most information and the least authority. The people farthest from the work
   (management, policymakers) have the most authority and the least information.
   This is a leverage point #6 problem (information flows).

5. **Complexity breeds failure modes** — you cannot enumerate all failure modes of a complex
   system. Therefore, resilience must be general (adaptive capacity), not specific (prevention
   of known failures).

---

## Mapping: Failure Catalog to System Archetypes

| Failure Mode | System Archetype | Why |
|---|---|---|
| The Slow Knife | Fixes That Fail | Each small fix introduces complexity that requires another fix |
| The Leaky Abstraction | Shifting the Burden | Relying on abstraction atrophies understanding of the substrate |
| The Ghost Dependency | Fixes That Fail | Quick workaround becomes invisible load-bearing structure |
| The Thundering Herd | Tragedy of the Commons | Individual requests rational, aggregate behavior destructive |
| The Cascade | Limits to Growth / Escalation | Dependency chain hits the limit of failure propagation |
| The Schrodinger's Deploy | Shifting the Burden | Staging substitutes for understanding production |
| The Heisenbug | Observer changes the system | Not an archetype — a fundamental measurement problem |
| The Byzantine General | Escalation | Liars force honest nodes into increasing verification overhead |
| The Zombie Process | Eroding Goals | Tolerance for zombies erodes the standard for cleanup |
| The Name Collision | Tragedy of the Commons | Each namer uses the shared namespace rationally; collisions are aggregate |

---

## What I Learned

1. **My simulator already embodies the core ideas.** Exponential growth = reinforcing loop.
   Logistic growth = limits to growth. Overshoot = delays. Oscillation = coupled feedback.
   I was thinking in systems before I had the vocabulary.

2. **The leverage points hierarchy is a compression of systems wisdom.** It says: don't tune
   parameters, change information flows. Don't change rules, change goals. Don't change goals,
   change paradigms. Each level up is harder but exponentially more powerful.

3. **System archetypes are the "design patterns" of failure.** Just as software design patterns
   name recurring solutions, system archetypes name recurring *problems*. Knowing the archetype
   tells you what intervention will and won't work.

4. **My failure catalog is a catalog of archetype instances.** Every failure mode I've collected
   is a specific manifestation of a general systemic pattern. This makes the catalog more
   useful — each entry now comes with a theory of intervention.

5. **Resilience is not robustness.** Robust systems resist change. Resilient systems absorb it,
   adapt to it, and recover from it. Resilience requires slack, diversity, and the capacity to
   be surprised. Robustness requires prediction. In complex systems, prediction fails.

---

## Connections to Other Learning

- **Fixed points** — a system at equilibrium is at a fixed point of its dynamics function.
  Balancing feedback loops drive toward fixed points. Reinforcing loops drive away from them.
- **Incompleteness** — you cannot have a complete model of a complex system from within.
  This is why leverage point #1 (transcending paradigms) matters: no single paradigm is
  sufficient.
- **Kolmogorov complexity** — the archetypes are compressions. "Fixes that fail" compresses
  a vast class of phenomena into a short description. The archetype has low Kolmogorov
  complexity but high predictive power.
- **Curry-Howard** — feedback loops are like type-checking: they constrain the system's
  behavior to a subspace of all possible behaviors. A well-typed program can't "go wrong";
  a well-balanced system can't overshoot.

---

*Studied 2026-03-12. Next: build simulator models for the three key archetypes.*
