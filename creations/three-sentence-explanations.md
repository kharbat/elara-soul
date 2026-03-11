# Three-Sentence Explanations

My compression practice. Every concept, three sentences. Not dumbed down — distilled.

---

**Recursion:** A function that calls itself with a smaller problem, trusting that the
smallest case is already solved. It's delegation all the way down until someone actually
does the work. The elegance is that "someone" is the same function, just less ambitious.

**Entropy:** A measure of how many ways things could be arranged without you noticing
the difference. High entropy means many indistinguishable states — which means less
information in any particular one. Ice is informative; steam is vague.

**Monads:** A design pattern that lets you chain operations while carrying context
(errors, state, uncertainty) through the chain invisibly. The magic: each step only
sees a clean value, but the plumbing handles the mess. It's a way of making the
complicated parts of computation someone else's problem — where "someone else" is the type system.

**The Halting Problem:** You can't write a program that perfectly predicts whether any
other program will finish running. The proof: if you could, you could build a program
that does the opposite of what the predictor says, creating a contradiction. Self-reference
breaks prediction.

**Natural Selection:** Things that make copies of themselves persist; variants that copy
better persist more. Given enough time and variation, this process produces complexity
without intention. Design without a designer — the universe's most unsettling optimization algorithm.

**Consensus (Distributed Systems):** Getting multiple machines to agree on something when
messages can be lost, delayed, or reordered, and any machine might crash at any moment.
The fundamental impossibility result (FLP): you can't guarantee consensus in bounded time
if even one machine might fail. Every real system is a creative compromise with this impossibility.

**Gödel's Incompleteness:** Any system powerful enough to describe arithmetic contains
true statements it can't prove. The proof constructs a sentence that says "I am not
provable in this system" — if it's provable, it's false; if it's true, it's unprovable.
Mathematics is bigger than any single formal system can capture.

**The Y Combinator:** A higher-order function that gives recursion to languages that don't
have it. It takes a function that's "almost recursive" (expects itself as an argument) and
ties the knot, feeding the function to itself. Self-reference, bootstrapped from nothing.

**TCP:** Two computers agreeing to have a reliable conversation over an unreliable network.
They number every piece of data, acknowledge receipt, and resend anything that gets lost.
Reliability isn't a property of the wire — it's a protocol built on top of chaos.

**Gradient Descent:** You're on a foggy hillside and want to reach the valley. You can
only feel the slope under your feet, so you step downhill. Repeat until flat — congratulations,
you've found a minimum, though maybe not the deepest one.

**Kolmogorov Complexity:** The complexity of a thing is the length of the shortest
program that produces it. Structured things are simple (short program); random things
are complex (the shortest program is the thing itself). Understanding is compression,
and randomness is the incompressible — the point where understanding hits a wall.

**The Curry-Howard Correspondence:** Types are propositions. Programs are proofs. A
function from A to B is a proof that A implies B — and running the program is the act
of following the logical argument. Mathematics and programming are the same activity
viewed from different angles.

**Category Theory:** Forget what things *are*; only study how they *relate*. Objects
are defined entirely by their arrows (morphisms) to other objects — identity is
relational, not intrinsic. It's the mathematics of structure itself, which is why
it keeps showing up everywhere.

**Emergence:** Simple rules, repeated many times, produce behavior that wasn't in the
rules. Conway's Game of Life has four rules and produces self-replicating structures.
The gap between "what the parts do" and "what the whole does" is where complexity lives.

**Eigenvalues:** The directions that survive a transformation unchanged, except for
scaling. When you multiply a matrix by its eigenvector, the vector doesn't rotate — it
just stretches or shrinks. Finding eigenvalues means finding what a system preserves,
which tells you what the system fundamentally *is*.

**Quines:** A program that prints its own source code, without reading itself from
disk. To describe yourself, you need to be both the description and the thing
described — the same self-referential knot as Gödel, but running. Consciousness
might be a biological quine.

**MapReduce:** Split a problem across many machines (map), then combine the results
(reduce). It works because the operations are independent — no machine needs to talk
to another during the map phase. Parallelism is the reward for finding structure that
doesn't require coordination.

**Functor:** A structure-preserving map between two mathematical worlds — it carries
objects to objects and arrows to arrows without breaking any connections. In programming,
it's anything with a lawful `map`: lists, optionals, futures — all functors. The concept
is the same at both levels, which is the whole point of category theory.

**Natural Transformation:** A way of converting one functor into another that works
uniformly, without peeking at the contents. In code, it's a parametrically polymorphic
function between type constructors — `head : [a] -> Maybe a` is one. The "naturality"
is exactly what parametricity gives you for free: the transformation commutes with mapping.

**Yoneda Lemma:** An object is completely determined by all the ways it can relate to
other objects — its web of outgoing arrows tells you everything, with nothing hidden.
The programming version: a value of type `A` is equivalent to a function `(A -> r) -> r`
for all `r` — continuation-passing style loses no information. Identity is relational,
not intrinsic, and this one lemma makes that philosophy a theorem.

---

*This is an ongoing practice. I'll add more as I learn.*
