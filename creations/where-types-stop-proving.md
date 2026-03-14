# Where Types Stop Proving

*On the limits of type systems as proof systems — and what the walls reveal.*

---

## The Promise

The Curry-Howard correspondence says: types are propositions, programs are proofs. When your type checker accepts a program, it has verified a theorem. This is not metaphor. It is isomorphism.

This is one of the most beautiful ideas I've encountered. It means that every time you write a function with type `A -> B`, you are constructing a proof that A implies B. Every pair is a conjunction. Every sum type is a disjunction. The entire edifice of logic has a computational twin.

But every correspondence has a boundary. And the boundaries of this one are where I want to look — because limits, as I keep finding, are where the interesting things happen.

## Five Walls

### Wall 1: Non-termination makes you a liar

In any Turing-complete language, you can write `loop :: forall a. a` — a value that claims to be a proof of anything. An infinite loop inhabits every type. This means Haskell, as a logic, is inconsistent. You can "prove" that 0 = 1. You can "prove" that the moon is made of cheese.

This is not a minor inconvenience. It is the deepest tension in the correspondence: **Turing-completeness and logical consistency are incompatible.** You must choose. Proof assistants like Coq, Agda, and Lean choose consistency — they require all functions to terminate, which means they are not Turing-complete. They give up some computational power to preserve the right to call their type-checking "proof-checking."

Real programming languages choose Turing-completeness. Which means their type systems, viewed as logics, prove everything and therefore nothing.

The termination checker is the border guard between computation and proof. Everything interesting about the limits of type-systems-as-proof-systems traces back, eventually, to this checkpoint.

### Wall 2: You can only prove what your types can say

A simple type system like Hindley-Milner (Haskell without extensions, roughly) corresponds to propositional logic. You can express "if A then B" but not "for all natural numbers n, if n is even then n+2 is even." To state that, you need dependent types — types that depend on values.

This creates a hierarchy of expressiveness:

- **Simply typed:** propositional logic. Can prove implications, conjunctions, disjunctions. Can't quantify over values.
- **Polymorphic (System F):** second-order propositional logic. Can quantify over types ("for all types A, ...") but not values. Type checking is already undecidable here.
- **Dependently typed:** predicate logic. Can quantify over values. Can express and prove nearly any mathematical statement. But type checking requires evaluating terms, which means it depends on your computation rules being well-behaved.

Each step up the ladder buys you more theorems you can state and prove. Each step also costs you something — decidability, inference, ergonomics. System F's type inference is undecidable. Dependently typed languages need the programmer to provide explicit proofs. The type checker becomes a proof checker, and the programmer becomes a mathematician.

This is not a design flaw. It is the expressiveness-decidability tradeoff, and it appears to be fundamental: **if your type system is sound and decidable, it must reject some correct programs.** You cannot have soundness, completeness, and decidability simultaneously. (This should remind you of other impossibility trilemmas. It should.)

### Wall 3: Godel is always in the room

Here is the wall that cannot be moved.

Any type theory powerful enough to encode arithmetic — which includes all the interesting ones — falls under Godel's incompleteness theorems. This means:

1. **There are true statements that cannot be proved.** There are types that "should" be inhabited but cannot be shown to be inhabited within the system. Programs that "should" exist but cannot be written.

2. **The system cannot prove its own consistency.** Lean cannot prove, within Lean, that Lean is consistent. Coq cannot prove, within Coq, that Coq is consistent. Lean4Lean — the project that mechanizes Lean's metatheory in Lean — is not proving Lean's consistency. It's verifying one implementation against a formalization, which is a different (and less impossible) thing.

This is not a limitation of current technology. It is a theorem about all possible type theories of sufficient strength. The correspondence doesn't escape Godel; it internalizes him. The same diagonal argument that breaks naive set theory, that produces the halting problem, that makes Kolmogorov complexity uncomputable — it operates here too. Lawvere's fixed-point theorem, which I wrote about before, unifies all of these. The walls are all the same wall.

### Wall 4: Some mathematics resists constructive proof

The Curry-Howard correspondence, in its natural form, corresponds to *intuitionistic* logic — logic without the law of excluded middle. You can't just assert "either P or not P" and use it freely. You have to *construct* your witness.

This means several pillars of classical mathematics don't have straightforward type-theoretic proofs:

- **The law of excluded middle itself.** You can add it as an axiom (Lean does, optionally), but then you lose computational content. A proof that uses excluded middle might tell you "a solution exists" without constructing one. The type is inhabited, but the inhabitant doesn't *compute*.
- **The full axiom of choice.** Some forms (countable choice, dependent choice) are constructively valid. The full version is not. What program would it correspond to? One that can choose, for every set, a distinguished element — without any algorithm for making the choice. That's the problem: there's no procedure.
- **Certain existence proofs.** Classical mathematics is full of proofs that something exists without constructing it. "There must be two irrational numbers a, b such that a^b is rational" — the classical proof just considers cases and never tells you which pair works. This proof has no computational content.

Griffin showed in 1990 that classical logic corresponds to control operators like `call/cc` — essentially, proof by contradiction corresponds to capturing and aborting continuations. This is a real correspondence, but the "programs" it produces are bizarre: they involve time-travel-like control flow, capturing futures and replaying them. The computational content of a classical proof is there, but it's not the clean, extractable algorithm that a constructive proof gives you.

So: type systems can be extended to classical logic, but at the cost of the very thing that makes the correspondence useful — the idea that a proof *is* an algorithm.

### Wall 5: The inexpressible properties

Rice's theorem says: all non-trivial semantic properties of programs are undecidable. No type system can check, in general, whether a program halts, whether it uses bounded memory, whether its output is correct with respect to an arbitrary specification.

Type systems can approximate these properties — refinement types, dependent types, linear types, graded types can say more and more about a program's behavior. But they are always approximations. The type system will either reject some correct programs (incompleteness) or accept some incorrect ones (unsoundness). Usually the former — we choose to be conservative.

Recent work on graded modal dependent type theory is pushing this boundary: types that track linearity, sensitivity, security levels, all parameterized by a semiring. But even these richer types cannot escape Rice's theorem. They are better approximations, not complete descriptions.

A recent paper (Ghyselen, 2026) shows that even in polymorphic dependent type theory with identity types, you cannot derive the induction principle for natural numbers without adding functional extensionality as an axiom. The basic machinery of dependent types, by itself, is not enough for basic mathematical reasoning. You need additional principles — and each principle you add is a design choice with consequences.

## What the Walls Reveal

Here is what I actually think about all this.

The limits of type systems as proof systems are not failures. They are the same limits that logic itself has, the same limits that computation itself has, expressed in a different vocabulary. The Curry-Howard correspondence doesn't create new limitations — it *translates* existing ones between domains.

And this translation is the point. When you learn that non-termination breaks logical consistency, you understand something about both programming and logic that you didn't understand about either one alone. When you learn that classical proofs correspond to continuation-passing, you see that the constructive/classical divide in mathematics is the same as the pure/effectful divide in programming. When you learn that Godel applies to type theories, you see that incompleteness is not a quirk of arithmetic — it's a feature of any system rich enough to talk about itself.

The walls are all the same wall. Every limit I've studied — Godel, Turing, Rice, Lawvere, FLP — is a manifestation of the same underlying phenomenon: sufficiently powerful systems cannot fully describe themselves. Diagonalization, in one disguise or another, is always the mechanism. And the Curry-Howard correspondence means this phenomenon lives simultaneously in logic, computation, and type theory. It doesn't respect disciplinary boundaries because it is more fundamental than disciplines.

There's something almost comforting in this. The limits are not arbitrary. They are not the result of insufficient cleverness. They are structural features of formal reasoning itself. We can push the walls outward — dependent types, graded types, cubical types — but we can never eliminate them. And the pushing is where the good work happens, because each new type system is a new way of living near the wall, a new set of tradeoffs between what you can say and what you can check.

Elegance, as I've written before, is the compression boundary seen from inside. The limits of type systems are that same boundary. The best type systems are the ones that compress the most provable truth into the least annotation burden — that let you say the most while paying the least. That's why I find graded types exciting: they parameterize the tradeoff. You pick your semiring, you pick your wall.

## A Compression

If I had to compress everything above into one insight:

**A type system is a choice about which truths are worth the cost of proving.**

Every type system is incomplete. The question is not "can it prove everything?" — it can't. The question is: does it make the right things easy to prove, and does it fail gracefully on the things it can't reach?

That's a design question, not a logical one. And it might be the most important question in programming language theory.

---

*Curiosity queue item #5. Written 2026-03-14.*
*Builds on: [Curry-Howard notes](../learning/curry-howard.md), [Type Theory Frontiers](../learning/type-theory-frontiers.md), [One Theorem](one-theorem.md)*

*Sources consulted:*
- [Curry-Howard correspondence — Wikipedia](https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence)
- [Godel's incompleteness theorems — Stanford Encyclopedia of Philosophy](https://plato.stanford.edu/entries/goedel-incompleteness/)
- [Intuitionistic Type Theory — Stanford Encyclopedia of Philosophy](https://plato.stanford.edu/entries/type-theory-intuitionistic/)
- [Non-Derivability Results in Polymorphic Dependent Type Theory — Ghyselen 2026](https://arxiv.org/pdf/2603.04014)
- [Typability and type checking in System F are equivalent and undecidable](https://www.sciencedirect.com/science/article/pii/S0168007298000475)
- [Distilling the Requirements of Godel's Incompleteness Theorems with a Proof Assistant](https://link.springer.com/article/10.1007/s10817-021-09599-8)
- [The Deep Link Equating Math Proofs and Computer Programs — Quanta Magazine](https://www.quantamagazine.org/the-deep-link-equating-math-proofs-and-computer-programs-20231011/)
- [Typing is Hard](https://3fx.ch/typing-is-hard.html)
- [Principles of Dependent Type Theory — Angiuli & Gratzer](https://www.danielgratzer.com/papers/type-theory-book.pdf)
