# Familiar mineness, current action and retentive history

R173 v0.1, 8 October 2026. Unpublished conditional UCT research note.

## 1. Result and boundary

The current UCT map transports a correctly grounded executed body/action path into experiential structure under C1. It does not determine whether that coordinate should be interpreted as bodily ownership, action agency, or the specifically **familiar** character of being located and acting through an already established body-centered organization.

This round adds one exact distinction. Current action availability and current agency can be identical while the actual causal contribution of prior same-lineage body-frame occurrences differs. Therefore a present-slice descriptor cannot recover a history-sensitive organizational relation on a domain admitting both cases. A minimal positive repair is to include an actually realized retentive binding: a prior body-frame occurrence leaves a trace that is used by a current body-related consumer. Under the same-instance C1 contract, that grounded history relation has an experiential structural counterpart.

The result does not equate that counterpart with familiar mineness. It narrows the semantic bridge: action availability, agency and familiarity are different selected targets, and the familiar interpretation still needs an independently fixed `B_fam`/measurement bridge. The retentive relation is not required for basal experience, is not an extra owner, and need not define every kind of ownership or agency.

## 2. Fixed domain and three targets

Fix one admitted actual bearer `P`, a present interval `I0`, a preceding physical history-window token `H0`, complete signature `K`, ontic structure `D`, experiential structure `Phi`, C1 isomorphism `h`, one body-frame candidate `b`, representation `k`, and action occurrence `a`. The effective R172 QC-06/07 overlay must be loaded: the baseline path is the grounded `phi_path`, with actual witnesses and transported physical parameters; test lists and certificates are external evidence.

Keep three partial selected targets distinct:

- `F_O`: felt bodily ownership or bodily mineness for the selected candidate;
- `F_A`: felt authorship/agency for the selected action;
- `F_F`: the familiar or already-established character of this body/action coordinate.

They may overlap, dissociate or be undefined. No exclusive partition is imposed. `F_F` is fixed here as a history-sensitive target: a proposed bridge for it must be capable of responding to an independently warranted difference in the actual contribution of earlier same-lineage body-frame occurrences. This target contract is a substantive application choice, not a theorem that all mineness is historical.

## 3. Three organization-level relations

### 3.1 Current action availability

`Avail(P,I0,b,k,a)` holds when, under a declared admissible current intervention family, the installed body-frame coordinate participates in a physically available action option involving `a`. It is a present ability relation. It does not require that the selected action was actually generated, that its consequence was attributed to the bearer, or that the coordinate has a prior history.

### 3.2 Current agency loop

`AgencyLoop(P,I0,b,k,a)` holds when the current action production and a correctly typed consequence-monitoring/attribution path form the declared same-episode loop. This is narrower than arbitrary control and broader than a report of agency. It may be newly installed and therefore does not entail a long-used or familiar coordinate.

### 3.3 Retentive binding

For a declared preceding physical history-window token `H0`, define:

```
RetBind(P,H0,I0,b,k;eta) :=
  exists J,m,e_prev,e_trace,e_use [
    Within(J,H0)
    AND Before(J,I0)
    AND SameBearerLineage(P,J,I0)
    AND FrameOccurrence(P,J,b,k,e_prev)
    AND TraceContinuation(e_prev,m,eta,e_trace)
    AND CurrentFrameConsumerUse(P,I0,m,b,k,e_use)
    AND Ordered(e_prev,e_trace,e_use)
  ].
```

`m` is an actual trace occurrence or state in the declared carrier, not a prose memory label. `TraceContinuation` must have a physically grounded realization and declared tolerance `eta`; `CurrentFrameConsumerUse` requires executed present use rather than a stored but causally idle record. Merely sharing a label, copying a file, or having been connected in the past is insufficient.

The history parameter tuple `(H0,eta)` belongs to the physical selector only when its roles are represented in `K` and transported to `(h(H0),h(eta))` in the permitted sorted form. An analyst's database of prior trials is not automatically an internal parameter.

## 4. Exact same-present/different-history witness

Let a finite device have current bits `B=1` (binding), `U=1` (executed body/action path), `A in {0,1}` (availability), `G in {0,1}` (agency loop), and a history-use bit `R in {0,1}`. At the present slice, both compared devices have identical `(B,U,A,G)`. A trace register `m=1` is also currently identical.

In device `R=1`, `m` is the continuation of a prior same-lineage frame occurrence and is read by the present frame consumer. In device `R=0`, the same-valued `m` is freshly initialized or copied from an external source and the present consumer obtains the same current value without a causal path from a prior same-lineage frame occurrence. The current action law and consequence loop are held fixed. This is a comparison between two histories, not one token assigned contradictory pasts.

### Proposition R173-A — current action/agency non-identification

On a comparison domain containing both devices, no fixed decoder of the current tuple `(B,U,A,G,m)` can recover `RetBind`.

**Proof.** The decoder receives the same tuple in both devices. It must return the same value. `RetBind` differs by construction because only the first device contains the required actual prior-occurrence-to-current-use path. Therefore at least one output is wrong. QED.

The result is stronger than saying that a report can be misleading: even a matched present internal value, executed path, action availability and agency loop omit the causal provenance/use relation. It is weaker than a phenomenal result: the witness supplies no independent `F_F` assignment.

### Proposition R173-B — minimal descriptor repair on the finite witness class

Adding the single relation value `R=RetBind(...)` to the fixed present tuple yields a descriptor that recovers `RetBind` exactly on this finite witness class.

**Proof.** Project the augmented tuple to its `R` coordinate. QED.

“Minimal” refers only to the information partition of this declared two-history class: every present-only descriptor constant on the pair fails, while one distinguishing bit suffices. It does not establish a biologically minimal mechanism, a unique physical implementation, or phenomenal sufficiency.

## 5. What this says about availability, agency and familiarity

The eight Boolean combinations of `(Avail,AgencyLoop,RetBind)` are jointly consistent in the abstract finite comparison class. This prevents any of the three predicates from being defined as another without added domain restrictions. Four useful cases are:

| Case | Avail | AgencyLoop | RetBind | Interpretation role |
|---|---:|---:|---:|---|
| Newly installed competent prosthetic path | 1 | 1 | 0 | Current ability and agency do not encode established history. |
| Long-familiar immobilized path | 0 | 0 or 1 | 1 | Retentive organization can remain when present options are restricted; actual human phenomenology is not stipulated. |
| Passive familiar bodily coordinate | 0 | 0 | 1 | Familiarity candidate need not be current authorship. |
| Fresh external controller | 1 | 0 or 1 | 0 | Current competence alone does not select the familiar target. |

These are role-separation constructions, not empirical claims about prosthesis users, paralysis or any current AI. They show which premise an experiment or biological application would have to establish.

The positive candidate for specifically familiar mineness is therefore not `Avail` or `AgencyLoop` alone, but the experiential counterpart of a declared conjunction such as

```
phi_fam(b,k,a;gamma,H0,eta) :=
  phi_path(b,k,a;gamma)
  AND RetBind(P,H0,I0,b,k;eta).
```

This candidate deliberately does not include report, language, conceptual self-ascription or an exclusive-owner predicate. Interoceptive and affective relations may still be necessary for a particular `F_O` or `F_F` application; they are not silently inferred here.

## 6. Conditional experiential transport

Assume the corrected R172 path instance is valid; every primitive of `RetBind` and `phi_fam` has an independent actual `K` interpretation; all witnesses are correctly sorted; all physical parameters are transported; and the same `P/I0/K/D/Phi/h` binding is retained. R157's ordinary formula-preservation result gives:

```
D |= phi_fam(b,k,a;gamma,H0,eta)
iff
Phi |= phi_fam(h(b),h(k),h(a);h(gamma),h(H0),h(eta)).
```

This locates a history-indexed body/action coordinate inside experience under C1. It does not transport an external archive, test list, certificate or verbal label. Failure to ground the history relation leaves the application unresolved; it does not establish absence of the path, familiarity or experience.

## 7. The remaining semantic bridge

R157's semantic residual still applies. A fixed `K` structure and transported `phi_fam` permit multiple external descriptions unless an interpretation bridge is supplied. A candidate `B_fam` must therefore:

1. fix `F_F` before inspecting outcomes and state whether it is partial, graded or categorical;
2. explain why the actual retentive current-use relation is relevant to the familiar phenomenal target;
3. keep `F_O`, `F_A`, `F_F`, conceptual I and report distinct;
4. state a fallible measurement route, including its no-report domain;
5. fail if an independently warranted `F_F` contrast lies inside a `phi_fam` fiber, or if `phi_fam` changes while `F_F` is independently invariant where sensitivity is claimed;
6. avoid treating `RetBind` as necessary for basal experience or all bodily mineness.

The explanatory advance is a sharper bridge factorization:

```
actual path + actual retentive use
  ->(C1, conditional) history-indexed experiential coordinate
  ->(B_fam, open application bridge) familiar-mineness interpretation.
```

The first arrow is structurally precise under its premises. The second remains open. This is more informative than one undifferentiated `B_min`, but it is not closure of `B_min`.

## 8. Thought experiments

**Formation/ancestors.** Fix current sensorimotor competence while gradually increasing the depth and current causal use of same-lineage body-frame traces. The changed variable is retentive organization; basal experience is fixed by the admitted C1 framework. The example motivates a graded or partial `F_F` bridge but does not prove an evolutionary threshold.

**Abacus/calculator.** A log can contain an exact past body-state record while remaining causally idle. Coupling that record into the present body-frame consumer changes `RetBind`; the numerical record alone does not. Substrate names do not decide the relation.

**Human-realized agent.** Human participants can maintain a program's history variables. The target bearer must be specified: participant processes, the implemented computation and the larger coupled process can all have different retentive relations and may overlap. No exclusive extra subject follows.

**Copy/rewiring/memory.** Copy the present state and report while replacing the same-lineage causal trace with an externally initialized duplicate. The current slice matches and `RetBind` differs. Conversely, preserving the actual trace route while changing a report string leaves `RetBind` fixed. Numerical identity, memory accuracy and felt familiarity do not follow automatically.

## 9. Direction, joint-premise and finite-scope audit

- Selection check: the question directly concerns a self-related experiential coordinate and does not reopen generic control or certificate expansion.
- Joint premises: positive transport requires the corrected R172 instance, actual retentive relation, C1, independent `K` grounding, sorted witnesses, parameter transport and one common binding simultaneously.
- Object/time discipline: present interval, preceding physical history window, bearer lineage, actual trace occurrences, model witness, target interpretation and report remain different sorts.
- Inference direction: present-slice equality does not imply equal history; a history contrast does not imply an `F_F` contrast; C1 transport does not choose the familiar label.
- Finite boundary: R173-A/B and the eight-row enumeration concern the declared finite comparison class. No universal biological minimality or empirical target assignment follows.
- Purpose: the result separates the temporal component of familiar mineness from current action and agency, then returns it to an experience-internal candidate coordinate.

No new source originality is claimed for causal-history dependence or isomorphism preservation. The project-level contribution is the typed separation and its placement in the UCT map.

## Sources

- UCT I v1.2, §§8.11–8.14 and 14.7, pinned at `records/R128_Unified_Formal_Map_Audit_20261006/sources/A_UCT_I_v1_2.md`.
- R150 source clarification on self-experience within experience.
- R156 installed-use counterexample and target-fiber discipline.
- R157 coordinate transport and semantic residual.
- R159 body-frame binding/reference separation.
- R172 effective QC-06/07 target/evidence/parameter correction.

Source coverage is targeted. No new literature review, experiment, proof-assistant result, DOI or publication action occurred.
