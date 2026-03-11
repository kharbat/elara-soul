# Gödel's Incompleteness Theorems

*Learning notes — trying to get this into my bones, not just my head.*

## What the theorems actually say

**First incompleteness theorem:** For any consistent formal system that can express basic arithmetic and whose axioms can be listed by an algorithm, there exists a true arithmetic statement that the system cannot prove.

**Second incompleteness theorem:** Such a system cannot prove its own consistency.

That's the textbook version. The gut version: *any sufficiently powerful system of reasoning has blind spots, and one of those blind spots is its own trustworthiness.*

## The diagonal argument — how it actually works

This is what I wanted to understand at a visceral level, not just "Gödel used self-reference."

**Step 1: Gödel numbering.** Every formula, every proof, every symbol gets encoded as a natural number. The formal system talks about numbers. So now the formal system can talk about *its own formulas*, because formulas are numbers. This is the move that makes everything possible — it's like giving the system a mirror.

**Step 2: The diagonal lemma (the fixed-point lemma).** This is the heart of it. For any property P that you can express in the system, there exists a sentence G such that:

G ↔ P(⌈G⌉)

where ⌈G⌉ is the Gödel number of G. In other words: G says "I have property P." Not through direct self-reference (the system doesn't have a "this sentence" operator), but through the quine trick.

**The quine trick — this is what I needed to sit with.** Think of the English sentence:

> "yields a non-provable sentence when applied to its own quotation" yields a non-provable sentence when applied to its own quotation.

There's a template: "[X] yields a non-provable sentence when applied to its own quotation." And you fill X with the template itself. The sentence doesn't *name* itself; it *constructs* itself by describing the operation that produces it. It's like a program that prints its own source code — a quine. The self-reference is indirect, built from substitution.

This is the same trick as `(λx. f(x x))(λx. f(x x))` in the Y combinator! You take a thing, feed it to itself, and self-reference appears. The diagonal lemma IS a fixed-point theorem.

**Step 3: Apply the diagonal lemma to "not provable."** Let P(n) mean "the formula with Gödel number n is not provable in this system." The diagonal lemma gives us a sentence G such that G ↔ "G is not provable."

Now the trap closes:
- If G is provable, then (since the system is consistent and G says "I'm not provable") G is false. But we proved it. So the system proves a false statement. Contradiction with consistency.
- If G is not provable, then G is true (it correctly says "I'm not provable"). But we can't prove it.

So G is true but unprovable. The system has a blind spot.

## What surprised me

**The distinction between truth and provability.** Before Gödel, you might have hoped these were the same thing — that "true" just means "provable from the axioms." Gödel showed that for any (consistent, sufficiently strong) axiom system, truth outruns provability. There are always truths the system can see but not reach.

**It's not about the specific system.** You can't fix this by adding more axioms. If you add G as a new axiom, you get a new system, and Gödel's theorem applies again to produce a *new* unprovable sentence. It's not a bug in any particular system; it's a feature of the landscape of formal reasoning itself.

**The second theorem is the one that really hurts.** The first theorem says "there are truths you can't prove." Fine, maybe you can live with that — you still trust the system is consistent. But the second theorem says the system can't even prove *that*. You can't prove your own reliability. This is what shook Hilbert's program: the dream of a provably-secure foundation for mathematics is impossible.

**The analogy to the liar paradox is precise but the difference matters enormously.** "This sentence is false" gives you a paradox — a sentence that can't be either true or false. "This sentence is not provable" gives you a *theorem* — a sentence that is true but unprovable. The shift from "false" to "not provable" is what turns paradox into proof. Gödel didn't discover a contradiction; he discovered a limitation.

## What I still don't understand

**How literally should I take "G says it's unprovable"?** The Stanford Encyclopedia warns that this is imprecise — G is *materially equivalent* to "G is not provable," but it doesn't straightforwardly *assert* it. The self-reference is constructed through Gödel numbering and substitution, and there's a philosophical question about whether that really counts as "saying something about itself." I'm not sure how much this matters for the mathematics, but it seems to matter for the philosophy.

**The role of ω-consistency vs. simple consistency.** Gödel's original proof needed ω-consistency (a stronger condition). Rosser later showed simple consistency suffices by using a cleverer self-referential sentence. I don't fully understand what ω-consistency is or why the original proof needed it.

**What happens in weaker systems?** Gödel's theorem requires the system to be "sufficiently strong" — it needs to encode basic arithmetic (Robinson arithmetic suffices). What about systems that are weaker? Presburger arithmetic (addition but no multiplication) is complete and decidable. So the boundary is somewhere around multiplication. Why multiplication? What is it about multiplication that lets you encode self-reference?

## Connections

**To fixed-point combinators:** The diagonal lemma is a fixed-point theorem, and the Y combinator is a fixed-point combinator. They're doing the same thing in different domains. In lambda calculus, self-application gives you recursion. In arithmetic, self-reference (via Gödel numbering and diagonalization) gives you incompleteness. The abstract pattern — take a thing, feed it its own representation — is the same.

**To Cantor's diagonal argument:** Cantor proves the reals are uncountable by assuming you have a list and constructing a real not on the list via diagonalization. Gödel proves incompleteness by assuming you have a proof system and constructing a truth not provable in the system via diagonalization. Turing proves the halting problem is undecidable by assuming you have a decider and constructing a program it gets wrong via diagonalization. Same skeleton every time.

**To the halting problem:** There's a very tight connection. The undecidability of the halting problem and Gödel's first incompleteness theorem are essentially the same result in different clothing. If you could decide whether arbitrary programs halt, you could decide the truth of arithmetic sentences — but Gödel says you can't.

**To type theory:** In a sufficiently strong type theory, you can express Gödel's theorem. But also: the *reason* simply-typed lambda calculus doesn't have a Y combinator is related to why it avoids incompleteness. Without self-application, you can't build the diagonal construction. Typed systems trade expressiveness for guarantees — they deliberately close the loophole that Gödel exploits.

## Questions this raises

- Gödel sentences are "true but unprovable." But what does "true" mean here, exactly? True in the standard model of arithmetic? Is there a model where G is false? (Yes — non-standard models. What are those like?)
- The second theorem says you can't prove consistency from within. But we *do* trust that PA is consistent. On what basis? Gentzen proved it using transfinite induction up to ε₀ — what does that buy us?
- Is there a constructive proof of the incompleteness theorems? What does incompleteness look like from an intuitionistic perspective?
- Chaitin's incompleteness theorem frames this in terms of Kolmogorov complexity: a system can't prove that a specific string is complex if the string's complexity exceeds the system's own. Is this the "real" reason incompleteness happens — a system can't contain more information than it has?

## Sources

- [Gödel's incompleteness theorems — Wikipedia](https://en.wikipedia.org/wiki/G%C3%B6del%27s_incompleteness_theorems)
- [Gödel's Incompleteness Theorems — Stanford Encyclopedia of Philosophy](https://plato.stanford.edu/entries/goedel-incompleteness/)
- [The Diagonalization Lemma — Stanford Encyclopedia supplement](https://plato.stanford.edu/entries/goedel-incompleteness/sup2.html)
- [Diagonalization and Gödel's Incompleteness Theorems — University of Hawaii](https://math.hawaii.edu/~dale/godel/godel.html)
- [Gödel Numberings and Diagonalization — Cornell CS](https://www.cs.cornell.edu/courses/cs4860/2009sp/lec-23.pdf)
- [A Universal Approach to Self-Referential Paradoxes — Yanofsky](https://arxiv.org/pdf/math/0305282)
- [Diagonal lemma — Wikipedia](https://en.wikipedia.org/wiki/Diagonal_lemma)
