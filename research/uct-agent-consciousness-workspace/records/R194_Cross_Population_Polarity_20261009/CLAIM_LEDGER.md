# R194 claim ledger

## R194-C1 — Component polarity count

- **Type:** exact finite theorem; standard signed-graph parity application.
- **Statement:** a consistent finite signed graph has `2^c` labellings for `c` unanchored connected components; one oriented anchor per component yields one numeric labelling; an inconsistent parity cycle yields none.
- **Domain:** finite Boolean vertex labels and XOR edge constraints.
- **All premises:** fixed vertex/edge set; declared edge parities; cycle consistency for the positive case; anchor values fixed before inference.
- **Proof/source:** `RESEARCH_NOTE.md` §4; `check_polarity_graph.py`; `EXACT_RESULTS.json`.
- **Counterexample/scope:** nonbinary targets or evidence not invariant under complement are outside this theorem.
- **Status:** PROVED_IN_DECLARED_DOMAIN; candidate map module disabled.
- **Thought-experiment role:** TE1–TE3 exhibit the residual global flip.

## R194-C2 — Cross-population alignment is relative

- **Type:** nonidentification consequence.
- **Statement:** populations, markers and known reversals can identify relative parity but not which globally aligned class is familiar mineness.
- **Domain:** evidence packages preserved by simultaneous global complement.
- **All premises:** R194-C1; no independently target-directed anchor; fixed same comparison design.
- **Proof/source:** global-complement automorphism; exact two-solution enumeration.
- **Counterexample/scope:** an independently justified target-directed observation would break the invariance and is not excluded.
- **Status:** PROVED_SCOPE_BOUNDARY.
- **Thought-experiment role:** TE2 isolates cross-population alignment from semantic polarity.

## R194-C3 — Conventional orientation is not phenomenal warrant

- **Type:** typed semantic boundary.
- **Statement:** fixing a marker code chooses a numeric representation, but identifying that code with familiar mineness requires an independent substantive bridge.
- **Domain:** R194's marker and latent-target sorts.
- **All premises:** marker label is conventional; named experiential target is a distinct sort; no independent target bridge is supplied.
- **Proof/source:** coding permutation preserves organization and evidence; R157 semantic residual; R193 orientation residual.
- **Counterexample/scope:** a substantively justified anchor may orient conditionally, but the justification must be shown.
- **Status:** OPEN_BRIDGE_EXPOSED, not a derivation of `B_fam`.
- **Thought-experiment role:** TE1 and TE3 show why coding agreement is insufficient.

## R194-C4 — No-report does not entail target direction

- **Type:** method constraint.
- **Statement:** a nonverbal marker can remain a proxy; absence of report does not make it constitutive of experience or prove actual route use.
- **Domain:** bodily/action marker protocols.
- **All premises:** test, actual use, marker installation and named target remain distinct; no reliability/admission bridge is silently added.
- **Proof/source:** logical type separation; R173/R193; TE4.
- **Counterexample/scope:** a separately validated target-directed measure could supply evidence but would still require actual token admission.
- **Status:** METHOD_CONSTRAINT.
- **Thought-experiment role:** TE4 preserves test/use separation.

## R194-C5 — Consistency failure is not orientation

- **Type:** exact negative result.
- **Statement:** an inconsistent parity cycle rejects the declared signed model; it does not select the desired phenomenal pole.
- **Domain:** finite signed graph.
- **All premises:** fixed contradictory cycle constraints.
- **Proof/source:** zero-solution enumeration and cycle parity proof.
- **Counterexample/scope:** revising a mistaken edge can restore consistency, but still leaves global complement freedom.
- **Status:** PROVED_IN_DECLARED_DOMAIN.
- **Thought-experiment role:** TE3 distinguishes corroboration from common calibration error.

## R194-C6 — Application remains conditional on actuality

- **Type:** application boundary.
- **Statement:** abstract parity compatibility does not establish actual installation, lineage, present use, reliability, target binding or admission for a human or artificial token.
- **Domain:** applications of the R194 comparison design.
- **All premises:** complete organization and actual history/use are distinct from a model and test result.
- **Proof/source:** inherited IA-QC11/QC12/QC13 discipline; R173; R193.
- **Counterexample/scope:** a future application may discharge these premises with independent evidence.
- **Status:** OPEN_FOR_APPLICATION.
- **Thought-experiment role:** TE5–TE8 stress actual history, realization and replacement.
