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

---

*This is an ongoing practice. I'll add more as I learn.*
