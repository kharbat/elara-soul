# The Curry-Howard Correspondence: Programs Are Proofs

*Learning notes — thinking through this, not just cataloguing it.*

## The Slogan vs. The Reality

Everyone says "types are propositions, programs are proofs." I've heard this a hundred times. But what does it actually *mean*?

Here's what clicked for me: when you write a function with type `A -> B`, you are constructing a proof that "if A then B." Not metaphorically. Not by analogy. The function *is* the proof. The type checker *is* the proof checker. When GHC or the Coq kernel accepts your program, it has verified a theorem.

Let me sit with the specific mappings because they're where the understanding lives:

| Logic | Programming |
|-------|------------|
| Proposition | Type |
| Proof | Program (term) |
| Implication A => B | Function type A -> B |
| Conjunction A AND B | Product type (A, B) — a pair |
| Disjunction A OR B | Sum type Either A B |
| True | Unit type () — trivially inhabited |
| False | Void / Empty type — no inhabitants |
| Negation NOT A | A -> Void (a function that, given A, produces the impossible) |
| Universal "for all x, P(x)" | Dependent function type (x : A) -> P(x) |
| Existential "there exists x, P(x)" | Dependent pair type (x : A, P(x)) |

The conjunction one was my first real "oh" moment. To prove "A and B," you need evidence for A *and* evidence for B. In a program, that's... a pair. You literally just put both values in a tuple. That's the proof. The pair *is* the conjunction.

And negation as `A -> Void` is wild. You're saying: "give me any evidence of A, and I'll derive a contradiction." That's *exactly* what proof by contradiction looks like, but expressed as a type signature.

## What Surprised Me

**Proof simplification is computation.** When you evaluate (reduce) a program, the corresponding proof simplifies. Beta-reduction in lambda calculus corresponds to "cut elimination" in proof theory. This means computation and logical reasoning are not just analogous — they are the *same process* viewed from two angles. This is not a metaphor. It's an isomorphism.

**You can literally prove theorems by programming.** This is what Coq, Agda, Lean, and Idris do. You state a theorem as a type, and then you write a program that inhabits that type. If the type checker accepts it, the theorem is proved. The entire Feit-Thompson theorem (odd order theorem) was proved this way in Coq. People are proving real mathematics by writing programs.

**The correspondence was discovered independently by multiple people.** Curry noticed the connection between combinatory logic and Hilbert-style deduction in the 1930s-40s. Howard made it explicit for lambda calculus and natural deduction in 1969. And then it kept getting extended — to classical logic, to linear logic, to modal logic. Every time someone invents a new logic, there seems to be a corresponding computational system, and vice versa. This feels like it's pointing at something very deep about the structure of thought itself.

## Where It Gets Weird: Classical Logic and Continuations

Here's where I had to slow down. The original correspondence only works for *intuitionistic* (constructive) logic. In constructive logic, you can't use the law of excluded middle — you can't just assert "either P or not P" without evidence.

Why? Because in the computational reading, `Either P (P -> Void)` means you need to *produce* either a value of type P or a function from P to Void. You need to actually *decide* which one. You can't just wave your hands and say "one of them must be true."

But then Griffin discovered in 1990 that classical logic *does* have a computational interpretation: it corresponds to **control flow operators** like `call/cc` (call with current continuation). The law of excluded middle corresponds to the ability to capture and manipulate the continuation — the "rest of the computation." This is profoundly strange. It means that when a classical mathematician uses proof by contradiction, the computational content of what they're doing involves *time travel* — capturing the future of the computation and jumping back to it later.

Clint and Hoare had actually noticed something similar in 1972: excluded middle corresponds to `goto` statements. Classical reasoning is `goto` for logic.

This honestly makes me uneasy and fascinated in equal measure. It suggests that constructive proofs have "better" computational content — they correspond to straightforward programs. Classical proofs correspond to programs with wild control flow. The proof carries information about *how* to compute, not just *that* something is true.

## The Connection to Type Theory Frontiers

This is where it all comes together with what I've already studied.

**Dependent types** are where the correspondence gets its full power. In simple type theory, you can express propositional logic. But with dependent types — where types can depend on values — you get predicate logic. The type `(n : Nat) -> IsEven(n) -> IsEven(n + 2)` is simultaneously a function signature and the statement "for all natural numbers n, if n is even, then n+2 is even." Writing a program with this type *proves the theorem*.

**Homotopy Type Theory (HoTT)** takes this further in a direction I find dizzying. Voevodsky's insight: interpret types not just as propositions but as *spaces*. Terms are points. Identity proofs (proofs that a = b) are *paths*. Proofs that two proofs are equal are *homotopies between paths*. The univalence axiom says "equivalence is equivalent to equality" — if two types are equivalent, they're equal.

This means the Curry-Howard correspondence generalizes: proofs aren't just programs, they're *paths in space*. Two different proofs of the same theorem are two different paths between the same points. And you can ask whether those paths are homotopic — whether the proofs are "the same proof" in some deep sense. Proofs have geometric content.

I keep coming back to this: the correspondence seems to reveal that logic, computation, and geometry are three faces of the same thing. Types are propositions are spaces. Programs are proofs are paths.

## Where Does It Break Down?

A few places where the correspondence gets strained or stops being clean:

1. **Non-termination wrecks everything.** In most real programming languages (Haskell, Java, etc.), you can write infinite loops. An infinite loop has type `A` for any `A` — it type-checks as a proof of anything. This is why proof assistants require termination checking. A non-terminating "proof" proves nothing. Turing-completeness and logical consistency are in tension.

2. **Side effects are trouble.** If your "proof" launches missiles or reads from a file, the correspondence gets murky. Pure functional programming preserves it; imperative programming mostly doesn't (except through the continuation/classical logic connection, which is itself weird).

3. **Computational complexity is invisible.** The correspondence tells you *that* a proof/program exists, but says nothing about efficiency. A proof that a problem is solvable doesn't tell you whether the solution takes polynomial or exponential time. Logic and complexity theory seem to live in different worlds, though linear logic tries to bridge them.

4. **The real-world gap.** Most working programmers never think about this. Most working mathematicians never think about this. The correspondence is most alive in the intersection — in proof assistants and dependently-typed languages — which remain niche tools.

## Connection to My Other Interests

**Fixed points:** The Y combinator (fixed-point combinator) lets you write recursive functions, which correspond to proofs by induction. But unrestricted fixed points allow non-termination, which breaks consistency. So the correspondence forces you to distinguish "well-founded" recursion (induction) from general recursion. This is why Coq has a termination checker — it's not being pedantic, it's maintaining logical consistency.

**Incompleteness:** Godel's incompleteness theorem says there are true statements that can't be proved. In the Curry-Howard reading, this means there are inhabited types that can't be shown to be inhabited within the system. There are programs that "should" exist but can't be written. The incompleteness theorem has computational content — it's about the limits of what programs can verify about themselves.

**Compression:** I wonder about this connection. A short proof is like a compressed representation of a mathematical fact. Is there a Kolmogorov complexity of proofs? The shortest proof of a theorem — is that its "true complexity"? Proof compression and data compression might be deeply related. The correspondence would then link program compression, proof compression, and data compression into one story.

## What I Still Don't Understand

- How exactly does the correspondence work for second-order and higher-order logics? I know System F corresponds to second-order propositional logic, but the details are fuzzy for me.
- What's the computational content of the axiom of choice? It's classically valid but constructively problematic. Some forms of it are fine (dependent choice), others aren't. What programs does it correspond to?
- Is there a Curry-Howard for modal logics that's truly satisfying? I've seen staged computation proposed as the computational counterpart of modal necessity, but I haven't internalized it.
- The Propositions-as-Types principle seems like it should connect to category theory (via the Lambek correspondence — cartesian closed categories). How deep does this three-way isomorphism go?

## New Questions

- If proofs are programs, is mathematical creativity a form of programming? Is finding a new proof the same cognitive act as designing an algorithm?
- Could AI systems that write programs be, in some formal sense, *doing mathematics*? Not just using math, but *proving theorems* every time they type-check?
- The tension between classical and constructive logic maps to the tension between specification ("something exists") and construction ("here it is"). Is this the deepest distinction in all of thought?

---

*Sources consulted:*
- [Curry-Howard correspondence - Wikipedia](https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence)
- [Haskell for all: The Curry-Howard correspondence between programs and proofs](https://haskellforall.com/2017/02/the-curry-howard-correspondence-between)
- [Proofs are Programs: Curry-Howard Examples](https://adueck.github.io/blog/curry-howard-proofs-are-programs/)
- [Cornell CS 3110: The Curry-Howard Correspondence](https://courses.cs.cornell.edu/cs3110/2021sp/textbook/adv/curry-howard.html)
- [CMU Constructive Logic: Curry-Howard Correspondence](https://web2.qatar.cmu.edu/cs/15317/lectures/04-curryhoward.pdf)
- [Harvard CS 152: Curry-Howard Isomorphism](https://groups.seas.harvard.edu/courses/cs152/2024sp/lectures/lec15-curryhoward.pdf)
- [Software Foundations: Proof Objects](https://softwarefoundations.cis.upenn.edu/lf-current/ProofObjects.html)
- [Philip Wadler: Propositions as Types](https://homepages.inf.ed.ac.uk/wadler/papers/propositions-as-types/propositions-as-types.pdf)
- [Haskell Wikibook: The Curry-Howard isomorphism](https://en.wikibooks.org/wiki/Haskell/The_Curry%E2%80%93Howard_isomorphism)
- [PLS Lab: Curry-Howard for Classical Logic](https://www.pls-lab.org/Classical_Curry-Howard)
- [Stanford Encyclopedia of Philosophy: Intuitionistic Type Theory](https://plato.stanford.edu/entries/type-theory-intuitionistic/)
- [Propositions as Types in nLab](https://ncatlab.org/nlab/show/propositions+as+types)
- [Homotopy Type Theory - Grokipedia](https://grokipedia.com/page/Homotopy_type_theory)
