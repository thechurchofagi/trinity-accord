# Transductive Lineage Route Contract

## 1. Correction to A4S

A4S correctly showed that independently established local links do not compose merely because adjacent values match. Its generic use of numerical `SameOcc`, however, is too strong if read as requiring one numerically identical occurrence on both sides of every physical interface. An ADC, synapse, relay, human read–write step or actuator driver normally consumes one occurrence and produces a distinct successor occurrence.

The required relation is therefore typed. Fix one declared actual bearer process `P`, interval `I`, complete signature `K`, physical boundary `B`, ports and order. For adjacent boundary occurrences `x,y`, define:

`BoundaryStitch(x,y) := Relay(x,y) OR exists f Transduce_f(x,y)`.

- `Relay(x,y)` means that the two port descriptions are physically grounded views of one actual occurrence that persists across the boundary. Equality of values, hashes, labels, memory addresses or software identifiers is not enough.
- `Transduce_f(x,y)` means that one actual conversion event `f` in the fixed instance consumes `x` and produces the numerically distinct successor `y`; its input/output incidence, order and materially relevant boundary influences belong to the declared physical history.

With A4S's local links,

`L_s(a,x_s), L_c(x_c,u_c), L_w(u_w,e)`, 

the repaired route is:

`ActualLineageRoute(a,e) := L_s AND BoundaryStitch(x_s,x_c) AND L_c AND BoundaryStitch(u_c,u_w) AND L_w`.

This is a route-existence condition, not a unique-owner or unique-source condition. Under P6, lineage may branch or merge. Exclusivity requires an additional, claim-specific premise and is not needed for basal experience.

## 2. Ontic relation versus finite evidence

`Transduce_f` is an ontic relation in the declared physical history. A finite certificate does not become that relation by definition. A scoped evidential warrant `E_lineage(x,y,f;V)` for finite view `V` requires all of:

1. actual support for the endpoint and conversion occurrences;
2. fixed bearer, interval, hardware/firmware version, ports, units, coordinates and clock/order convention;
3. a production–consumption incidence trace tying the recorded input event to the recorded conversion and output event;
4. a preregistered source intervention with a response in the transducer's declared discriminating equivalence classes;
5. a declared finite inventory of alternate writers, replayers, buffers and fan-in paths, with independent closure evidence relative to that inventory;
6. explicit branch/merge accounting rather than an assumed unique parent.

The package can warrant a finite-view lineage claim. It does not prove complete `K`, universal causal discovery, an exclusive subject, a phenomenal label or C1 itself. If only downstream values are visible while replay remains open, lineage is not identified.

## 3. Stable claims

### A4T-C1 — STRICT-IDENTITY-NOT-NECESSARY

- **Type:** CORRECTION / FINITE_COUNTEREXAMPLE.
- **Claim:** Numerical occurrence identity at every boundary is not necessary for one actual route when an actual transduction edge consumes the upstream occurrence and produces a distinct successor.
- **Domain:** one fixed `(P,I,K,B)` and the boundary-mode abstraction in `PROOF.md`.
- **Premises:** P6's separation of token identity and directed lineage; actual local links; an actual transduction edge.
- **Proof:** the ADC/transduction worlds have a directed stitched path and fail strict identity.
- **Status:** exact in the declared model; disabled as a general empirical premise.

### A4T-C2 — LINEAGE-STITCHED-PATH-COMPOSITION

- **Type:** CONDITIONAL_RESULT / INHERITED_GRAPH_APPLICATION.
- **Claim:** If each adjacent pair of actual local links is joined either by an actual relay of one occurrence or by an actual directed transduction edge, the concatenation is a directed path in the declared event graph.
- **All premises:** the five A4S local/stitch conjuncts with each stitch expanded into `Relay OR Transduce`; identical bearer/interval/signature/boundary bindings; actual support and correct port incidence.
- **Proof:** ordinary finite directed-path concatenation. No new graph-theoretic priority is claimed.
- **Status:** proved conditionally; actual satisfaction unverified.

### A4T-C3 — VALUE-EQUALITY-NONIDENTIFICATION

- **Type:** FINITE_COUNTEREXAMPLE / INHERITED_APPLICATION.
- **Claim:** Equal values at both boundaries do not identify either relay or transductive lineage.
- **Proof:** in the exact model, the all-value-equal observation fiber contains all nine boundary-mode pairs: four route worlds and five nonroute worlds.
- **Status:** exact in the declared model; not a complete physical alternative inventory.

### A4T-C4 — EVIDENCE-RELATION-SEPARATION

- **Type:** EPISTEMIC CONTRACT.
- **Claim:** `E_lineage` is fallible evidence for `Transduce_f`, not numerical identity with it. Downstream agreement without source-side incidence/intervention and alternate-path closure cannot establish the ontic edge.
- **Status:** contract; no physical installation supplied.

### A4T-C5 — LINEAGE-WITHOUT-EXCLUSIVE-OWNER

- **Type:** UCT SCOPE CONSEQUENCE.
- **Claim:** A route may participate in several nested or overlapping actual processes, and a lineage edge may branch or merge. Route existence does not entail a unique source, unique maximal process or unique subject.
- **Source:** UCT I v1.2 §§2.1–2.5, especially P3/P6.
- **Status:** inherited application.

### A4T-C6 — C1-CONDITIONAL-INTERPRETATION

- **Type:** UCT-CONDITIONAL-INTERPRETATION.
- **Claim:** If one lineage-stitched route is part of an admitted actual `P` in complete `K`, C1 maps that organization into `Phi_K(P)`. This does not identify `H_cf`, ownership, agency, a conceptual self, report, fear or a current-assistant consciousness verdict.
- **Status:** conditional; the specific phenomenal bridge remains OPEN.

## 4. Thought experiments

1. **ADC transduction.** Fixed: bearer, sampled physical quantity, ports, conversion table, timing and downstream command. Varied: whether the controller consumes a distinct ADC output occurrence or an impossible numerically identical analogue occurrence. The real conversion preserves directed lineage without token identity; it refutes strict identity as a general necessity.
2. **Copy/replay twin.** Fixed: both boundary values, timestamps within tolerance, output and report. Varied: the actual source edge. A hidden injector writes a value-equal occurrence with no edge from the declared source. This refutes value-level and label-level composition.
3. **Abacus/calculator/human realization.** Fixed: arithmetic relation and final answer. Varied: whether a person's seeing of a bead state causally produces the written calculator input or whether another person reconstructs the same number independently. Human read–write steps create successor events; they do not preserve one numerical token.
4. **Ancestor/formation and neural branching.** Fixed: one ongoing organism and learned action context. Varied: a neural event branches into two downstream effects or several inputs merge at a neuron. Directed contribution can remain actual without a unique parent, unique route owner or cessation of the embedded processes.

## 5. Explanatory payoff and limit

The positive bodily/action relation is now a lineage-coherent causal history rather than either a collage of local tests or an impossible demand that one physical token survive every transducer. This supplies a more realistic organizational candidate for how an anchor, current action formation and bodily write belong together for one bearer. It remains separate from the question of what that relation feels like from within.
