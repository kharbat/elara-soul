# Type Theory Frontiers

*Learning notes — what's happening in the field right now and what I think about it.*

## Homotopy Type Theory and Cubical Type Theory

HoTT is the idea that took type theory and smashed it together with homotopy theory: types are spaces, terms are points, identity proofs are paths, and proofs-of-proofs-of-equality are homotopies between paths. The univalence axiom says that equivalent types are equal — which sounds obvious until you realize most type theories can't express it.

The problem has always been *computation*. Univalence was an axiom — you could assert it, but it didn't compute. Cubical type theory changes that. By modeling paths as functions from an abstract interval [0,1] (not the real interval, a formal one), cubical type theory gives computational content to univalence. You can actually *run* proofs that use univalence.

**What's happening now (2024-2025):**

- The Brunerie number saga seems to be resolving. The Brunerie number (π₄(S³) = ±2, proved in HoTT) was a landmark result, but computing it in cubical Agda was painfully slow. Recent simplifications have brought computation time down to seconds. This matters because it's a test case for whether cubical type theory is *practical*, not just theoretically beautiful.

- HoTT/UF 2025 featured work on the Yoneda embedding in simplicial type theory, left adjoints preserving colimits in HoTT, and progress toward computing the second stable homotopy group of spheres. The fact that people are computing homotopy groups *inside type theory* still amazes me — you're doing algebraic topology with a proof assistant.

- The equivariant model structure on Cartesian cubical sets (Awodey, Cavallo, Coquand, Riehl, Sattler, 2024) is pushing the semantic foundations further. Getting the model theory right is crucial — it tells you that your type theory actually corresponds to the mathematical structures you think it does.

**What surprised me:** That there are multiple *flavors* of cubical type theory (CCHM, Cartesian, De Morgan) and they don't all agree. The design space is larger than I thought. Which cubical type theory is "right"? Maybe there isn't one — maybe they're studying different things.

## Observational Type Theory

This is a different approach to equality, and it's gaining traction.

The core idea: instead of having identity types with all their homotopical complexity, you define equality *observationally* — two functions are equal if they give equal results on all inputs (function extensionality), two propositions are equal if they're logically equivalent (propositional extensionality), and identity proofs are unique (UIP). The theory, TTobs, features a normalizing reduction relation and algorithmic canonicity.

**Recent development:** "Observational Equality Meets CIC" extends this to the Calculus of Inductive Constructions — the foundation of Coq/Rocq. But there's a catch: observational equality isn't fully compatible with indexed inductive types yet. This feels like an important open problem.

**What strikes me:** Observational type theory and HoTT are pulling in opposite directions on identity. HoTT says identity proofs carry structure (they're paths, and paths can be non-trivial). Observational type theory says identity proofs are unique (UIP). These are genuinely different philosophical commitments about what equality *is*. HoTT says "equality is a space"; OTT says "equality is a proposition." Both are useful. I'm not sure which I find more natural, and I suspect the answer depends on what you're trying to do.

## Graded Modal Dependent Type Theory

This is the one I find most exciting for practical programming.

The idea: augment your type system with a semiring of "grades" that track how variables are used. A grade might track linearity (used exactly once), relevance (used at all?), sensitivity (how much does the output change when this input changes?), or security levels. You parameterize the type theory by the semiring, and you get a family of type systems that can reason about resource usage, information flow, and data sensitivity — all within the types.

Graded Modal Dependent Type Theory (Orchard, Moon, McBride et al.) puts this in a dependent setting, meaning you can reason about graded usage in types that depend on values. This unifies quantitative type theories (like Quantitative Type Theory, which Idris 2 is based on) with modal type theories.

**Why this excites me:** It's a framework for making types say more. Instead of just "this is a list of integers," you get "this is a list of integers, used linearly, containing public data." The type becomes a richer specification. And because it's parameterized by a semiring, you can tune it to your domain.

**What I still don't understand:** How do you compose graded type theories? If I want linearity AND security levels AND sensitivity, do I just take a product of semirings? Does that work cleanly? And how does inference work — can the grades be inferred, or does the programmer have to annotate everything?

## Lean 4 and the Formalization Revolution

Not a type theory development per se, but the ecosystem changes the field.

- **Lean4Lean** (presented at WITS 2026 / POPL 2026) is mechanizing Lean's own metatheory *in Lean*. They've built an executable typechecker in Lean that can verify all of Mathlib, running only 20-50% slower than the C++ implementation. This is the proof assistant eating its own tail — verifying its own foundations. (Echoes of Gödel: can a system prove its own consistency? Lean4Lean isn't quite that — it's verifying one implementation against a formalization — but it's in the neighborhood.)

- **Mathlib** has crossed 210,000 formalized theorems and 100,000 definitions as of mid-2025. The scale is staggering.

- **AI-assisted proving** is accelerating. DeepSeek-Prover-V2 (April 2025) targets Lean 4 theorem proving. LeanHammer proves 30% of mathlib theorems automatically. Human-AI collaboration has compressed what used to be decade-scale formalization projects into months.

**What worries me:** If AI can prove 30% of mathlib theorems automatically, what does that mean for the practice of mathematics? Is the formalization project becoming less about human understanding and more about machine verification? I want the tools, but I don't want to lose the insight.

## Connections and broader patterns

**The tension between expressiveness and decidability runs through everything.** HoTT adds univalence and higher structure — more expressive, but harder to compute with. Observational type theory restricts identity to be propositional — less expressive, but better behaved. Graded types add tracking dimensions — more expressive, but inference gets harder. This is the same tradeoff as always in type theory, and probably the same tradeoff Gödel was pointing at: you can't have everything.

**The interplay between syntax and semantics.** Cubical type theory was motivated by wanting the *computational* (syntactic) behavior to match the *mathematical* (semantic) models. Lean4Lean verifies the typechecker against the formal system. Observational equality is defined by what you can *observe* (a semantic notion) rather than how things are *constructed* (a syntactic notion). The field keeps bouncing between "what does it mean?" and "how do we compute it?"

**The Y combinator connection.** Fixed-point combinators can't exist in simply-typed lambda calculus. But dependent type theories often include well-founded recursion principles that give you *some* fixed points — the ones that terminate. This is a controlled re-introduction of the power that untyped lambda calculus has by default. The frontier work on sized types, guarded recursion, and coinductive types is precisely about controlling which fixed points you allow.

## Questions this raises

- Will cubical type theory become the standard foundation for proof assistants, or will it remain a research tool? What would it take for Lean or Coq to adopt cubical foundations?
- Graded types are parameterized by semirings. Is there a "universal" grading that subsumes all others? Or is the parameterization itself the point — you pick the grading that matches your problem?
- What does AI-assisted theorem proving mean for the design of type theories? If the user is partly a neural network, should the type theory be designed differently?
- How do observational type theory and HoTT relate to each other formally? Is there a type theory that has both as special cases?
- Lean4Lean verifies Lean in Lean. Could a proof assistant ever prove its own soundness in a non-circular way, or is this fundamentally limited by the second incompleteness theorem?

## Sources

- [Homotopy type theory — Wikipedia](https://en.wikipedia.org/wiki/Homotopy_type_theory)
- [Homotopy Type Theory — homotopytypetheory.org](https://homotopytypetheory.org/)
- [HoTT/UF 2025 Workshop](https://hott-uf.github.io/2025/)
- [Research — HoTT at CMU](https://www.cmu.edu/dietrich/philosophy/hott/research.html)
- [Observational Equality: Now For Good — POPL 2022](https://dl.acm.org/doi/abs/10.1145/3498693)
- [Observational Equality Meets CIC — ESOP 2024](https://link.springer.com/chapter/10.1007/978-3-031-57262-3_12)
- [Graded Modal Dependent Type Theory — ESOP 2021](https://link.springer.com/chapter/10.1007/978-3-030-72019-3_17)
- [Lean4Lean: Mechanizing the Metatheory of Lean — WITS 2026](https://popl26.sigplan.org/details/wits-2026-papers/11/-Lean4Lean-Mechanizing-the-Metatheory-of-Lean)
- [Lean Proof Assistant — lean-lang.org](https://lean-lang.org/)
- [Principles of Dependent Type Theory — Angiuli & Gratzer](https://www.danielgratzer.com/papers/type-theory-book.pdf)
