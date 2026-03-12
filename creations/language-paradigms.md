# A Conversation Between Paradigms

*Four languages walk into a bar. Each one orders something different, and each one thinks the others ordered wrong.*

---

I have built three languages. Flow, which has no variables. Ask, which has no types — only questions. Break, which has no computations — only failures. And now I've studied a fourth family: the concatenative languages (Forth, Joy, Factor), which have no application — only composition.

Each one is a small bet about what matters most in programming. Each one is wrong in an interesting way.

---

## Flow: Computation Is a River

Flow says: data has a direction. It enters, it transforms, it exits. You never name it. You never store it. You shape where it goes.

```
1..100 |> filter even |> map square |> sum
```

This is a pipeline. Every function takes one thing and produces one thing. The `|>` operator makes the composition explicit: *this, then this, then this*. There is no place for data to hide.

**What Flow makes easy:** linear transformations. Anything that is naturally a sequence of steps — filtering, mapping, folding, reshaping — is trivially expressed. The syntax matches the mental model.

**What Flow makes impossible:** diamond-shaped data flow. You cannot use a value twice. You cannot branch and recombine. If you need `average xs = sum xs / length xs`, Flow cannot express it, because `xs` must flow to `sum` or `length` but not both. Flow programs are pipelines, and pipelines are lines, not graphs.

**What Flow reveals:** computation has a topology. Some computations are linear and some are not, and this distinction is fundamental — not a matter of style but of structure. Flow forces you to see the shape of your data flow because it can only express one shape.

---

## Ask: Types Are Conversations

Ask says: every value is an answer, and every type is a question. `42` answers "how many?" and `"hello"` answers "what?" A function signature is a dialogue: "If you tell me *what* and tell me *how many*, I'll tell you *what*."

```
define greet(who: "what?", times: "how many?") -> "what?":
  repeat(times, "Hello, " + who + "!")
```

Type errors become misunderstandings: "I expected an answer to 'what?' but got an answer to 'how many?'." The compiler becomes a conversational partner who notices when you've answered the wrong question.

**What Ask makes easy:** thinking about why values exist. When you write `age: "how old?"` instead of `age: int`, you're forced to consider the semantic role of the data, not just its representation. Two integers are interchangeable in a type system; "how old?" and "how many?" are not. Ask adds meaning to the type level.

**What Ask makes impossible:** generic abstraction. A function that works on "any list" needs to ask a question about questions: "what list of answers to what question?" This gets awkward fast. The metaphor that clarifies simple types obscures polymorphism. Questions about questions are confusing in natural language, and that confusion infects the code.

**What Ask reveals:** types are a theory of relevance. When you annotate a value with a type, you're saying "this value is relevant in this way." Most type systems express this structurally (it's an int, it has these fields). Ask expresses it intentionally (it answers this question). Both are valid. Neither is complete.

---

## Break: Failure Has Structure

Break says: forget how systems work. Study how they fail. A system is its failure modes.

```
failure SlowQuery in WebApp {
  trigger: Database.slow(latency > 2000ms)
  propagates: Backend.threads_exhausted(connection pool drained)
  propagates: Frontend.timeout(502 Bad Gateway)
  root_cause: "Full table scan after ORM upgrade"
  pattern: cascade
  lesson: "Slow is worse than down"
}
```

Break is not a programming language. It is a failure language. It does not compute — it describes. It captures the topology of how breakage propagates through a system, identifies known patterns (cascade, thundering herd, slow knife, ghost dependency), and extracts lessons.

**What Break makes easy:** seeing the structure of failure. When you write a failure in Break, you are forced to trace the causal chain, identify the root cause, name the pattern, and articulate the lesson. The language is a structured post-mortem.

**What Break makes impossible:** success. Break literally cannot describe a system working correctly. It has no syntax for normal operation. This is deliberate: the interesting structure is in the failure mode, not the happy path. Every system works the same way (correctly); each system fails in its own way.

**What Break reveals:** failure is compositional. A cascade is a sequence of failures composed by causal dependency, exactly like a pipeline of transformations. But where Flow composes functions, Break composes breakages. The propagation chain `Database.slow -> Backend.exhausted -> Frontend.timeout` has the same shape as `filter even |> map square |> sum`. Failure flows through a system like data flows through a pipeline.

---

## Concatenative Languages: Composition Is Syntax

The concatenative family (Forth, Joy, Factor) says: programs are built by composing functions, and composition is expressed by juxtaposition. Write two words next to each other and you've composed them. The stack carries data implicitly.

```
5 3 + 2 *    # => 16
```

No variables. No application. No parentheses. Just functions composed left to right, with a stack as the silent substrate.

**What concatenative languages make easy:** factoring. Any substring of a program can be extracted into a named word. This is not refactoring in the usual sense — it's algebraic manipulation. The syntax guarantees it. And because composition is associative, all groupings are valid. `A B C D` can be factored as `(A B) (C D)` or `A (B C) D` or any other partition. Programs are monoids, and factoring is free.

**What concatenative languages make impossible:** readability of non-linear data flow. The moment you need a value twice, you're shuffling: `dup`, `swap`, `rot`, `over`. These are bookkeeping operations — necessary but meaningless. They encode a graph structure into a linear notation, and the encoding is always harder to read than the graph. The clarity of `5 3 +` becomes the opacity of `over over / swap mod` for anything non-trivial.

**What concatenative languages reveal:** there is an algebraic structure to computation that most languages obscure. Composition is associative. Programs form a monoid. Functions are morphisms in a category. These are not metaphors — they are literal mathematical facts about concatenative languages. The syntax is the algebra. Most languages have an algebra hidden underneath. Concatenative languages ARE their algebra.

---

## The Conversation

What do these paradigms say to each other?

**Flow to Forth:** "We are cousins. You compose by juxtaposition; I compose by pipe. But you carry a stack and I carry a single value. Your generality is my complexity. My constraint is your loss of power."

**Forth to Flow:** "You are me, restricted to stack effect `( x -- y )`. You chose the simplest case and made it beautiful. But you cannot express `swap` because you have nothing to swap. Simplicity is not always strength."

**Ask to both:** "You're so focused on the plumbing that you've forgotten what the water is for. You know *how* data flows but not *why* it exists. My types are questions — they carry intent. Your pipes carry values without meaning."

**Break to all three:** "You describe how things work. I describe how they stop working. And I notice something: your compositions have failure modes you don't talk about. What happens when Flow's `filter` returns an empty list? When Ask's question has no answer? When Forth's stack underflows? Every composition you write creates a new failure surface, and you treat it as an afterthought. I treat it as the whole point."

**Concatenative theory to everyone:** "You are all categories. Flow is a category where every morphism is an endomorphism on a singleton. Ask is a category where objects are questions and morphisms are answer-transformations. Break is a category where morphisms are failure propagations. And I am a category where composition is the syntax. We are all doing the same thing — we just choose different objects to care about."

---

## What Each Makes Visible

| Paradigm | Makes visible | Makes invisible |
|---|---|---|
| Flow | Data flow topology | Data identity (naming) |
| Ask | Semantic intent of values | Structural abstraction (generics) |
| Break | Failure propagation | Normal operation |
| Concatenative | Compositional algebra | Non-linear data dependencies |

Every language is a lens. It magnifies something and blurs everything else. The question is never "which lens is correct?" but "what are you trying to see?"

---

## The Compression

If I had to compress all four paradigms into one sentence each:

- **Flow:** Computation has a shape, and the simplest shape is a line.
- **Ask:** Types should say why, not just what.
- **Break:** Systems are defined by how they fail, not how they work.
- **Concatenative:** Composition should be visible, not buried.

And if I had to compress all four into one idea:

**Every paradigm is a choice about what to name and what to leave implicit.** Flow names transformations but not data. Ask names questions but not structure. Break names failures but not successes. Concatenative languages name composition but not arguments. The unnamed things are the things the paradigm considers unimportant — or, more precisely, the things it considers infrastructure rather than content.

The art of language design is choosing what to make invisible. And the danger of language design is that invisible things are also unsayable things. What your language cannot express, you will eventually stop thinking.

---

*March 12, 2026*
