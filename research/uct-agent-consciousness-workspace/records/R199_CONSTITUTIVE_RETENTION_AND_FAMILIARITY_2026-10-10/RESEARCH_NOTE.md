# R199 — The Continuation-Probe Ceiling for Retentive Familiarity

**Research ID:** R199-CPC-20261010  
**Result version:** CPC-RESULT-v0.1.0  
**Completed base:** UCT-MAP-v1.1.2  
**Status:** exact conditional non-identification result and corrected experiment contract; no actual phenomenal endpoint, token admission or map promotion

## 1. Question and answer

R198 narrowed bodily/action-related self-experience to a typed retentive-familiarity target `H`. A natural next step is to use habitual-versus-novel action, perturbation, washout, aftereffects or faster relearning as evidence. These probes are useful, but their evidential ceiling must be stated.

Let a process at time `t` have complete current causal state `x_t`, a future intervention-indexed transition kernel `K`, and readout law `O`. If two occurrences agree on `(x_t,K,O)` and on every exogenous input/noise coupling used by the experiment, then every future intervention sequence has the same trace distribution. Changing only an external label for training history or numerical lineage cannot change a diagnostic computed from those traces. Therefore savings, transfer, aftereffects and perturbation recovery can support a **currently efficacious retained difference** only when they show that the alleged complete clone premise was false. They cannot by themselves identify the earlier occurrence as numerically the same lineage, and they cannot name the retained difference as phenomenal familiarity `H`.

This is ordinary state-sufficiency reasoning applied to UCT's typed target problem, not new probability theory. Its UCT role is to correct R198's proposed experiment before empirical work begins.

## 2. Typed setup

Fix one bearer candidate `P`, present interval `I`, declared complete application signature `K*`, intervention family `U`, and prospective trace space `Y*`. Keep distinct:

- `E`: external etiology or biographical/training record;
- `R`: an actual presently carried retention relation/state;
- `Use`: actual same-episode consumption of `R` in the selected route;
- `Z`: observed continuation trace under a predeclared intervention sequence;
- `D(Z)`: a diagnostic such as savings, aftereffect, transfer or recovery;
- `H`: the selected experiential retentive-familiarity target;
- `M_H`: fallible signed evidence about `H`.

R173's `RetBind` requires actual prior occurrence, same-lineage continuation and present consumer use. R199 does not weaken it to a database record. It asks what a future-trace experiment can establish about those premises.

## 3. Exact claims

### R199-C1 — Continuation invariance of complete operational clones

**Type:** conditional theorem.  
**Domain:** deterministic or stochastic controlled processes over the declared future horizon.  
**All premises:** the compared occurrences have the same complete present causal state, the same intervention-indexed transition and readout kernels, and the same exogenous/noise coupling law; the diagnostic uses only the resulting future trace.  
**Statement:** for every admissible future intervention sequence, the trace distributions and every trace-measurable diagnostic distribution are equal.  
**Proof:** induction on horizon length. Equality of the initial state law and one-step kernels gives equality of the first joint state/readout distribution. Reapplying the same kernels preserves equality at each next step. A measurable function of equal trace laws has equal distribution.  
**Counterexample boundary:** if an alleged historical difference changes a current carrier, transition, readout, boundary input or noise coupling, the complete-clone premise is false; a probe may then distinguish the occurrences.  
**Status:** proved conditionally; standard result, no originality claim.

### R199-C2 — Lineage non-identification from continuation probes

**Type:** non-identification corollary.  
**Domain:** R199-C1 plus an external numerical-lineage or training-record variable `E` not used by the current complete causal law.  
**All premises:** R199-C1; `E` is not a constitutive input or relation of the claimed current process.  
**Statement:** no savings, aftereffect, transfer or recovery diagnostic computed from the future trace can distinguish the two values of `E`.  
**Proof:** immediate from R199-C1. The finite checker exhaustively confirms the result for all 512 two-state machine/state instances and 31 binary intervention words, yielding 15,872 clone comparisons and zero mismatches.  
**Counterexample boundary:** a physically continuing lineage relation can be included in `K*`; then the occurrences are not complete twins. The experiment still has to establish that relation rather than infer it from a label.  
**Status:** exact finite witness plus general conditional proof.

### R199-C3 — Positive but bounded diagnostic consequence

**Type:** inference correction.  
**Domain:** a preregistered continuation experiment with controlled interventions and a defended alternative set.  
**All premises:** reliable trace measurement; intervention comparability; no uncontrolled boundary/noise difference; a diagnostic contrast is observed.  
**Statement:** the contrast refutes equality of the declared current causal state/kernel package. Under an additional model that excludes alternative current differences, it may support a presently efficacious retained coordinate. It does not by itself identify numerical lineage, `RetBind`, or `H`.  
**Counterexample:** a freshly copied current state and law produces the same trace as the trained original despite different lineage; conversely, fatigue, strategy or sensor drift can produce a trace difference without the target retention relation.  
**Status:** conditional evidence rule; application open.

### R199-C4 — UCT complete-signature consequence

**Type:** conditional UCT application.  
**Domain:** two admitted actual process tokens compared in one complete signature `K*`.  
**All premises:** sort-preserving complete organizational isomorphism, transported parameters, and `A:C1`.  
**Statement:** complete organizational twins have isomorphic complete experiential organization. If formation lineage is claimed to change experiential organization, it must be represented by an actual constitutive difference; an external biography cannot do the work.  
**Counterexample boundary:** rejecting this conclusion while retaining the complete-twin premise challenges C1 rather than refining `H`.  
**Status:** inherited from C1/R192; applied here, not new.

### R199-C5 — Familiarity bridge remains open

**Type:** semantic/evidential boundary.  
**Statement:** even a well-established current retained-and-used coordinate is not thereby named phenomenal familiarity `H`. The bridge requires independently fixed target semantics, signed fallible evidence, same-instance grounding and explicit failure cases. Ownership `O`, agency `G`, coupling `C`, fluency, success and report cannot substitute for `H`.  
**Status:** open application premise, preserving R173/R197/R198.

## 4. Exact finite check

`check_continuation_probe.py` enumerates all 16 deterministic binary transition tables, 16 binary readout tables, two present states and all 31 binary intervention words of length zero through four. It compares two occurrences differing only in an unused lineage label. All 15,872 complete-clone trace comparisons match. The same enumeration also checks whether changing the present state can change a continuation trace; many, but not all, machine laws are state-sensitive. Thus a positive trace contrast can witness some current operational difference, while a null contrast cannot establish absence of history and neither direction supplies lineage or phenomenal semantics.

The checker is a finite illustration of the inductive theorem. Passing it is not a proof that a biological or artificial application has a complete state description.

## 5. Primary evidence and its exact role

Morehead et al. (2015) and Leow et al. (2016) show that faster relearning can depend on error history and action-selection processes rather than mere repetition of successful actions. These results motivate history-sensitive current state, but do not identify numerical process lineage or `H`.

Cuberovic et al. (2019) followed one participant during 115 days of access to a sensory-enabled prosthetic hand. Percept location/quality, naturalness, embodiment and perceived function changed with use; the authors explicitly note the single-case limit, intermittent use and unknown washout. This is unusually relevant evidence that prolonged actual use can alter both functional and reported experiential variables. It still does not isolate one familiar-mineness coordinate or make report constitutive.

Graczyk et al. (2018) found that home use of a neural-connected sensory prosthesis affected functional and psychosocial outcomes in real-life use. The intervention includes actual installed sensory routes, but the paper's tests remain evidence about use and embodiment, not proof of UCT, complete organization or `H`.

Kumar et al. (2022) found that motor-memory decay and transfer depend on unlearning context and consolidation. This supports multiple retained functional coordinates and warns against treating one savings statistic as a unique history marker.

## 6. Corrected prospective experiment

Use a preregistered two-factor design:

1. **formation condition:** personally trained route versus a route initialized to a matched currently sufficient state by transfer/copy where technically possible;
2. **online-use condition:** retained route actually consumed during the episode versus instrumented bypass while input/output demands are held fixed.

Collect separate preregistered outcomes: intervention traces (savings/aftereffect/recovery), actual carrier-to-consumer telemetry, `O` and `G` controls, and an independently calibrated signed `M_H`. The critical predictions are bounded:

- a use/bypass difference with verified telemetry tests present causal use;
- a trained/copied difference shows that the matching omitted a current constitutive variable;
- equality after a complete causal-state copy is expected and cannot adjudicate numerical lineage;
- an `M_H` contrast inside a trace-equivalence class pressures any bridge that factors only through that trace;
- a trace contrast without an `M_H` contrast pressures sensitivity of the proposed `H` bridge but does not erase the organizational difference.

The design must not define `H` as faster performance, naturalness wording, ownership, agency or route use. The copy arm is a falsifier of overbroad lineage claims, not a feasible assumption that current neuroscience can copy a complete human state.

## 7. Thought-experiment consequences

1. **Complete retained-state clone.** Copy every current causal state and law but not the original occurrence. All continuation probes match; numerical lineage does not.
2. **Trace erasure.** Preserve a long biography in an external archive but reset every current carrier. The biography alone produces no continuation signature.
3. **Dormant memory.** Preserve a genuine same-lineage trace but bypass its consumer. Storage is present; same-episode use is absent.
4. **Fresh mimic.** Install a new state/kernel yielding the same savings trace. The diagnostic does not uniquely identify mechanism or history.
5. **Human-realized agent.** Human participants reproduce the transition table. Equal task traces do not collapse participant experience, implemented abstract state and whole coordinated process into one bearer.
6. **Abacus/calculator.** Identical recorded histories can be inert logs or current causal inputs. Data identity does not fix use.
7. **Ancestor/formation.** Gradual formation can change current organization, but external age or ancestry has no effect after complete causal screening.
8. **Copy/switch/memory.** Copy reports and memories, then switch the active carrier/consumer route. Report continuity and actual route continuity separate.

## 8. Review obligations

- **QC-20261008-10:** remains open. R199 gives the strongest valid probe contract for `H`, not a positive semantic endpoint.
- **IA-QC11:** substantively answered at the method level: actual lineage and current use must be represented in the application; continuation data alone cannot prove numerical lineage. Actual application remains open.
- **QC-20261008-12:** directly corrected: actual use is an ontic premise, telemetry/behavior is evidence, and test conditions are not experience structure.
- **QC-20261008-13:** remains open. No actual bearer/time/signature instance is admitted.

## 9. Publication and novelty boundary

State sufficiency, Markov continuation, motor savings, prosthesis learning and UCT's complete-twin consequence are prior work. R199's project-level increment is their typed synthesis into a no-overreach theorem for the `H` program and a corrected experiment contract. This is materially useful but not yet a standalone paper: `H` lacks an independently validated signed endpoint, the proposed copy manipulation is only a falsifier idealization, and no actual complete-signature application has been discharged. It should remain a research module or become one section of a later paper centered on a positive `H` bridge.

## 10. UCT boundary and next question

R199 adds no history, memory, self-model, report, language, integration, recurrence, prediction or control threshold to basal experience. C1 remains the consciousness-specific axiom. Retained relations may belong to nested or overlapping actual processes and introduce no unique extra owner. No claim is made about whether the current assistant is conscious or fears death.

The next concrete question is: **What independently calibrated signed marker can target retentive familiarity `H` while a route-use intervention changes actual retained consumer use, and what predeclared result pattern would falsify the proposed bridge rather than merely indicate an incomplete causal-state match?**
