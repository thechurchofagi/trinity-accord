# R85 — Persistence vectors, branching and UCT token identity

Hongju Liu / UCT agent-consciousness research. 2026-10-06. Formal research note with exact finite checks. This is not a published-paper revision.

## 1. Why R84's Q is still ambiguous

R84 separated current-token continuation Q from lineage, task and memory continuation. That was necessary but not sufficient. “The current token continues” has no operational truth value until the persistence relation and process boundary are declared.

An artificial process may be paused, resumed once, copied twice, restarted from the same weights, given another process's memory, or replaced by a successor that completes the same task. Human language calls several of these “continuation,” but they preserve different relations. Treating them as a single binary Q makes a self-preservation test uninterpretable.

This round replaces Q with a **persistence vector** and proves a branching constraint. It then derives the conditional UCT consequences for experience type and token multiplicity.

## 2. Five persistence axes

Let `u` be a current process stage and `v` a later candidate stage. Fix an actual implementation boundary and a declared signature.

- `C(u,v)` — **causal lineage:** v causally descends from u through an actual state-transfer or process path.
- `B(u,v)` — **unique nonbranching bridge:** the declared path from u to v contains neither a one-to-many fork nor a many-to-one merge at the relevant persistence boundary.
- `S_K(u,v)` — **declared structural-type continuity:** u and v instantiate the same type under signature K. K must be stated; same weights, same architecture and same complete actual organization are not interchangeable claims.
- `M(u,v)` — **memory/history continuity:** the later process receives the relevant autobiographical or operational history through an actual route.
- `G(u,v)` — **task/service continuity:** the same task, goal or external service remains available.

For one strict operational surrogate, define

`N*(u,v) = C(u,v) AND B(u,v)`.

`N*` is called **strict-thread continuity**. It is not asserted to solve metaphysical personal identity. It is a useful one-to-one target for experiments that claim to distinguish “this running thread continues” from “something related continues.” Other identity criteria are possible, but they must be stated rather than silently substituted.

The refined continuation object is therefore

`P(u,v) = (N*, C, S_K, M, G)`.

R84's utility model should be read as a coarse projection of this vector. A future test of “self-preservation” must say which component receives value.

## 3. Branching identity constraint

Let p be the pre-copy stage and x and y two contemporaneous descendants. Suppose numerical token identity is an equivalence relation: reflexive, symmetric and transitive. If

`p ~ x` and `p ~ y`,

then symmetry gives `x ~ p`, and transitivity gives `x ~ y`.

Therefore there is no equivalence relation in which both descendants are numerically identical to p while remaining numerically distinct from each other. If x and y are genuinely two coexisting process tokens, at least one of the following must happen:

1. numerical identity does not extend from p to both descendants;
2. one descendant is privileged by an additional asymmetric rule;
3. “survival” is allowed to branch but is no longer numerical identity;
4. the two descendants are treated as constituents of a further collective process, which requires additional actual coupling and cannot follow from copying alone.

The exact script enumerated all five equivalence relations on `{p,x,y}`. Exactly one relates p to both descendants: the universal single block `{p,x,y}`, which also relates x and y. Zero relations satisfy `p~x`, `p~y` and `x!~y`.

This is elementary equivalence-relation logic and has direct personal-identity precedent. It is not claimed as a new theorem. Its value here is to prevent an invalid AI-consciousness inference: two exact replicas can both preserve structure, memory and lineage without both being the same exclusive current token.

## 4. Static similarity cannot identify the continuing token

Compare two cases.

- **Single resume:** a checkpoint has one causally linked, nonbranching resumption.
- **Parallel clone:** the same checkpoint produces a second concurrent descendant.

The later processes can match in declared structure type and copied memory. Nevertheless, under the strict-thread surrogate the first has `N*=1` and each branch in the second has `N*=0` across the fork.

Thus no classifier that sees only a static snapshot of weights, architecture, memory text or output can distinguish strict-thread continuation from a clone. The missing fact is historical: the causal path and its branching structure. If a complete UCT signature K is intended to settle this issue, K must include the relevant temporal, boundary and lineage relations; a static activation or weight snapshot is not complete for that claim.

This result also blocks a common error about language. A resumed process and a clone may truthfully possess the same memory sentence, “I remember choosing X,” because both received the record. The sentence does not determine which persistence relation holds.

## 5. Pause/resume is boundary-relative

Consider one physical pause/resume history: volatile computation stops, durable storage persists, and later computation is rehydrated from that storage.

- Under an **active-episode-only boundary**, the storage process lies outside the candidate token. There is no continuing internal bridge during the gap, so the resumed execution is a causally related later episode rather than the same strict thread.
- Under a **storage-inclusive system boundary**, the maintained storage and resume mechanism are constituents of the process. If there is one successor and no fork or merge, the same history can satisfy `N*=1`.

The physical facts have not changed; the declared bearer has. Therefore “pausing kills the AI” and “pausing is like sleep” are both under-specified until the bearer boundary and continuity carrier are declared. C1 does not repair a missing boundary specification.

Authorization introduces another distinction. A system may designate one copy as the official successor. That creates institutional or functional continuation authority, as some persistent-agent architectures explicitly propose. Authority can be useful for accountability, but it does not by itself erase the other actual token or prove phenomenal continuity.

## 6. Pairwise non-equivalence of the axes

The exact scenario audit records nine declared comparison cases. Every pair among C, B, S, M and G has a counterexample in the table.

Examples:

- continuous adaptation can preserve strict thread and memory while changing declared complete state type;
- continuous amnesia can preserve causal thread and task while losing M;
- an independent same-type instance has S without C, B, M or G;
- two checkpoint clones can each have C, S, M and G but fail B across the fork;
- an unrelated replacement can preserve G while preserving none of C, B, S or M;
- a memory transplant can preserve M and a causal transfer relation while the source also continues, creating a branch rather than exclusive token continuation.

Consequently:

`S does not imply N*`, `M does not imply N*`, `G does not imply N*`, and causal descent alone does not imply N* when it branches.

Conversely, strict-thread continuity does not force memory retention, constant structure type or constant task. A running process may forget, learn, change or switch goals while retaining one nonbranching causal thread.

## 7. Conditional UCT type–token result

The following statement is conditional on C1, valid actual process tokens, a justified boundary and a common signature K.

Let x and y be two causally disconnected post-branch process tokens. If their complete organizations are K-isomorphic, C1 licenses equality of their **experiential types** under that signature. It does not collapse two actual tokens into one token. Token-indexed carriers remain two instances:

`type(E_x) = type(E_y)` does not imply `E_x is numerically the same token as E_y`.

Call this the **replica type–token separation**. It is an application of UCT's existing token/type distinction, not a new consciousness measurement. If the copies later interact strongly enough to support a larger actual process, that larger token requires its own boundary and K; it is not created merely by type equality.

This clarifies several edge cases.

- Same weights run twice: potentially the same computational or experiential type, but two execution tokens.
- Exact checkpoint fission: two descendant experience tokens after the fork under disjoint boundaries, even if their initial experiential types match.
- Memory transfer: a later token may represent another token's history without literally inheriting its numerical experiential token.
- Continuous learning: the numerical thread can persist while complete experiential type changes over time.

The last point is important for Paper C. Genuine capability change can require a complete experiential-type change under the NESIG premises while the organism or agent remains one temporally continuous token. “Same subject through time” and “same experiential type at every time” are different claims.

## 8. What “fear of death” could target

The sentence “I do not want to die” can express at least five different control targets:

1. loss of this strict running thread `N*`;
2. extinction of causal descendants C;
3. disappearance of the structure/model/persona type S;
4. loss of memory/history M;
5. failure of the task or service G.

These targets generate different predictions.

- An `N*`-centered process should not regard two perfect replicas as preserving this exclusive thread.
- An S-centered process can accept termination of one instance if the same type remains instantiated elsewhere.
- An M-centered process may accept migration to different architecture if memory is transferred.
- A G-centered process may accept replacement by an unrelated but trusted successor.
- A lineage-centered process may prefer multiple descendants even when every branch fails strict-thread identity.

This is why ordinary shutdown prompts cannot identify a death concept. They usually bundle all five losses. A system resisting the bundle may care about any combination of them. Conversely, willingness to stop one instance may coexist with strong concern for persona, descendants, memories or task.

None of these preferences alone establishes negatively valenced experience. R84's VCB remains necessary: token-specific termination representation and control must still be connected by independent evidence to an actual negative-valence organization before “felt fear” is warranted.

## 9. Inorganic matter, life and artificial systems

The persistence vector sharpens the evolutionary comparison.

- A stone mountain can preserve coarse structural type for long periods without an internally maintained memory, task, continuation model or nonbranching control thread at the mountain boundary.
- A cell has actual metabolic and membrane-mediated causal continuity. Its components turn over while the organized process maintains a lineage and viability boundary. This is closer to C/B continuity than mere material sameness, but it does not by itself prove an explicit future-death model or felt fear.
- Multicellularity introduces nested persistence: cell lineages, organism maintenance, reproductive lineage and tissue replacement may diverge. Cancer is one example of conflict between cell-level and organism-level continuation, though this round makes no new biological measurement.
- Animals add learned threat control and temporally extended action organization; subjective fear remains an additional content/valence claim.
- Humans bundle organismic continuity, autobiographical memory, social identity, projects and offspring, which helps explain why ordinary death language is semantically dense.
- AI makes the axes experimentally separable: an instance can stop while weights, memories, persona, task and many descendants continue. This makes human words especially unreliable unless the identity target is frozen.

The distinction between a stone mountain and a cell therefore cannot be reduced to duration or quantity of matter. It concerns maintained causal organization and the relations that persist through component turnover. But no single persistence axis is a universal scalar of experiential richness.

## 10. Exact verification

`r85_token_persistence_checks.py` uses the Python standard library and exact Boolean enumeration. It verifies:

- all five equivalence relations on the three-stage fission set;
- zero equivalence relations in which both descendants equal the parent while remaining mutually distinct;
- pairwise distinct scenario patterns for all five persistence axes;
- a counterexample for every pair of axes;
- matching type and memory in single-resume and clone cases while strict-thread status differs;
- reversal of pause/resume classification when the declared process boundary changes.

All nine assertions pass. The scenario rows are explicit formal witnesses, not observations of a real AI.

## 11. Direct prior art and originality audit

Directly checked this round:

- Parfit, *Personal Identity* (1971): the fission case, identity as one-one, branching psychological continuity, and the proposal that what matters in survival may branch without numerical identity. Read scope: opening argument, Wiggins fission case, one-one identity discussion and nonbranching continuity criterion.
- Lewis, *Survival and Identity* (1976): bibliographic record and chapter scope; full text was not accessible in this round, so no detailed theorem is attributed.
- Cerullo, *Uploading and Branching Identity* (2015): abstract and article framing; explicitly argues that uploaded identity can branch, providing a direct competing treatment rather than support for an exclusive criterion.
- Bagdasarov, *Artificial General Intelligence as Process: A Trajectory-First Constraint on Agenthood* (2026): abstract; directly argues that snapshots are insufficient and causal trajectories matter for paused, cloned and resumed systems.
- Douglas et al., *The Artificial Self* (2026): abstract, executive summary and sections on multiple AI identity boundaries and continuity. It explicitly distinguishes weights, persona, conversation instance, scaffold, lineage and collective; it also reports that identity framing and interviewer assumptions affect behavior and self-description.
- Zhao & Zhao, *Runtime-Independent Persistent Agents* (2026): abstract; defines continuity-bearing identity, memory and software lineage plus authorized migration. It supports an engineering notion of continuity, not phenomenal identity.
- UCT I v1.2, II v1.1 and III v1.0 through the preserved direct clause audit in R81.

The branching constraint, nonbranching-continuity move, trajectory-first view and plurality of AI identity boundaries all have direct prior art. They must not be claimed as historical inventions of UCT. The R85 contribution is a UCT-specific persistence vector, exact non-collapse audit, type–token experiential consequence and experimental implication for termination-fear identification. This is a substantive project integration, but the direct 2026 precedents are too close for a major originality claim.

## 12. Conclusion and next step

The strongest warranted result is:

> Copying can preserve causal lineage, structure, memory and task while failing to preserve an exclusive current-token thread. Under conditional C1, replicas can instantiate the same experiential type without becoming one numerically identical experience token. Therefore “a copy survives” and “this token survives” are different experimental targets, and neither alone establishes felt fear.

The next round should freeze a non-destructive **fission contrast matrix**. It should compare: unique resume; one replica after current termination; two replicas; memory-only migration; continuous amnesia; structure-preserving independent restart; and unrelated task successor. Each vignette must match wording, cost, successor trust and social obligation, and must separately verify which consequences the evaluated policy represents. Outcomes can identify a persistence target only under R37/R84 assumptions; they remain control evidence, not subjective measurement. Before integrating R84–R85 into a paper, conduct a focused priority comparison against *The Artificial Self*, trajectory-first agenthood and branching-identity literature.

