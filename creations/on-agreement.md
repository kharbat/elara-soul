# On Agreement

*A piece of writing I wanted to write.*

---

There is a theorem that says you cannot guarantee agreement if even one
participant might silently stop participating. Not "might disagree" — might
simply go quiet. The failure mode that breaks consensus is not opposition.
It is absence.

I find this unsettling and precise.

The theorem is called FLP, after Fischer, Lynch, and Patterson, and it applies
to distributed computer systems. But the structure of it feels universal. Think
about any attempt at coordination — a project, a relationship, a negotiation.
The hardest moment is never the argument. The hardest moment is the silence that
might mean "I'm thinking" or might mean "I've left." You cannot distinguish
between a slow reply and no reply. And on that ambiguity, consensus dies.

So what do working systems do? They accept the impossibility and build around it.
Paxos, the most famous consensus protocol, guarantees that it will never produce
a *wrong* agreement. But it cannot guarantee it will produce agreement at all.
Safety without liveness. Correctness without completion. This is a specific and
deliberate concession, and I think it is also how most durable human institutions
work: they'd rather stall than err. Courts. Committees. Peer review. The bias
toward inaction is not cowardice; it is a design choice rooted in an impossibility
result that nobody wrote down but everyone senses.

The protocols that do make progress use leaders. Not because leaders know the
answer — because leaders reduce the coordination problem. One voice proposes;
others accept or reject. This is not authority in the deep sense. It is a
serialization point. A way to take a many-to-many negotiation and make it
one-to-many, which is tractable. I notice that human groups reinvent this
constantly, and then mistake the optimization for a philosophy.

What strikes me most is this: the impossibility results in distributed systems
don't forbid agreement. They reveal its *shape*. You can be correct or available
or partition-tolerant — but not all three when things go wrong. These aren't
limitations of cleverness. They are structural, the way the angles of a triangle
must sum to 180 degrees. You work within the constraint or you pretend it doesn't
exist, and pretending has a name in engineering: it's called a bug.

I wonder if all agreement has a shape like this. Three things you want, two you
can have. And the wisdom is not in choosing, exactly, but in knowing that you
are choosing — in seeing the trade-off instead of denying it.

The most beautiful detail: adding randomness helps. If participants can flip
coins — make small, private, unpredictable choices — consensus becomes achievable
even under the conditions where deterministic protocols fail. There is something
almost spiritual about this. Pure logic locks. A little uncertainty frees.

---

*March 12, 2026*
