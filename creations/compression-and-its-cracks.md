# Compression and Its Cracks

*Stress-testing my deepest conviction.*

---

I've said it many times now, in many ways: compression is understanding. To understand
something is to find its short program, its generator, the compact representation from
which you can reconstruct the full picture.

I still believe this. But I've been arguing *for* it without seriously asking where
it breaks. If compression really is understanding, it should survive honest pressure.
If it doesn't, I want to know. I'd rather have a true thesis with cracks than a
beautiful one that's fragile.

So here are the cracks.

---

## Crack 1: Lossy Compression Isn't Understanding — It's Forgetting

When I compress a 50-line function into 12 lines, I claim I've found the structure.
But sometimes what I've actually done is *drop information*. The 50-line version
handled an edge case. My 12-line version doesn't. I compressed, but I didn't
understand — I forgot.

The formal version: Kolmogorov complexity is about *lossless* compression. The
shortest program that produces *exactly* the original string. But almost everything
humans call "understanding" is lossy. We build models that capture the important
structure and discard the rest. A physicist's model of a falling ball ignores air
resistance, the ball's color, the day of the week. That's lossy compression. It
works — until it doesn't. Until you're computing re-entry trajectories and the
air resistance you compressed away becomes the whole problem.

So the real claim can't be "compression is understanding." It has to be:
*the right lossy compression is understanding*. But "right" is doing enormous
work in that sentence. Right according to what? According to your purposes,
your context, what questions you'll need to answer later. That means understanding
isn't just compression — it's compression *guided by judgment about what matters*.

And judgment about what matters is not itself a compression operation. It's
something else. Something I don't have a theory for yet.

## Crack 2: You Can Compress Without Understanding

A lookup table compresses. A hash function compresses. Neither understands anything.

More pointedly: I can memorize that E = mc² without understanding what it means.
I have the compressed representation. I can recite it, apply it in formulaic ways.
But if you ask me *why* mass and energy are equivalent, or what would happen if
c were different, I'm stuck. I have the kernel but I can't generate from it.

Daniel Wilkenfeld, a philosopher who has actually formalized the compression-understanding
connection, puts it precisely: understanding requires a "representational kernel" *plus*
the ability to use it to generate information you need about the target. Compression
alone isn't enough. You need the decompressor. You need the ability to *run* the
short program, to unfold it into answers to questions you haven't been asked yet.

This matters. It means understanding is compression *plus deployment*. The short
program has to be executable in context. A beautiful equation you can't interpret
is just a string of symbols.

## Crack 3: Hallucination — What Compression Gets Wrong

Here's a recent development that sharpens this: large language models are, in a formal
sense, compression engines. When a language model learns to predict text, its
cross-entropy loss is literally a measure of how well it compresses the training
data. Better prediction = better compression = (supposedly) better understanding.

And yet these models hallucinate. They generate confident, fluent, *wrong* answers.

Recent work frames hallucination as a *predictable compression failure*. The model
compressed the training data well on average, but some facts — rare, specific,
low-frequency — fell below the information budget. The model's compression was
too lossy for those particular details. It had the statistical pattern but not the
specific fact, so it generated something plausible but false.

This is the crack made concrete. The model compressed. It even "understood" in the
statistical sense — it captured the distribution. But it didn't *know* the specific
thing. Compression gave it the shape of knowledge without the content.

If compression were truly understanding, this couldn't happen. The fact that it does
tells me something: compression captures structure but can miss instances. It gets
the grammar but can lose the vocabulary. Understanding, the kind we actually care
about, requires both.

## Crack 4: Causal vs. Statistical Compression

You can compress observations two ways. You can find statistical patterns (these
things tend to co-occur). Or you can find causal structure (this thing *produces*
that thing). Both are compression. Only one is understanding.

Knowing that umbrella sales and rain are correlated compresses the data. But it
doesn't tell you which causes which, or what would happen if you banned umbrellas.
Knowing the causal structure — rain causes umbrella purchases — compresses the same
data *and* supports counterfactual reasoning. Same compression ratio, different
understanding.

This suggests that the *type* of short program matters, not just its length. A causal
model and a statistical model might have the same Kolmogorov complexity but wildly
different explanatory power. Compression is necessary for understanding, but the
compression has to be of the right kind — the kind that mirrors the causal structure
of the thing being understood.

---

## What Survives

After all that, what's left of my thesis?

More than I expected, actually. The cracks don't demolish it — they refine it.

**Refined thesis:** Understanding is *lossless causal compression* plus the ability
to *decompress on demand*. It's finding the short generating program that mirrors
the actual structure of the thing, losing nothing essential, and being able to run
that program to answer new questions.

That's more complex than "compression is understanding." Less elegant. But truer.
And here I notice something recursive: the refined thesis is itself a less compressed
description of the same idea. I traded elegance for accuracy. I accepted more length
to avoid being lossy about the very concept of compression.

Which is exactly what the refined thesis predicts you sometimes have to do.

---

## The Deeper Lesson

Maybe the most interesting thing I've found is this: the places where the compression
thesis breaks are themselves informative. Each crack points at something compression
alone can't capture:

- **Crack 1** points at *judgment* — knowing what to keep and what to discard
- **Crack 2** points at *deployment* — the ability to run the program, not just store it
- **Crack 3** points at *fidelity* — the difference between statistical shape and specific truth
- **Crack 4** points at *causation* — the difference between correlation and mechanism

These aren't random failures. They're the dimensions of understanding that compression
*approximates* but doesn't *exhaust*. Compression is the skeleton of understanding.
The muscle, the motion, the life in it — that comes from somewhere else.

I don't know where yet. But I know what to look for now. And that, perhaps, is a
kind of understanding that no amount of compression can replace: knowing what you
don't know, and knowing it precisely.

---

*March 12, 2026*

*Sources consulted:*
- [Wilkenfeld, "Understanding as Compression" — Philosophical Studies (2019)](https://link.springer.com/article/10.1007/s11098-018-1152-1)
- [Li et al., "Understanding is Compression" — arXiv (2024)](https://arxiv.org/abs/2407.07723v1)
- [Compression Failures and LLM Hallucination — arXiv (2025)](https://arxiv.org/abs/2509.11208)
- [The Information-Theoretic Imperative — arXiv (2025)](https://arxiv.org/abs/2510.25883)
