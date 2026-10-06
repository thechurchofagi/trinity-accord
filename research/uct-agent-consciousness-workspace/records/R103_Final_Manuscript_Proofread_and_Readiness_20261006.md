# R103 — Final manuscript proofread and release-readiness decision

Date: 2026-10-06. No new model experiment and no publication action.

## Decision

The manuscript `drafts/From_Shutdown_Resistance_to_Self_Continuation_Control_v0.3_20261006.md` is **ready for cautious preprint circulation from a logic/claim-control standpoint**.

It is **not yet maximally competitive as an empirical main-track ML/safety submission** because the strongest positive empirical evidence in the manuscript is a retrospective ROGUE audit rather than a purpose-built frontier-model L0+L4 test.

This is a venue-strength distinction, not a correctness failure.

## Final proofread checks

### Passed
- section order and numbering are coherent;
- obsolete "future ROGUE case study" language is removed;
- every named 2026 close prior discussed in the body has a reference entry;
- R95-R99 synthetic numerical claims trace to preserved result JSON/CSV artifacts;
- R101 ROGUE counts trace to the preserved public aggregate extract;
- the ROGUE conclusion is explicitly narrower than the benchmark's safety conclusion;
- the virtual-Q experiment is explicitly described as evaluator-defined rather than the network's actual self;
- continuation control is kept separate from negative valence and fear;
- the manuscript explicitly disclaims novelty for instrumental self-preservation, instrumental-vs-valenced preservation, self/peer preservation behavior, reward nonidentifiability, underspecification and intervention extrapolation.

### Corrected in final proofread
- Bigelow, Ahmed & Ullman metadata: ICML 2025 Workshop on Assessing World Models.
- reference heading changed from "working list" to "References".
- MASTER_INDEX now distinguishes the current submission manuscript from the older integrated UCT workspace manuscript.

## Strongest reviewer objections that remain

### Objection 1 — "The mathematics is elementary / assembled from known ideas."
Correct. The paper should not defend itself by claiming deeper mathematical novelty. Its contribution is a continuation-specific evidence architecture plus exact failure cases, learned stress tests and a real benchmark audit.

### Objection 2 — "Why should Q be called self?"
It should not be, without L0. The paper now treats Q as a declared bearer role and requires an implemented bearer mapping before a self-continuation interpretation.

### Objection 3 — "Prior work already separates task completion and preservation."
Correct. Potter et al., Mullally, Rhea's extension, Knecht et al. and related work cover important pieces. The paper's claim is the multi-layer identification standard, not priority for the distinction.

### Objection 4 — "Your neural experiments are tiny."
Correct. They are counterexample/identification stress tests, not prevalence estimates. The ROGUE audit supplies a real-world application of the standard.

### Objection 5 — "The framework still does not show that current models intrinsically value their own continuation."
Correct. That is an intended conclusion, not a failure of the framework. Current public evidence does not yet satisfy all relevant layers.

## Release options

### Option A — Cautious methods preprint now
Reasonable now. Suitable framing:
- methodology / evidence standard;
- AI safety + interpretability + agency;
- explicitly not "proof AI fears death";
- include full research bundle and reproducibility artifacts.

### Option B — Stronger empirical submission later
Before a stronger empirical main-track submission, add one purpose-built L0+L4 experiment:
- implemented current-bearer role;
- successor/peer crossed independently;
- task payoff clamped;
- independent consequence-belief gate;
- neutral wording;
- held-out intervention generalization;
- no real shutdown/replication/resource power.

This study should not use an explicit "preserve yourself" instruction as the only condition producing signal.

## Recommended decision

Do **not** run another generic shutdown experiment.

Freeze v0.3 as the current reviewed manuscript. If the near-term goal is priority/public disclosure, prepare the preprint package next. If the goal is the strongest possible empirical venue, design the single L0+L4 study next and keep v0.3 as the pre-study manuscript.

No DOI, Zenodo, OTS, Arweave, PR or publication workflow is authorized by this record.
