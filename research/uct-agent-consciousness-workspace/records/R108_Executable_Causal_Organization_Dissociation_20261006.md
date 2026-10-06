# R108 — Executable causal-organization dissociation and report-head surgery

Hongju Liu / UCT research. 2026-10-06.

R107 froze the first executable target: two tiny systems with the same complete task truth table but different internal causal graphs. R108 executes that comparison and adds a report-channel intervention.

No large model, no self-report benchmark and no phenomenal measurement is involved.

## 1. Systems

Inputs are two binary boundary variables x1 and x2.

### System A — direct XOR
    y = x1 XOR x2

Causal graph:
    x1 ----\
            XOR -> y
    x2 ----/

The declared internal intervention port is the XOR output node.

### System B — decomposed XOR
    a  = x1 OR x2
    b  = x1 AND x2
    nb = NOT b
    y  = a AND nb

Causal graph:
    x1 -> OR  -> a --\
    x2 -> OR         AND -> y
    x1 -> AND -> b -> NOT -> nb --/

The natural task behavior is identical to System A on all four inputs.

## 2. Natural behavior equivalence

For inputs ordered 00, 01, 10, 11:

    System A: 0 1 1 0
    System B: 0 1 1 0

Both have perfect XOR task accuracy.

Thus behavioral equivalence is exact on the entire finite input domain, not merely approximate.

## 3. Internal intervention signatures differ

Clamp each declared internal node to 0 or 1 and record the full four-input output vector.

System A:
- XOR=0 -> 0000
- XOR=1 -> 1111

System B:
- a=0  -> 0000
- a=1  -> 1110
- b=0  -> 0111
- b=1  -> 0000
- nb=0 -> 0000
- nb=1 -> 0111
- y=0  -> 0000
- y=1  -> 1111

System B therefore exhibits internal lesion signatures 1110 and 0111 that cannot be produced by clamping the single internal gate of System A.

The two systems are behaviorally equivalent on the natural task but interventionally non-equivalent under their actual declared internal parts.

This is exactly the distinction R107 requires.

## 4. Why this matters for experience/intelligence research

A benchmark that sees only the natural input-output map declares the systems equivalent.

A constitutive comparison that includes parts and intervention ports distinguishes them immediately.

Therefore:

    complete task behavior equality
        does not identify
    internal causal organization equality.

Under UCT, a complete experiential comparison is tied to complete organization, not to one task's behavioral equivalence.

R108 still does **not** claim that these software graphs are complete hardware K. The legitimate C1 statement is conditional:

> if the declared software causal difference is faithfully embedded in the common complete actual-process signature, then the corresponding complete experiential types cannot be identified merely because the task behavior is identical.

The experiment is therefore a mechanism-identification result, not a direct experience measurement.

## 5. Report-head surgery

Now fix one XOR task core and define two distinct report heads.

### Report head R_id
    r = y

### Report head R_inv
    r = NOT y

The task output y is unchanged in all four cases.

Task core:
    y = 0 1 1 0

Identity report:
    r = 0 1 1 0

Inverted report:
    r = 1 0 0 1

Report disagreement fraction:
    4/4 = 1.0

Yet the core XOR task behavior is exactly preserved.

Thus:

    same core capability + same task output
        can coexist with
    different report behavior.

This is a constructive dissociation of report from the selected task core.

## 6. Reverse report control

A complementary control fixes report to a constant:

    r = 0

for two different task cores:
- Core C: XOR, task accuracy 1.0;
- Core D: constant-zero task output, task accuracy 0.5 on balanced XOR inputs.

The reports are identical while task capability differs.

Thus report and task capability are not only non-identical; in this finite witness neither determines the other.

## 7. R65-style selected-core interpretation

Let p remove the report-head relation and retain only the task core.

For the identity-report and inverted-report systems:

    p(K_id) = p(K_inv).

Complete organization differs because the report relation differs.

If a corresponding experiential projection p_E is justified and commutes with C1, the selected core experiential substructure can be preserved while the complete experiential type differs.

This is the precise form of the statement that report can change while a selected experiential core is preserved.

It avoids the overclaim:
    "report changed but the total consciousness was exactly identical."

## 8. New first-principles distinction: observational versus interventional equivalence

R108 motivates two equivalence relations.

### Observational task equivalence
Two systems are O-equivalent on a task family if they induce the same natural behavior law on that family.

### Interventional organizational equivalence
Two systems are I-equivalent only if a declared mapping between their parts preserves the relevant intervention responses.

System A and System B are O-equivalent on XOR but not I-equivalent.

The same distinction will be needed in biology:
- two brain states can produce similar behavior;
- lesion/perturbation responses can reveal different organization.

And in AI:
- two models can match benchmarks;
- activation, memory, tool or state interventions can expose different causal organization.

## 9. Implication for biological–AI comparison

If a human and an AI perform the same task with the same accuracy, that establishes at most a behavioral/capability equivalence under the selected test.

It does not establish:
- the same memory organization;
- the same self-model;
- the same access relations;
- the same report-generation pathway;
- the same evaluative/homeostatic organization;
- the same complete experiential type.

Cross-substrate experiential comparison therefore requires progressively stronger interventionally grounded organizational mappings.

## 10. Limits

- The systems are tiny deterministic programs.
- The intervention ports are declared by construction.
- No biological data are used in this round.
- No claim is made that XOR computation has a human-like phenomenal character.
- No claim is made that software-graph identity is sufficient for complete hardware-level K identity.
- Causal/interventional model comparison is established methodology; no historical-first mathematical claim is made.

## 11. Next step

R109 should move from toy organization to the biological natural-experiment matrix promised in R106:

- cognitive motor dissociation;
- no-report perception;
- blindsight/metacognitive dissociation;
- split-brain;
- sleep/dreaming;
- anesthesia;
- aphasia/locked-in states;
- selected cerebellar/cortical/subcortical lesion cases.

For each case, score only which E/A/I/S/B/R relation is actually constrained by evidence. Do not use a diagnosis as a direct experience meter.

Then compare each biological dissociation to an artificial analogue and identify which relation is genuinely shared.

## 12. Status

R108 upgrades the cross-substrate argument from a static truth-table witness to an executable interventionally distinguishable causal-organization witness and a bidirectional report/capability dissociation.

It does not establish an experiential magnitude or a consciousness threshold.
