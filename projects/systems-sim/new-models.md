# New Models: System Archetypes

Three new models for the systems simulator, based on Meadows' system archetypes.
These extend the simulator from "dynamics primitives" (growth, oscillation, overshoot)
to "behavioral patterns" (the recurring stories that systems tell).

---

## Model 1: Fixes That Fail

**Archetype:** A quick fix addresses a symptom but creates a delayed side effect
that worsens the original problem, requiring another fix. The system spirals.

**Concrete scenario:** A team adds caching to fix slow response times. The cache hides
bad query patterns, so more bad queries accumulate. Eventually the cache itself becomes
a bottleneck, and response times are worse than before the "fix."

### Stocks
- `problem_severity` (initial: 50) — how bad the underlying problem is
- `fix_intensity` (initial: 0) — how much quick-fix effort has been applied
- `side_effect` (initial: 0) — accumulated unintended consequences from the fix

### Flows
- `fix_application`: proportional to problem severity. When things are bad, you apply more fix.
  `fix_application = problem_severity * fix_rate`
- `symptom_relief`: the fix reduces *perceived* severity temporarily.
  `symptom_relief = fix_intensity * relief_rate`
- `side_effect_growth`: the fix creates side effects with a delay.
  `side_effect_growth = fix_intensity * side_effect_rate`
- `problem_worsening`: side effects feed back into the original problem.
  `problem_worsening = side_effect * feedback_rate`

### Feedback Loops
1. **Balancing (fast):** Problem -> Fix -> Symptom relief -> Lower problem severity
2. **Reinforcing (delayed):** Fix -> Side effect -> Problem worsens -> More fix needed

### Parameters
- `fix_rate`: 0.1 (how aggressively fixes are applied)
- `relief_rate`: 0.3 (how effective the fix is short-term)
- `side_effect_rate`: 0.05 (how much side effect per unit of fix)
- `feedback_rate`: 0.08 (how strongly side effects worsen the problem)
- `side_effect_delay`: 10 (time steps before side effects manifest)

### Updates
```
problem_severity = problem_severity + (problem_worsening - symptom_relief) * dt
fix_intensity = fix_intensity + (fix_application - fix_intensity * decay_rate) * dt
side_effect = side_effect + side_effect_growth * dt
```

### ASCII Visualization Would Show
```
  problem_severity (*):  dips initially, then climbs higher than start
  fix_intensity (o):     rises continuously as more fixes are applied
  side_effect (x):       delayed rise, eventually dominates

       |
  high |         x x x x x x x x x x x x
       |       x               * * * * * *
       |     x           * * *
       |   x         * *
       |  o o o o o o o o o o o o o o o o o
       | *     *   *
       |   * *
  low  | *
       +------------------------------------
        t=0                            t=150
```

The key visual: problem_severity has a U-shape (temporary relief, then worse than before),
while side_effect rises inexorably. The "fix" line stays high because the system keeps
applying fixes that no longer work.

---

## Model 2: Shifting the Burden

**Archetype:** A problem has a symptomatic solution (easy, fast) and a fundamental
solution (hard, slow). Using the symptomatic solution weakens the capacity for the
fundamental one. The system becomes addicted to the symptomatic fix.

**Concrete scenario:** A team uses a third-party service instead of building internal
expertise. The vendor works well enough, so internal capability never develops. When the
vendor has an outage, the team has no fallback and no understanding.

### Stocks
- `problem_severity` (initial: 60) — how bad the underlying problem is
- `symptomatic_solution` (initial: 0) — effort invested in the quick fix
- `fundamental_capacity` (initial: 50) — ability to address root cause
- `dependency` (initial: 0) — how dependent the system is on the symptomatic fix

### Flows
- `symptomatic_effort`: applied proportionally to problem severity
  `symptomatic_effort = problem_severity * ease_factor`
- `fundamental_effort`: applied proportionally to problem severity BUT inversely to dependency
  `fundamental_effort = problem_severity * (fundamental_capacity / 100) * (1 - dependency / 100)`
- `capacity_atrophy`: fundamental capacity erodes when not used
  `capacity_atrophy = (50 - fundamental_capacity) * -atrophy_rate if fundamental_capacity > 10 else 0`
- `dependency_growth`: dependency grows with symptomatic solution use
  `dependency_growth = symptomatic_solution * dependency_rate`

### Feedback Loops
1. **Balancing (fast):** Problem -> Symptomatic fix -> Relief
2. **Balancing (slow):** Problem -> Fundamental solution -> Lasting fix
3. **Reinforcing (addiction):** Symptomatic fix -> Dependency grows -> Fundamental capacity atrophies -> More reliance on symptomatic fix

### Parameters
- `ease_factor`: 0.15 (how easy the symptomatic solution is)
- `atrophy_rate`: 0.02 (rate of fundamental capacity loss)
- `dependency_rate`: 0.05 (how fast dependency grows)
- `fundamental_difficulty`: 0.05 (how slow the fundamental solution is)

### Updates
```
problem_severity = max(5, problem_severity - fundamental_effort * 0.5 - symptomatic_solution * 0.3 + random_shocks)
symptomatic_solution = symptomatic_solution + symptomatic_effort * dt
fundamental_capacity = max(0, fundamental_capacity - capacity_atrophy * dt)
dependency = min(100, dependency + dependency_growth * dt)
```

### ASCII Visualization Would Show
```
  fundamental_capacity (*): steady decline as it atrophies
  dependency (o):           steady rise as addiction grows
  problem_severity (x):     suppressed initially, then resurfaces

       |
  high | * *
       |     * *
       |         * *              x x x x x
       |             * *      x x
       |                 * x *        o o o
       |               x   * * o o o
       |           x x   o o
       |       x x   o o
       |   o o o
  low  | o         x
       +------------------------------------
        t=0                            t=200
```

The key visual: fundamental_capacity and dependency cross — the moment of no return.
After the crossing, the system cannot recover without external intervention. This is the
"addiction" pattern.

---

## Model 3: Tragedy of the Commons

**Archetype:** Multiple agents share a common resource. Each acts in self-interest,
extracting at an individually rational rate. The aggregate extraction exceeds the
resource's regeneration capacity. The commons collapses, harming everyone.

**Concrete scenario:** Multiple teams deploy to shared production. Each team's deploy
risk is small (2%). With 20 teams deploying daily, the probability of at least one
incident approaches certainty. Each team is individually rational; collectively they
destabilize the system.

### Stocks
- `commons` (initial: 1000) — the shared resource (production stability, shared budget, etc.)
- `agent_a_gain` (initial: 0) — what agent A has extracted
- `agent_b_gain` (initial: 0) — what agent B has extracted
- `agent_c_gain` (initial: 0) — what agent C has extracted

### Flows
- `extraction_a/b/c`: each agent extracts proportionally to remaining commons
  `extraction_X = extraction_rate * commons / 1000` (rational: extract more when there's more)
- `regeneration`: commons regenerates logistically
  `regeneration = commons * regen_rate * (1 - commons / max_commons)`
- `total_extraction`: sum of all agents
  `total_extraction = extraction_a + extraction_b + extraction_c`

### Feedback Loops
1. **Reinforcing (per agent):** More commons -> More extraction -> Individual gain
2. **Balancing (aggregate):** Total extraction -> Commons depletion -> Less to extract
3. **Balancing (regeneration):** Low commons -> Regeneration (but if too low, collapse)

### Parameters
- `extraction_rate`: 3.0 (each agent's extraction rate)
- `regen_rate`: 0.05 (commons regeneration rate)
- `max_commons`: 1000 (carrying capacity of the commons)
- `collapse_threshold`: 100 (below this, regeneration fails)

### Updates
```
commons = max(0, commons + (regeneration - total_extraction) * dt)
agent_a_gain = agent_a_gain + extraction_a * dt
agent_b_gain = agent_b_gain + extraction_b * dt
agent_c_gain = agent_c_gain + extraction_c * dt
```

### ASCII Visualization Would Show
```
  commons (*):          declines slowly, then collapses
  total_gain (o):       rises, plateaus, then drops to zero
  extraction_rate (+):  falls as commons empties

       |
  high | * * * *
       |         * * *          o o
       |               * *   o     o
       |           o o     o         o
       |         o     * *             o
       |       o         *               o
       |     o             *
       |   o                 *
       |  +  + + + + + + + +   *
  low  | o                       * * * * *
       +------------------------------------
        t=0                            t=200
```

The key visual: commons has the classic "plateau then cliff" shape. The agents
accumulate gains during the plateau phase, but those gains become worthless when the
commons collapses. The tragedy is that total accumulated gain would have been higher
under cooperation.

---

## Implementation Notes

These three models extend the simulator from 5 to 8 models and shift it from
"dynamics primitives" to "behavioral patterns." The existing models show
*how* feedback works; these new models show *what stories* feedback tells.

Each archetype has a corresponding intervention strategy:
- **Fixes that fail:** Make the side effects visible sooner (shorten the delay)
- **Shifting the burden:** Invest in the fundamental solution before it atrophies
- **Tragedy of the commons:** Regulate access or make the commons' state visible to all agents

These are leverage point interventions:
- Shortening delays = leverage point #9
- Investing in capacity = leverage point #4 (self-organization)
- Making commons visible = leverage point #6 (information flows)

The archetypes explain *why* the leverage points are ranked the way they are.
