# Higher-order intervention masking under bounded action sequences

**Research ID:** R186-HOM-20261009. **Result version:** HOM-v0.1.0. **Map candidate:** UCT-MAP-v1.1.1-R186-candidate.1. **State:** CONDITIONAL FINITE-STATE RESULT, PENDING_MAP; NOT a new phenomenal law.

## Question and inherited results

The previous UI result says that jointly observable noncommutation refutes a specified independent-update product model; absence of measured noncommutation does not establish independence. R185 and AC/IL remain pending. We ask: can *every* experiment of at most m operations from one reset state fail to detect coupling, while an m+1 operation experiment reveals it? The point is to stop promoting a short-horizon negative intervention test to actual organization factorization.

## Construction and theorem

For an integer m>=1, state (f_1,...,f_m,z) in {0,1}^{m+1}, initialized to all zeros. For i=1..m, command A_i sets f_i to 1, leaving the others and z unchanged. Command C flips z if and only if f_1=...=f_m=1, otherwise does nothing. Comparator machine N uses identical A_i, but C always does nothing. Readout may be the *full state* after each operation, not merely z.

**Theorem.** Every command sequence of length <= m starting from the reset state produces exactly the same full state trace in both machines. The length m+1 sequence A_1,...,A_m,C distinguishes them: in the coupled machine z=1, in comparator z=0. Reversing by doing C before all flag settings leaves z=0. The distinguishing length m+1 is minimal from this reset condition.

**Proof.** Before any occurrence of C within a sequence of length <=m, at most m-1 distinct A_i commands can have occurred. The conjunction needed to flip z cannot hold. The A_i operations agree between models. Induction on prefix length proves identical state traces; the constructed length m+1 witness activates all flags and then C. QED.

The theorem remains valid if the observer sees every flag and z continuously at operation boundaries, because all states are identical in the tested class. A test that explicitly presets all flags or changes the reset is outside the fixed contract and can distinguish C in one action. A system with unbounded internal variables or continuous-time perturbations is not characterized by this tiny automaton.

**Corollary.** For any chosen finite experimental action horizon H, there exist two finite causal transducers agreeing on *all* action histories of length <=H from a fixed reset and disagreeing at H+1. Hence finite-horizon non-detection alone cannot certify unconditional independent-update factorization or absence of longer-horizon organizational dependence. This is an adversarial identifiability limitation, not a general impossibility of learning an identifiable system under known state-size/reset/coverage bounds.

**Countercontrols.** (1) A single command C given an initial state with all flags already set separates the machines. (2) No claim applies under complete testing of all states/transitions with suitable known finite-state bounds. (3) Observing only the external report can miss *more* differences, but here all full state traces coincide at short horizons. (4) A_i alone or pairwise sequential tests cannot exclude conjunctive higher-order gating for m>=2; pairwise under arbitrary premade states is another contract. (5) Commutation itself is not equivalent to product factorization: mutually dependent commuting maps are possible.

## UCT interpretation (explicitly conditional)

This strengthens the *method of comparing organization* without proposing a new gate for the existence of experience. Under U1/P3, each admitted actual local process remains experience-bearing while it exists, regardless of performance. The machines differ in transition organization; a concrete physical realization, full constitutive signature, matched experiment/time/boundary and application of C1 are separate premises. The finite test does not identify what-it-is-like, unique subject, numerical experiential magnitude, or which real AI has experiences. The operational question suggested by the theorem is what target-relative *depth and state-reset coverage* is needed to exclude hidden interaction, not whether short behavioral agreement guarantees identity of experience.

## Prior art and priority boundary

Finite-state-machine checking-sequence methods and bounded sequence conformance testing have long examined horizons, distinguishing sequences and state-identification limits. See https://doi.org/10.1016/j.tcs.2010.01.030 and https://isa-afp.org/entries/FSM_Tests.html. Higher-order conjunction logic is elementary; neither the construction nor its logic is claimed as historically new. Narrow increment vs earlier UI: an arbitrary hidden-interaction depth construction that defeats ALL shorter full-state reset traces, not merely one short output comparison. No definitive consciousness prediction, no DOI/OTS/AR authorization.

## Executed evidence and mapping

`test.py` checks all words of length <=m for m=1..5, and 3,000 deterministic generated sequences per length for m=6..8. It checks the exact depth m+1 witness for every m=1..8; the general bound follows from proof, not finite tests. The initial exhaustive m<=8 attempt timed out; it is preserved in the work log instead of described as PASS. `review_map.py` inspects all 1,373 inherited item records structurally and classifies 625 as needing targeted semantics; it is NOT a completed fresh item-by-item semantic audit. No mutation of existing C1/U1/P3 or activation of R185/AC/IL or the earlier UI material.

## Next unsolved task

Study distinguishability given finite memory/state-budget bounds and intervenability contracts, and identify a physically supported, non-report circular discriminator for shared actual process participation. Re-run all 1,373 full semantic judgments plus delta interaction before authorizing UCT-MAP-v1.1.1 final release; record per-ID decisions and affected theorem rederivations. This is an explicit blocker, not a claim that saving 1,373 rows proves semantic review.
