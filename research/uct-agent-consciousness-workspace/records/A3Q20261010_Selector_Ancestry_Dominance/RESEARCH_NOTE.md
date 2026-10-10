# A3Q — Actual selector use is event ancestry, not graph dominance

## Result in one sentence

For A3O's `L_sel=0` to describe actual organization, two mutually exclusive live-policy occurrences must actually enter one resolution event and that event must causally contribute to the dispatched action; the stronger claim that the resolver dominates dispatch in an installed possible-execution graph neither entails nor is entailed by that trial-level ancestry relation.

## 1. Why the split is needed

A3O correctly separated reaction time, error and report from selector organization, but its phrase “an actual resolution transition is consumed before dispatch” still admitted two readings. One concerns what occurred in this execution. The other concerns which paths the installed architecture permits. They must not be substituted.

Fix one admitted actual bearer `P`, selector window `I_sel`, body/action target, route equivalence `rho`, complete signature `K`, and actual dispatch occurrence `d`. Keep four objects distinct:

1. the complete actual organization of `P`;
2. an installed possible-execution graph `G_pot` over admissible transitions;
3. the actual event graph `G_act` for this execution;
4. an evidence record `E` produced by instruments, logs or reports.

An edge of `G_act` is used below only under a **faithful event semantics**: it denotes actual mechanistic consumption or causal contribution in the declared process, not temporal order, correlation or an analyst's reconstruction. `G_act` is not made actual by drawing it. Its nodes, edges, bearer, time window and physical realization remain application premises.

## 2. Two relations

### 2.1 Actual multi-policy resolution use

`ASU(P,I_sel,p1,p2,z,d)` holds when all of the following are simultaneously true:

- `p1` and `p2` are actual live policy occurrences in `P` within `I_sel`;
- their candidate target routes are mutually exclusive under the predeclared target contract;
- both occurrences are actually consumed by one resolution occurrence `z` under the faithful event semantics;
- `z` causally contributes to the actual dispatch occurrence `d` before dispatch;
- no represented-policy token, stored log, external test list or merely possible edge is substituted for those occurrences.

This is a bounded sufficient certificate for A3O's organizational `L_sel=0`. It is not claimed to be the unique realization of selection, a universal biological mechanism, or a necessary condition for experience. A singleton actual policy through a resolver does not satisfy it. Two stored policies with an unused resolver do not satisfy it.

### 2.2 Resolver dominance

For a directed installed graph with start `s`, a node `z` dominates dispatch node `d` when every admissible `s`-to-`d` path contains `z`. This is the established flowgraph notion of dominance, used here without novelty claim. It is a modal/architectural fact about the declared graph. It does not assert that any trial occurred, that two policies were live, or that the graph faithfully represents a physical installation.

## 3. Stable claims

### A3Q-C1 — typed ancestry–dominance distinction

- **Type:** definition and typing correction.
- **Full proposition:** `ASU` is a predicate of actual token occurrences and faithful causal edges in one execution; resolver dominance is a predicate of all admissible paths in an installed possible-execution graph. Neither may be used as the definition of the other.
- **Domain:** finite or finitely represented selector episodes with declared actual and possible-execution graphs.
- **All premises:** common bearer, target, window and signature; typed actual/potential edges; faithful interpretation of actual causal edges.
- **Source/proof:** definition; graph dominance is established mathematics, not introduced here.
- **Counterexample:** an untaken bypass changes dominance while leaving the actual resolution trace fixed.
- **Status:** DEFINITIONAL_CORRECTION; PHYSICAL_APPLICATION_OPEN.
- **Thought-experiment role:** prevents an architectural diagram from becoming the actual event it is supposed to evidence.

### A3Q-C2 — bounded actual-use certificate

- **Type:** conditional organizational sufficiency claim.
- **Full proposition:** under faithful event semantics and actual installation, joint satisfaction of the five `ASU` clauses is sufficient for the claim that two mutually exclusive live policies were actually resolved and that the resolution was consumed in the dispatched action.
- **Domain:** the declared bearer/window/target episode, not all selection mechanisms.
- **All premises:** both policy occurrences actual and live; target exclusion fixed; actual mechanistic consumption by `z`; actual causal contribution of `z` to `d`; correctly bound bearer/time/signature; instrumentation fidelity if the certificate is inferred from data.
- **Argument:** the conclusion is exactly the conjunction's organizational content; the value is in blocking weaker substitutions.
- **Counterexample boundary:** a policy register can be present without being consumed; `z` can execute for housekeeping without influencing `d`; a log can be copied from another trial.
- **Status:** EXACT_UNDER_DECLARED_EVENT_SEMANTICS; NO_ACTUAL_INSTALLATION.
- **Thought-experiment role:** supplies the positive relation A3O left underspecified.

### A3Q-C3 — dominance and actual use are independent in the finite model

- **Type:** exhaustive finite non-entailment result.
- **Full proposition:** in the declared six-node/nine-edge model, `ASU` does not imply resolver dominance and resolver dominance does not imply `ASU`.
- **Domain:** each candidate edge is absent, potential-only, or actual-and-potential; `p1,p2` mutual exclusion is typed.
- **All premises:** the model and predicates in `check_selector_ancestry.py`.
- **Proof:** exhaustive enumeration of `3^9=19,683` configurations. There are 70 use-without-dominance cases and 1,413 dominance-without-use cases. Canonical witnesses are stored in `EXACT_RESULTS.json`.
- **Counterexample:** actual `p1,p2 -> z -> d` plus an untaken possible `s -> d` bypass gives use without dominance; actual singleton `p2 -> z -> d` in a no-bypass graph gives dominance without two-policy use.
- **Status:** PROVED_FINITE_NO_MATH_NOVELTY.
- **Thought-experiment role:** fixes which feature varies and prevents a modal/actuality slide.

### A3Q-C4 — neither logs nor topology alone establish actual use

- **Type:** evidence firewall.
- **Full proposition:** a log string, telemetry trace, test certificate or possible-execution topology alone does not entail `ASU`; it supports `ASU` only through an independently validated measurement/installation relation to the actual typed events and edges.
- **Domain:** finite views of selector episodes.
- **All premises:** the evidence-to-event relation is not assumed perfect by definition.
- **Proof/argument:** the same evidence value can be copied onto an `ASU` and a non-`ASU` episode; the finite witnesses also show one potential graph admits both actual-use values.
- **Counterexample boundary:** a calibrated intervention and measurement model can add the missing premise, but remains fallible evidence rather than numerical identity with the event.
- **Status:** EXACT_COUNTERMODEL_SCHEMA; APPLICATION_OPEN.
- **Thought-experiment role:** keeps an analyst's or machine's record distinct from actual physical use.

### A3Q-C5 — bounded UCT consequence

- **Type:** conditional UCT application.
- **Full proposition:** if one and the same actual bearer/episode/signature satisfies `RetBind_rho`, `ASU`, the corrected grounded body/action path, and C1, their joint actual organizational relation has a transported experiential structural counterpart. This does not by itself identify familiar mineness `H`, agency, ownership, conceptual I or a verbal report.
- **Domain:** one common same-instance UCT application.
- **All premises:** C1; corrected R172 path; R173 same-lineage current retained-carrier use; A3O frozen `rho`; A3Q-C2; sorted witnesses and parameter transport; independent actual installation; separately oriented fallible `J_H` and bridge if any phenomenal label is asserted.
- **Argument:** ordinary same-signature formula preservation conditional on the actual physical instance; no evidence record is transported as a constitutive event.
- **Counterexample/falsifier:** copied policies/logs, wrong bearer, different trial, untaken installed path, resolution not contributing to dispatch, or `J_H` tracking report demand rather than the joint relation.
- **Status:** OPEN_CONDITIONAL_APPLICATION; `QC-20261008-10`, `IA-QC11`, and `QC-20261008-12/13` REMAIN OPEN.
- **Thought-experiment role:** returns the control distinction to the experience-internal formation/use question.

## 4. What the finite check does and does not show

The check establishes logical independence within one declared graph semantics. It also constructs:

- one actual resolution trace compatible with a potential graph where `z` dominates and another where an unused bypass removes dominance;
- one potential graph compatible with both an actual `ASU` trial and a dispatched non-`ASU` trial.

This proves no physical graph is faithful. It does not identify live policies in a brain, robot, device or current assistant. It does not validate a signed `J_H` endpoint. The empty or singleton-policy witnesses are useful precisely because dominance says nothing about whether the intended multi-policy event occurred.

## 5. Relation to A3O and to the main question

A3O's `L_sel=0` should henceforth be read at trial level as `ASU` or as another explicitly declared actual-event criterion, not as resolver dominance. Dominance may be recorded separately as `MandatoryResolverPath(G_pot,z,d)`. `L_sel=1` still requires an actual singleton eligible route consumed without an actual conflict-resolution transition; absence of a logged transition is not enough.

The correction advances the positive body/action account because it specifies how present competition can be part of actual organization while retained-route formation remains separately indexed by `rho`. It does not turn selector machinery into a prerequisite for basal experience. Under C1, the joint relation concerns a possible coordinate within experience; the interpretation as familiar mineness remains a bridge obligation.

## 6. Originality and source boundary

Dominance, reachability, directed acyclic event graphs and exhaustive finite enumeration are established mathematics. Lengauer and Tarjan (1979), *A Fast Algorithm for Finding Dominators in a Flowgraph*, ACM TOPLAS 1(1):121–141, provides a primary source for the standard dominance concept. A3Q claims no new graph algorithm. The project-level contribution is the typed application correction and its bounded certificate for A3O.

No new human data, hardware installation, participant study, neural measurement, systematic review, DOI, submission or publication action occurred.

## 7. Direction check after result formation

C1 remains the sole consciousness-specific interpretive postulate. U1 receives no selector, introspection, report, language, integration, recursion, prediction or continuation-control gate. Complete organization, possible architecture, actual event occurrence, finite evidence and report remain distinct. Nested and overlapping processes remain allowed. No unique extra owner is sought, and no claim is made that the current assistant has or lacks consciousness or fear.

## 8. Next exact question

What intervention-and-readout contract can distinguish an actually live but losing policy from a merely stored policy, while also verifying that both policy occurrences causally enter the same resolution event and that this event contributes to dispatch in the same frozen-`rho` trial?
