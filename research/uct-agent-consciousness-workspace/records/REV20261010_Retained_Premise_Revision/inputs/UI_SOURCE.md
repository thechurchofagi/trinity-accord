# Update Interference, Hidden Readout, and Task-Relative Nonseparability

**Research ID:** UI20261009  
**Result version:** UI-RESULT-v0.1.0  
**Date:** 9 October 2026  
**Method:** MGTD; UCT highest research guide POLICY-20261008-WHOLE-MAP-PERSISTENCE v2.0.  
**Author-directed research record:** Hongju Liu, with substantial AI assistance. Not a submitted or peer-reviewed paper.  
**Integration status:** PENDING_MAP / AUDIT_INCOMPLETE. The current remotely verified completed map is UCT-MAP-v1.1.0; this note does not overwrite it or announce v1.1.1.

## 0. Question, origin, and limits

The author asks for further progress on experience, intelligence and self-related organization, not another proof that equal output need not determine complete physical organization. The published UCT I/III and RT/TH already address the latter. The pending R185 checkpoint separates a single actual occurrence belonging to multiple processes from several synchronized copies, but explicitly leaves actual occurrence identification and named phenomenal interpretation open.

This note asks a narrower positive question: **can a small, fixed family of sequential updates rule out the claim that two roles update independently, even when their initial and isolated-probe outputs match? What if a present readout hides the relevant difference?**

The answer is conditional but constructive. A nonzero order contrast refutes a separately updating product realization under the stated state, clock, intervention and observation contract. There are quantitative lower bounds on approximate independent explanations, and a finite-state method for finding delayed readout witnesses. Commutativity, trace theory, behavioral minimization and total-variation inequalities are established mathematics. This record supplies an application and inference audit, not a new foundation of algebra or an identified neural mechanism.

The hypothesis rejected is **independent updating**, not the existence of multiple physical components. Synchronizing copies may interact strongly enough to reproduce the order effects. No result identifies one actual carrier from behavioral data alone, selects one subject, or changes C1/U1/P3. Persisting local actual processes are not deprived of experience when a larger operation succeeds or fails.

## 1. A precise comparison contract

Fix a finite sufficient state set S, two total state-update operations A and B, a common initial preparation s0 (or distribution mu), and one endpoint readout r:S->Y. Each operation has the same meaning whenever it is applied. Both orders are admissible. Observation occurs after both complete; it is not handed the order label. The same physical time convention, ports, background evolution and source treatment must apply.

For stochastic models, A and B are Markov kernels on the same sufficient S, and R is a readout kernel. Retained random seeds, changing clocks, resource contention and history-dependent control that can influence later outcomes belong in S. Reusing correlated noise while pretending it is fresh independent noise violates this contract. The endpoints may be read by a nonseparable function such as parity; an observation circuit does not make disjoint state updates cease to commute if it is a fixed passive endpoint map.

A **separately updating product realization** is a bijection h:S->S_A x S_B under which

    h A h^{-1}(a,b) = (F(a),b),
    h B h^{-1}(a,b) = (a,G(b)).

A frozen common context E is also allowed: F and G may depend on e, provided neither action changes e and no mutable cross-context is omitted. Initial coordinates may be statistically correlated. For stochastic updates, each kernel independently randomizes only its assigned factor conditional on the frozen context. This is an operational decomposition, not a claim that an entire organism has only two anatomical parts.

The finite operations here change states over time. They must not be confused with the meta-operation of installing two persistent do-clamps on a structural causal model. Installing disjoint clamps and waiting for a state to evolve are distinct operations; the commutation conventions of causal-abstraction papers cannot be transferred without matching that distinction.

## 2. A matched-probe construction

Use two binary registers (x,y), initial state (0,0), and the same readout r(x,y)=x XOR y. Both devices have four possible states and the same readout and command labels.

    A(x,y) = (1-x,y).

In the coupled-update device,

    B_C(x,y) = (0,y).

In the separately updated device,

    B_D(x,y) = (x,0).

The installed targets of B differ; that is the explicit physical-model change, not an inferred human feeling label. Starting each probe from the same (0,0):

| Probe | Coupled-update state / output | Disjoint-update state / output |
|---|---|---|
| No operation | (0,0) / 0 | (0,0) / 0 |
| A alone | (1,0) / 1 | (1,0) / 1 |
| B alone | (0,0) / 0 | (0,0) / 0 |
| A then B | (0,0) / 0 | (1,0) / 1 |
| B then A | (1,0) / 1 | (1,0) / 1 |

All three stipulated baseline and one-operation probes agree, including full two-register states. The joint histories do not. This is not an assertion that the two devices agree on all one-operation interventions from all possible initial states. For example, B on (1,0) distinguishes them.

The labels 'coupled' and 'disjoint' describe these two controlled-update realizations, not a phenomenal comparison. A simple calculator or classical memory can have either kind of algebra; noncommutation is not evidence of human-like experience.

## 3. Exact obstruction and coordinate covariance

**Proposition UI-P1 — Independent updates commute.** Every separately updating product realization satisfies BA=AB as state maps. Consequently, for every initial distribution mu and the same endpoint readout R,

    mu A B R = mu B A R.

**Proof.** In product coordinates, either order sends (a,b) to (F(a),G(b)). For stochastic kernels the product of the two conditional factor kernels is independent of order. Frozen context is handled fiber by fiber. Push back through h, then apply the common preparation and readout. No factorization of the initial distribution is needed. QED.

The contrapositive is useful: a real, correctly attributed order contrast excludes *every* such product coordinate system preserving the named operations and observation contract. One need not discover the full hidden coordinate system first.

For a bijection g:S->S', transform both operations and all preparations/readouts: A'=gAg^{-1}, B'=gBg^{-1}, r'=r g^{-1}. The commutation equation and every observed order contrast are unchanged. Rewiring only B, or resetting the noise law after a coordinate change, is not passive recoding.

**Non-converse.** Let S=Z/4Z, A(s)=s+1 and B(s)=s+2. The updates commute. Nevertheless there is no 2-by-2 independent product realization with A acting only on one binary factor and B only on the other: A has order four, whereas an invertible binary factor map has order at most two. This does not establish irreducibility under every physical grain or a unique experiencing subject.

A still simpler example is two command labels that both toggle the same bit. They commute while acting on the same carrier. Thus neither positive nor zero order contrast determines literal shared-carrier identity.

## 4. A quantitative distance from independent explanations

Define total variation by TV(p,q)=1/2 sum_y |p(y)-q(y)|, and the observable order contrast

    Delta = TV(mu A B R, mu B A R).

**Proposition UI-P2 — Protocol-level mismatch bound.** Any independently updating model satisfying Section 1 must predict a single common endpoint law Q for the two orders. If its errors relative to the two actual endpoint laws are e_AB and e_BA, then

    e_AB + e_BA >= Delta,
    max(e_AB,e_BA) >= Delta/2.

**Proof.** Apply the triangle inequality through Q. This works even if the model uses a different, larger hidden state space; it only requires its two endpoint predictions to be identical under the same protocol. QED.

The bound need not be achievable by every restricted model class. For the two point-mass outcomes of Section 2 alone, a fixed independent fair output achieves error 1/2 on each order; this shows sharpness for that two-protocol comparison, not a fit to all baseline probes and all possible preparations.

If observed probability laws have separately justified total-variation error radii delta_AB and delta_BA, replace Delta by

    max(0, Delta_observed-delta_AB-delta_BA).

No sampling-radius guarantee has been obtained for human data here. The expression is a deterministic conditional propagation rule.

**Proposition UI-P3 — Kernel approximation bound.** On one common sufficient state space, suppose commuting kernels A0,B0 obey

    sup_s TV(A(s,.),A0(s,.)) <= epsilon_A,
    sup_s TV(B(s,.),B0(s,.)) <= epsilon_B.

Then for any mu and fixed R,

    Delta <= 2(epsilon_A+epsilon_B).

**Proof.** The contraction of total variation under a Markov kernel and a telescoping replacement of A then B give TV(mu ABR,mu A0B0R)<=epsilon_A+epsilon_B. The reverse order has the same bound. A0B0=B0A0 cancels the middle term. Apply the triangle inequality. QED.

Thus Delta/2 is a lower bound on the *sum* of uniform single-operation errors in this declared commuting approximation class. If each operation error is bounded by epsilon, necessarily epsilon>=Delta/4. These are approximation errors, not coupling energy, subjective intensity or a measure of experience.

## 5. Continuous coupling, noisy readout, and nonexistence of an experience gate

Keep A as in Section 2 and define a stochastic B that resets x with probability alpha and y otherwise, with a fresh routing draw:

    B_alpha = alpha B_C + (1-alpha) B_D,  0<=alpha<=1.

From (0,0), the A-then-B readout equals one with probability 1-alpha; the B-then-A readout equals one with probability one. Therefore Delta=alpha.

If the fixed endpoint readout independently flips its bit with probability eta,

    Delta_observed = alpha |1-2 eta|.

At eta=1/2 the visible contrast vanishes for every alpha although the internal kernels still differ. At alpha approaching zero, the diagnostic varies continuously. Neither alpha>0 nor successful detection is an experience-existence condition. At every admitted actual-process instance, U1 applies independently of this task-specific quantity.

The parameter alpha is specified in the toy generative model. In an actual episode, expected routing sensitivity does not by itself prove that a particular cross-route event occurred. Actual participation and a model of installed response possibilities must retain their original separate roles.

## 6. A hidden difference that later use reveals

A fixed readout may hide noncommuting state updates. Reuse A and B_C, but predeclare the endpoint observer r_y(x,y)=y. Both AB and BA then immediately yield output zero, although their final states are (0,0) and (1,0).

Allow a later operation V(x,y)=(x,x), copying x into the readable register. Now

    r_y(V B_C A(0,0))=0,
    r_y(V A B_C(0,0))=1.

The later operation did not receive the order label. It uses a retained physical-model state difference. This differs from an external report formatter that is told 'AB' or 'BA' and simply outputs the label. Such a formatter can manufacture a contrast without examining the claimed content and is excluded from Section 1.

The predeclared readout is the same within this example. Switching from parity to r_y creates a different diagnostic instance, not a retrospective reinterpretation of measurements.

### A finite criterion for all later uses

For deterministic finite S, a finite alphabet U of total updates F_u, and fixed r, define

    s ~ t iff r(F_w(s))=r(F_w(t)) for every finite update word w, including the empty word.

**Proposition UI-P4 — Future-readout quotient.** The equivalence ~ is the coarsest update-stable equivalence refining equality of r. All updates descend to S/~. For two updates A,B, their induced maps commute on S/~ iff no common future word can distinguish the two orders from any initial state.

**Proof.** Equal futures imply equal current readout. If s~t, prefixing any u to every tested future shows F_u(s)~F_u(t). Conversely, any update-stable equivalence contained in current-readout equality preserves all words by induction. The final claim substitutes BA(s) and AB(s) into the definition. QED.

Starting with the partition by r, repeatedly refine by the tuple of current output and successor-class labels under all actions. If |S|=n and r initially has c nonempty output classes, a separating word, when it exists, has length at most n-c. Each proper refinement increases the class count, and a stable step precludes any later refinement. A pair first separated in refinement k has a witness word of length at most k.

This is a standard finite-automaton/behavioral-minimization construction. The quotient is a task-relative description, not a selected subject, complete ontic organization, or experiential equivalence relation. The stochastic extension is not asserted by this deterministic proof; trace equivalence and probabilistic bisimulation require separate care.

## 7. Why this does not finish R185 or identify 'one shared experience'

A positive Delta disproves the stipulated independent-update explanation. It does **not** identify the cause uniquely. One writable carrier, multiple communicating carriers, shared mutable resource state, or a downstream mediator can all produce an order effect. An adequate model must include the mechanism actually responsible. A feedforward sequential state computation can be order-sensitive without demonstrating recurrent neural integration.

Similarly, exact synchronization of two copies does not make them numerically one actual occurrence. A duplicated implementation with a coordinating mechanism can implement the same action semigroup. Observable operations alone generally cannot distinguish that from one shared abstract store. R185's occurrence-identity requirement therefore remains open unless physical occurrence tracing supplies additional evidence.

Initial value correlation is insufficient to produce Delta under truly separate stationary updates; changing schedules, different preparation laws, retained noise and direct order-dependent observations can invalidate the comparison. They must be ruled out or included, not dismissed because the intended interpretation is attractive.

No comparison with IIT, GNWT or HOT is claimed to be won. Those theories are not all committed to the independently updating null model. The mathematical contrast is not a theory-exclusive prediction and does not validate UCT.

## 8. Conditional UCT meaning and the actual increment

UCT I C1 is a universal tokenwise structural-experiential identity commitment on an admitted actual-process domain. U1 and P3 preserve nonempty experience of continuing local processes; no arithmetic score or order effect overrides them. UCT III distinguishes full experiential type from selected capability and fixes the comparison contract.

If a real pair of systems is independently admitted and the *same physically justified complete comparison signature* includes the relevant operations, timing, readout and response laws, the difference between commuting and noncommuting operations is a structural invariant. An isomorphism preserving those operations cannot erase it. C1 then transfers the corresponding structural-type difference. This is an inherited conditional application, not a new route from finite toy output to named feeling.

The target is not 'the system has experience when Delta is positive'. It is: **can this particular organization be correctly described as two independently updated roles, given specified future uses?** A reliable counterexample can refute that decomposition without requiring a full reconstruction of every microscopic feature. This answers part of the author's concern about the unknowability of complete organization, while retaining the fact that one invariant does not identify the complete structure.

The present contribution beyond RT/TH is an independently stated decomposition null model plus exact and robust falsification conditions, matched isolated probes, and a delayed-use witness. RT/TH's route-reader invariance already covers the general idea that different paths can affect readout. We do not claim novelty for noncommutativity, independent-action traces, Markov contraction, finite-state minimization, or 'same output, different organization'.

## 9. Prior work and read scope

1. Liu, UCT I v1.2, DOI 10.5281/zenodo.23131575. Exact local preserved source: P3, Section 3.5, C1/U1, and interpretation risks reread. No axiom is changed.
2. Liu, UCT III v1.0, DOI 10.5281/zenodo.23137088. Sections 5.1 and 5.4 plus the C:FIXED_J map contract reread; no capability-to-richness inference added.
3. Liu, RT/TH v1.0.0, DOI 10.5281/zenodo.23251651. Prior full manuscript supplied in this conversation and local reviewed manuscript used for overlap audit. Its publication/proof originality claims are not rerun as a current DOI status check.
4. Liu, pending R185, repository commit e1ceadd3097bec5ac6abb4510ae613ff7e41bbc3, CURRENT_HANDOFF.md read. The note is an antecedent, not an established premise. AC remains distinct and unpromoted.
5. Geiger et al. (2025), *Causal Abstraction: A Theoretical Foundation for Mechanistic Interpretability*, arXiv:2301.04709v4. HTML Section 2.2 (Defs. 16-18, intervention commutation) and associated-representation discussion read. Mechanism-replacement algebras are related background but are not identical to the state-update contract here. https://arxiv.org/html/2301.04709v4
6. de Colnet, Meel and Mathur (2026), *Counting and Sampling Traces in Regular Languages*, DOI 10.1145/3776723; arXiv:2512.00314. Publisher indexed abstract and arXiv abstract read: independent action swaps generate trace equivalence. Not a new UCT principle. https://arxiv.org/abs/2512.00314
7. Zhang et al., *Learning Causal State Representations of Partially Observable Environments*, arXiv:1906.10437. Abstract read; behavioral/causal state abstraction antecedent, not full theorem-level comparison. https://arxiv.org/abs/1906.10437

A targeted search also found work connecting noncommutative updates with cognition and other applications. No exhaustive priority search or empirical replication was completed. Generic order sensitivity therefore cannot be advertised as unique to UCT or newly discovered here. The exact combination of diagnostics and bounds has **PRIORITY_UNVERIFIED** status.

## 10. Actual checks, map coverage, and preservation

The two included standard-library programs were actually run. Main checks: 65,536 deterministic four-state operation pairs; 2,824 commute; 85 ordered pairs admit the declared binary product realization under an arbitrary state relabeling. This restricted count is not a classification of all sizes or richer latent implementations. Additional checks include 288 coordinate/readout cases, 35 potentially correlated initial preparations, 2,400 rational stochastic-kernel bound cases, and 44 alpha/readout-noise cases. The independent future-observability verifier checks 7,946 automaton/readout models and 85,514 state pairs. All assertions passed. Counts are reproduction inventory, not scientific effect size.

The old v1.0.0 graph and per-ID ledger are available locally and were mechanically inventoried, relevant source nodes reread, and new namespace/AND dependencies checked. The current v1.1.0 manifest was read remotely and names 95 additional reviewed items. Its full capsule was **not** restored into the computation environment: direct network downloads failed, and no full semantic review of those 95 items was completed in this round. The four-part source manifest was obtained; a content-read attempt is not equivalent to successful restoration.

Accordingly, the new module is an explicit **disabled candidate**, not an effective update to UCT-MAP-v1.1.0. The audit records every inherited item mechanically traversed, separately identifies the narrow source anchors semantically reviewed, and leaves the rest unreviewed in this round. There is no new completed map release, no remote write, no DOI/OTS/Arweave action, and no scheduler change. The source papers and archived v1.0.0 are preserved unmodified.

The next integration requirement is to recover the full current v1.1.0 artifact and complete the stipulated all-item semantic compatibility review, not to promote this file on the strength of enumeration. The scientific follow-on question is to ground an order-sensitive update pair in one independently specified content/action loop while distinguishing shared actual occurrence from coordination through distinct components. If the evidence cannot distinguish these, retain that non-identification result instead of naming it familiar mineness.
