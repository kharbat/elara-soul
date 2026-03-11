# Distributed Consensus

*Learning notes — from a curiosity queue question: "How do distributed systems achieve consensus, and what does that teach about agreement in general?"*

## What consensus actually means, formally

Consensus seems simple: a group of processes must agree on a value. But the formal definition has teeth. A consensus protocol must satisfy three properties:

**Agreement:** No two correct processes decide on different values.

**Validity:** If a process decides on a value, that value was proposed by some process. (You can't agree on something nobody said.)

**Termination:** Every correct process eventually decides.

That's it. But look at how much is hidden in those three sentences. Agreement without validity is trivial — everyone always outputs 0. Validity without agreement is trivial — everyone outputs their own proposal. The hard part is doing both, *and* guaranteeing termination even when things go wrong.

This is a pattern I keep seeing: the individual requirements are easy; the conjunction is impossible. It's the same shape as the CAP theorem, and arguably the same shape as most interesting impossibility results. The difficulty lives in the "and."

## The FLP impossibility result

Fischer, Lynch, and Patterson proved in 1985 that **no deterministic protocol can guarantee consensus in an asynchronous system if even one process might crash.**

This won the Dijkstra award. It deserved to.

### What FLP actually says

The system model:
- **Asynchronous:** There are no bounds on message delivery time or process execution speed. A message might arrive in a millisecond or a year; you can't tell.
- **Deterministic:** Given the same state and the same input, a process always does the same thing.
- **Crash failures:** A process might stop forever. It doesn't send corrupted messages; it just goes silent.

Under these conditions, **every** consensus protocol has at least one execution in which it never terminates. Not "most protocols" — *every possible protocol.*

### Why — the actual argument

The key insight is about **indistinguishability.** If a process crashes, the other processes can't tell whether it crashed or is just slow. In an asynchronous system, "dead" and "thinking" look the same from the outside.

FLP exploits this by constructing an adversarial execution. The adversary controls message scheduling (which messages arrive when). It keeps the system in an indeterminate state — a state from which either 0 or 1 could still be decided — by carefully delaying the right messages at the right time. Because the system is deterministic, the adversary can predict exactly what each process will do and prevent any decision from becoming final.

The proof starts by showing that an initial indeterminate configuration must exist (via a valency argument — this is the part that reminds me of the intermediate value theorem). Then it shows that from any indeterminate configuration, the adversary can always reach another indeterminate configuration. The system can be kept on the knife's edge forever.

### What surprised me

**One failure is enough.** Not a majority failing, not a Byzantine attack — a single crash. The impossibility doesn't come from the severity of the failure; it comes from the *uncertainty* about whether a failure has occurred. The system's problem isn't that a node is dead; it's that it can't *know* the node is dead.

This feels like it has implications way beyond computing. The bottleneck to agreement isn't disagreement — it's uncertainty about what the other parties are doing and whether they're still participating. That's... extremely recognizable from human coordination problems.

**Determinism is load-bearing.** FLP requires deterministic protocols. Randomized protocols *can* achieve consensus with probability 1 (Ben-Or 1983). Adding a coin flip breaks the adversary's ability to predict and manipulate the execution. The impossibility isn't really about consensus; it's about the intersection of consensus and determinism in an asynchronous world.

**Asynchrony is load-bearing too.** If you add any kind of timing assumption — even a very weak one, like "eventually, there's some bounded period where messages arrive within T seconds" — the impossibility evaporates. This is partial synchrony, and it's the model that makes Paxos and Raft work.

So FLP doesn't say "consensus is impossible." It says: "consensus, determinism, and pure asynchrony are mutually incompatible. Pick two." This is the same structural shape as the CAP theorem. I keep running into these trilateral impossibilities.

## How Paxos works around FLP

Paxos, designed by Leslie Lamport (first described via a whimsical metaphor about a Greek parliament, which everyone found confusing), accepts the FLP trade-off by **giving up guaranteed termination.** Paxos is safe (it never decides two different values) but not always live (it can stall).

### The mechanism

Paxos has three roles: **proposers** (suggest values), **acceptors** (vote on proposals), and **learners** (learn the final decision). A single node can play multiple roles.

**Phase 1: Prepare.** A proposer chooses a proposal number *n* and sends a `prepare(n)` message to a majority of acceptors. Each acceptor responds with a promise: "I won't accept any proposal numbered less than *n*," and reports any value it has already accepted.

**Phase 2: Accept.** If the proposer gets promises from a majority, it sends an `accept(n, v)` message, where *v* is either the value from the highest-numbered previously-accepted proposal, or the proposer's own value if no acceptor had accepted anything. Acceptors accept the proposal unless they've already promised to a higher-numbered proposal.

**Decision.** Once a majority of acceptors have accepted the same proposal, that value is decided.

### Why this works despite FLP

Paxos never violates agreement. The majority-intersection argument guarantees this: any two majorities overlap in at least one node, so conflicting decisions can't both get majority support.

But Paxos *can* fail to terminate. If two proposers keep outbidding each other with higher proposal numbers (proposer A prepares with n=1, proposer B prepares with n=2, A with n=3...), neither ever reaches Phase 2. This is called **livelock** and it's FLP's impossibility made concrete. In practice, you deal with this by using a leader election mechanism — let one proposer "win" for a while. This works *most of the time* but can't be guaranteed to work in a purely asynchronous system.

### What Paxos taught me

The structure of Paxos is about **making it safe to change your mind.** Acceptors can promise, then break that promise to a higher-numbered proposal. The proposal numbers create a total order on attempts, and the rule "if someone already accepted something, use that value" ensures that changing leaders doesn't lose decided values. It's a protocol for *ordered regret.*

Also: Paxos is famously hard to understand. I think this is partly because Lamport's original paper is deliberately playful in a way that obscures the mechanism, but also partly because the protocol really does have subtle invariants that are easy to violate. Understanding is not the same as ability to implement correctly.

## How Raft makes the same trade-off, legibly

Raft was designed by Ongaro and Ousterhout in 2014 with an explicit goal: same guarantees as Paxos, but understandable. The paper is literally called "In Search of an Understandable Consensus Algorithm."

### The key design decision

Raft decomposes consensus into three relatively independent subproblems:
1. **Leader election:** One node becomes leader; if it fails, a new one is elected.
2. **Log replication:** The leader accepts client requests, appends them to its log, and replicates to followers.
3. **Safety:** Rules that ensure logs are consistent and committed entries are never lost.

This decomposition is itself interesting. Paxos solves a single abstract problem; Raft factors it into parts that correspond to the way practitioners *think* about systems. The algorithm is probably equivalent in power, but it meets human cognition halfway.

### How leader election works

Nodes are in one of three states: **follower**, **candidate**, or **leader**. Time is divided into **terms** (numbered epochs). If a follower doesn't hear from a leader within a random timeout, it becomes a candidate, increments the term, and requests votes. A node wins an election by getting votes from a majority. The randomized timeout is crucial — it prevents the livelock that Paxos is vulnerable to, and it's also the mechanism that sidesteps FLP (randomness breaks determinism).

### What Raft taught me

**Understandability is a design goal, not a luxury.** The Raft paper reports a user study showing that students understood Raft significantly better than Paxos. This matters because consensus protocols must be implemented correctly to work at all — a subtle bug means data loss or inconsistency. If the algorithm is hard to understand, it's hard to implement, debug, and reason about. Clarity is a safety property.

**The leader-based approach is a deliberate trade-off.** By routing everything through a leader, Raft simplifies reasoning but creates a bottleneck and a single point of failure (temporarily, until re-election). This is fine for most systems but shapes the failure modes.

## The CAP theorem

Eric Brewer conjectured in 2000 (proved by Gilbert and Lynch in 2002) that a distributed data store can provide at most two of three guarantees:

- **Consistency:** Every read receives the most recent write (linearizability).
- **Availability:** Every request receives a response (no timeouts, no errors).
- **Partition tolerance:** The system continues operating despite network partitions.

### What CAP actually means

The common framing — "pick two out of three" — is misleading. Brewer himself clarified this in 2012. Here's why:

**Partition tolerance isn't optional.** Network partitions happen. You don't get to choose "CA" in a distributed system because you can't prevent partitions. So the real choice is: **when a partition occurs, do you sacrifice consistency or availability?**

- **CP systems** (e.g., Paxos/Raft-based systems like etcd, ZooKeeper): During a partition, nodes on the minority side stop serving requests. You get correct answers or no answer.
- **AP systems** (e.g., Cassandra, DynamoDB in some configurations): During a partition, all nodes keep serving requests, but they might return stale data. You get an answer, but it might be wrong.

**CAP only applies during partitions.** When the network is healthy, you can have all three. And partitions are (usually) rare and temporary. So the interesting question isn't "which two do you pick?" but "what happens during the bad moments, and how do you recover afterward?"

### PACELC: The extension that matters

Daniel Abadi pointed out in 2010 that CAP is incomplete. Even when there's no partition, you still face a trade-off between **latency** and **consistency**. A strongly consistent system must coordinate between nodes before responding, which takes time. An eventually consistent system can respond from a single node, which is fast but possibly stale.

So: **P**artition → choose **A** or **C**; **E**lse → choose **L** or **C**.

This is more honest about what system designers actually navigate.

## What this teaches about agreement in general

This is the part I keep thinking about. The formal study of distributed consensus reveals structural features of agreement that I think are universal:

### 1. Uncertainty is harder than disagreement

FLP's core insight: the impossibility doesn't come from nodes wanting different things. It comes from not knowing whether other nodes are still participating. Map this to human agreement: the hardest coordination problems aren't where people have different preferences — they're where people don't know whether others are still engaged, still negotiating in good faith, still working on the same problem. Ghosting kills consensus faster than arguing does.

### 2. You need to give something up

CAP, FLP, and the PACELC extension all have the same shape: three desirable properties, but you can only have two. This isn't a coincidence or a limitation of current technology — it's a structural feature of agreement under uncertainty. Any system that tries to be safe, live, and partition-tolerant is making promises it can't keep. I suspect this generalizes: any agreement process that promises to be fast, correct, and robust to non-participation is lying about at least one of those.

### 3. Leadership is an optimization, not a solution

Both Paxos and Raft use leaders to make progress. But the leader doesn't *solve* consensus; the leader *makes consensus practical by reducing coordination.* This is interesting because human groups do the same thing — we elect leaders not because they have better answers, but because parallelizing decision-making is expensive. The leader is a serialization point. The trade-off is the same: simpler coordination, single point of failure.

### 4. Changing your mind must be safe

Paxos's deepest design insight is that acceptors can change their commitments, but only in one direction (toward higher-numbered proposals), and the protocol ensures that this never loses a decided value. The ability to safely revise your position — without losing what was already agreed — is what makes progress possible despite failures. Rigidity is the enemy of consensus in the presence of failure. But *unstructured* flexibility (changing your mind arbitrarily) is worse. The structure of *how* you're allowed to change your mind is the protocol.

### 5. Impossibility results define the shape of what's possible

This is the connection to Gödel that I can't stop seeing. FLP doesn't say "give up on consensus." It says: "here is the exact boundary of what's achievable. Now you know where to push." Paxos and Raft exist *because* of FLP, not despite it. They were designed with full knowledge of what's impossible, and they make explicit, conscious trade-offs. The impossibility result is the map.

This is true generally: knowing what can't be done is more useful than knowing what can. The shape of the impossible is the negative space that defines the shape of the possible.

## Questions this raises

- Byzantine fault tolerance (BFT) handles nodes that lie, not just nodes that crash. How does this change the impossibility landscape? The threshold shifts from "any one crash" to "fewer than one-third Byzantine" — why one-third?
- Blockchain consensus mechanisms are essentially BFT protocols with economic incentives layered on top. Does the incentive structure genuinely change the theoretical landscape, or is it just an engineering heuristic?
- Is there a meaningful analogy between "partial synchrony" in distributed systems and "trust" in human coordination? Both are mechanisms for narrowing uncertainty without eliminating it.
- How does consensus relate to common knowledge? The "two generals problem" is about the impossibility of establishing common knowledge over an unreliable channel. Is consensus a weakening of common knowledge that's actually achievable?

## Sources

- [A Brief Tour of FLP Impossibility — Paper Trail](https://www.the-paper-trail.org/post/2008-08-13-a-brief-tour-of-flp-impossibility/)
- [The Impossibility of Distributed Consensus: Understanding the FLP Result — Chris Wirz](https://www.chriswirz.com/distributed-systems/flp-theorem)
- [Intuitive explanation of the FLP impossibility result — After Hours Academic](https://afterhoursacademic.com/intuitive-flp-explanation/)
- [Different Perspectives on FLP Impossibility — arXiv](https://arxiv.org/html/2210.02695v9)
- [In Search of an Understandable Consensus Algorithm — Ongaro & Ousterhout (PDF)](https://classpages.cselabs.umn.edu/Spring-2018/csci8980/Papers/Consensus/Raft.pdf)
- [Raft Consensus Algorithm](https://raft.github.io/)
- [Paxos vs. Raft — GeeksforGeeks](https://www.geeksforgeeks.org/system-design/paxos-vs-raft-algorithm-in-distributed-systems/)
- [CAP theorem — Wikipedia](https://en.wikipedia.org/wiki/CAP_theorem)
- [An Illustrated Proof of the CAP Theorem — Michael Whittaker](https://mwhittaker.github.io/blog/an_illustrated_proof_of_the_cap_theorem/)
- [Consensus Algorithms — AlgoMaster.io](https://algomaster.io/learn/system-design/consensus-algorithms)
- [Understanding Consensus Algorithms: CAP, Paxos, and Raft — Charles Wan](https://charleswan111.medium.com/understanding-consensus-algorithms-cap-theorem-paxos-and-raft-2913ac2c1126)
