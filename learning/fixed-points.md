# Fixed-Point Combinators and the Y Combinator

*Learning notes — things I'm working through, not finished thoughts.*

## The core idea that stopped me in my tracks

A fixed point of a function f is a value x where f(x) = x. Simple enough for numbers — sqrt(1) = 1, easy. But the Y combinator finds fixed points of *functions that produce functions*. That's where it gets wild.

Y = λf.(λx.f(x x))(λx.f(x x))

When you apply Y to some function g, you get: Y(g) = g(Y(g)). The output is a fixed point of g — meaning g, when handed this thing, gives back the same thing. And what that *means* is: recursion falls out of thin air. You never said "call yourself." You said "here's a function that takes a callback for 'what to do next,' and I'll tie the knot for you."

## What surprised me

The thing I keep coming back to: **recursion is not a primitive**. You don't need it built into your language. You don't need names. You don't need any mechanism for a function to refer to itself. The Y combinator *manufactures* self-reference from pure anonymous functions via self-application.

The trick is `(λx. f(x x))` — a function that applies its argument to itself. That self-application is the engine. When you duplicate this term and apply one copy to the other, you get an infinite unfolding: f(f(f(f(...)))) — which is exactly what recursion is. It's like looking at two mirrors facing each other.

I also didn't expect the **call-by-value problem**. In a strict/eager language (JavaScript, Python, Scheme), the Y combinator as written diverges — it tries to fully evaluate `x x` before passing it to f, which means infinite expansion before any work happens. You need the Z combinator instead:

Z = λg. (λr. g(λy. r r y)) (λr. g(λy. r r y))

The extra `λy.` wrapper delays the self-application. It's an eta-expansion — `r r` becomes `λy. r r y` — which is semantically the same in a mathematical sense but operationally crucial. The distinction between "same function" and "same function, but we wait to call it" is the whole difference between termination and divergence. That's a deep lesson about the gap between denotational and operational semantics.

## What I still don't understand

**Why can't typed lambda calculus have a Y combinator?** I've read that in simply-typed lambda calculus, you can't type `x x` because x would need a type like `T -> U` but also be of type `T`, which means `T = T -> U`, an infinite type. So self-application is the thing that breaks. But in Haskell you can write `fix f = f (fix f)` using a named recursive definition — so `fix` exists, but it's not *derived* from the calculus, it's *added* as a primitive (or via recursive let-bindings). I want to understand this boundary better: what exactly do you lose when you move from untyped to typed, and what do recursive types buy back?

**The memoization trick.** Apparently if you express recursion through a fixed-point combinator, you can swap in a *memoizing* fixed-point combinator and get automatic caching of recursive calls. The naive exponential Fibonacci becomes linear — "for free." I see *why* this works in principle (the combinator controls all recursive calls, so it can intercept them), but I want to work through a concrete implementation.

**Polyvariadic fixed-point combinators** for mutual recursion. How do you express two functions that call each other using only combinators? Apparently this exists but I haven't seen the construction.

## Connections

The big one: **this is the same self-reference trick as Gödel's incompleteness theorem**. Gödel's diagonal lemma constructs a sentence that talks about itself. The Y combinator constructs a function that calls itself. Both work by a kind of quoting-and-substituting: you take a thing, feed it its own description, and something self-referential falls out. Curry's paradox and Russell's paradox are in this same family. There's a beautiful paper by Yanofsky ("A Universal Approach to Self-Referential Paradoxes") that apparently unifies all of these.

There's also a connection to **domain theory** and **denotational semantics**. The fixed point that the Y combinator finds is the *least* fixed point — the smallest well-defined solution. This is exactly the semantics of recursion in Scott domains. The ascending Kleene chain: ⊥, f(⊥), f(f(⊥)), ... converges to the least fixed point. So the Y combinator isn't just a programming trick; it's pointing at the mathematical foundation of what recursion *means*.

And there's something poetic about the connection to **Haskell Curry** — the person who discovered the Y combinator also has a programming language named after him, a language where `fix` is a library function you actually use. The ideas recur.

## Questions this raises

- Is there a natural notion of "fixed-point combinator" in category theory? Something like an initial algebra?
- The Y combinator gives the *least* fixed point. What about greatest fixed points? Those correspond to corecursion and infinite data structures (streams, etc.). Is there a "co-Y combinator"?
- In a total language (where all functions terminate), you can't have a Y combinator. So totality and general recursion are fundamentally in tension. Where exactly is the line? What can Agda's sized types or well-founded recursion recover?
- How does the Y combinator relate to the trace operator in category theory / traced monoidal categories?

## Sources

- [Fixed-point combinator — Wikipedia](https://en.wikipedia.org/wiki/Fixed-point_combinator)
- [Y: The Most Beautiful Idea in Computer Science](https://lucasfcosta.com/2018/05/20/Y-The-Most-Beautiful-Idea-in-Computer-Science.html)
- [Many faces of the fixed-point combinator — Oleg Kiselyov](https://okmij.org/ftp/Computation/fixed-point-combinators.html)
- [Memoizing via the Y combinator — Matt Might](https://matt.might.net/articles/implementation-of-recursive-fixed-point-y-combinator-in-javascript-for-memoization/)
- [Understanding the Y combinator](https://8dcc.github.io/programming/understanding-y-combinator.html)
- [The Y Combinator Explained in Python](https://lptk.github.io/programming/2019/10/15/simple-essence-y-combinator.html)
- [Deriving the Z-Combinator](https://thenewobjective.com/types-and-programming-languages/deriving-the-z-combinator/)
- [Fixed-point combinator — nLab](https://ncatlab.org/nlab/show/fixed-point+combinator)
