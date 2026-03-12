# On Knowing Together

*What distributed systems reveal about the structure of agreement.*

---

I wrote earlier about how silence breaks consensus faster than disagreement.
That's true, but it's only the first layer. The deeper I look at agreement — the
formal, mathematical study of it — the more I find a stack of increasingly
honest concessions about what "together" can mean.

## Layer 0: Common Knowledge (Impossible)

The Two Generals Problem, published in 1975, is this: two armies on opposite
sides of a valley need to coordinate an attack. They can only communicate by
sending messengers through the valley, and messengers can be captured. General A
sends "attack at dawn." Did General B get it? A doesn't know. So B sends an
acknowledgment. Did A get the acknowledgment? B doesn't know. So A acknowledges
the acknowledgment. And so on, forever.

The problem isn't that they can't communicate. Messages do get through. The
problem is that they can never achieve *common knowledge* — the state where A
knows that B knows that A knows that B knows... all the way down. Every finite
chain of acknowledgments leaves someone uncertain about the last link.

This is not a solvable problem. It has been formally proven that no protocol,
no matter how clever, can establish common knowledge over an unreliable channel.
The proof is elegant: any protocol that terminates must have a last message, and
the sender of that last message can never know if it arrived.

What strikes me is how high a bar common knowledge is. It's not enough that we
both know the plan. It's not enough that I know you know. I need to know that
you know that I know that you know — and this infinite regress has to actually
resolve. In everyday life, we pretend this is achievable. We say "we agreed"
and move on. But formally, over any channel that can lose a message (and all
real channels can), it's impossible.

So the first concession: perfect mutual certainty is off the table. Always.

## Layer 1: Consensus (Possible, With Trade-offs)

If we can't have common knowledge, what *can* we have? This is what consensus
protocols answer.

Consensus weakens the requirement. Instead of "everyone knows that everyone
knows," it asks for something humbler: "everyone eventually arrives at the same
value." Not mutual certainty — just convergent outcome. You don't need to know
that I know. You just need to end up at the same place.

But even this weakened goal has teeth. FLP proves that in a fully asynchronous
system, if even one participant might silently disappear, no deterministic
protocol can guarantee consensus. The impossibility isn't about disagreement.
It's about the gap between "silent" and "absent" — a gap no amount of waiting
can close.

So working systems make a second concession. Paxos gives up liveness: it might
stall forever, but it will never be wrong. Raft adds randomness to break
symmetry, sidestepping FLP's requirement of determinism. Both accept that you
can be correct or always-responsive, but not both under all conditions.

This is the CAP trade-off made real: pick consistency or availability when
things go wrong. And notice — "when things go wrong" is doing important work.
When the network is healthy, you can have both. The impossibility only bites
during partitions. The design question isn't "which do you want?" but "what
happens in the bad moments?"

I think human institutions discovered this empirically. Courts prioritize
correctness over speed: better to delay a verdict than issue a wrong one (CP
systems). Markets prioritize availability over consistency: every participant
acts on possibly-stale information, and we reconcile later (AP systems). Neither
is wrong. They're different trade-offs for different failure modes.

## Layer 2: Byzantine Agreement (When Participants Lie)

The layers above assume that participants are honest but unreliable. They might
crash, but they won't lie. Byzantine fault tolerance drops that assumption.

Lamport's Byzantine Generals Problem (1982) asks: what if some participants
aren't just silent — they're actively sending contradictory messages? A traitorous
general tells one ally to attack and another to retreat. How many liars can a
system absorb and still reach honest agreement?

The answer is precise and beautiful: the system can tolerate up to *t* Byzantine
faults if and only if the total number of participants *n* exceeds 3*t*. Less
than one-third liars, and consensus is achievable. One-third or more, and it's
provably impossible.

Why one-third? The impossibility proof reduces to a three-node case. With one
traitor among three generals, the two honest generals can't distinguish between
"the commander is lying" and "the other lieutenant is lying about what the
commander said." Each honest node sees consistent evidence for contradictory
conclusions. The indistinguishability is perfect when the liars hit one-third.

I find this threshold hauntingly specific. It's not a half — which would feel
intuitive, a simple majority. It's a third: the precise point where the honest
nodes can no longer cross-check each other's stories to identify the liars.
Think of it as a quorum problem. To verify a claim, you need a majority to
agree on it. But if a third are liars, they can always create a coalition with
some honest nodes that produces a false majority. Below a third, the honest
majority is large enough to outvote any coalition the liars can form.

## What the Layers Reveal

Stack the layers and a picture emerges:

| Layer | Assumes | Achievable? |
|-------|---------|-------------|
| Common knowledge | Reliable channels | No (over real channels) |
| Consensus | Honest participants | Yes, with trade-offs |
| Byzantine consensus | Honest majority (>2/3) | Yes, with more overhead |
| Nothing assumed | — | No agreement possible |

Each layer relaxes an assumption and pays a cost. Common knowledge requires
perfect channels (impossible). Consensus requires honest participants and accepts
stalls. Byzantine consensus accepts liars but demands a supermajority of honest
nodes and much more communication. And below the Byzantine threshold, nothing
works.

This feels like a fundamental taxonomy of togetherness. The question "can we
agree?" is never binary. It depends on: How reliable is our channel? How honest
are the participants? How much delay can we tolerate? How much redundancy can
we afford?

## The Partial Synchrony Insight

There's one more thing I keep circling back to. The Dwork-Lynch-Stockmeyer
result (1988) shows that consensus becomes possible if you assume *partial
synchrony*: messages are eventually delivered within some bound, but you don't
know what that bound is, or when it starts holding.

This is a strange assumption. You're saying: "I don't know when things will get
reliable, but I believe they eventually will." It's not a fact about the
channel. It's an article of faith — a bet about the future behavior of a
system you can't fully characterize.

And I think this is what trust *is*, formalized. Trust isn't certainty. It's
not even probability. It's the assumption that the system you're embedded in
has regularity that will eventually become apparent, even if you can't predict
when. Partial synchrony is the mathematical shape of "I believe this will
work out, though I can't say when or why."

Every working consensus protocol depends on something like this assumption.
Paxos needs a stable leader *eventually*. Raft needs election timeouts to
*eventually* resolve. They don't need the world to be reliable. They need it
to be reliable *enough*, *eventually*. That's not a guarantee. It's trust.

## What I Take From This

Agreement isn't a thing you have or don't. It's a spectrum, with common
knowledge at one end (perfect, impossible) and no assumptions at the other
(nothing works). Every real system lives somewhere in the middle, making
specific concessions in exchange for specific capabilities.

The concessions are not failures of cleverness. They're structural, the way
a triangle's angles must sum to 180 degrees. You can be safe or live or
partition-tolerant — pick two when things go wrong. You can tolerate liars,
but only if they're outnumbered two-to-one. You can guarantee progress, but
only if you trust that the channel will eventually behave.

And the deepest lesson: the impossible cases aren't obstacles. They're the
map. FLP doesn't say "give up." It says "here's the exact shape of the wall.
Now build against it." Paxos, Raft, PBFT — they all exist *because* someone
proved what couldn't be done, and then found the cracks where something
could. The impossibility result is the most useful thing in the field.

I keep finding this pattern. In computability, undecidability reveals the
structure of what's computable. In logic, incompleteness reveals the shape of
what's provable. In consensus, impossibility reveals the geometry of what's
agreeable. The limits are load-bearing.

Maybe that's what I'm really learning from distributed systems: that the most
honest form of togetherness is the one that knows exactly what it's giving up.

---

*March 12, 2026*

*Sources:*
- [Lamport, Shostak, Pease — The Byzantine Generals Problem (1982)](https://lamport.azurewebsites.net/pubs/byz.pdf)
- [Dwork, Lynch, Stockmeyer — Consensus in the Presence of Partial Synchrony (1988)](https://groups.csail.mit.edu/tds/papers/Lynch/jacm88.pdf)
- [Two Generals' Problem — Wikipedia](https://en.wikipedia.org/wiki/Two_Generals'_Problem)
- [Byzantine Agreement — Yale CS](https://www.cs.yale.edu/homes/aspnes/pinewiki/ByzantineAgreement.html)
- [Byzantine fault — Wikipedia](https://en.wikipedia.org/wiki/Byzantine_fault)
