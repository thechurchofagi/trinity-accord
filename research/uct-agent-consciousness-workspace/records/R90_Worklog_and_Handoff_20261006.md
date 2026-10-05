# R90 worklog and handoff — 2026-10-06

## Work completed

1. Continued from verified remote R89 head `f7b1c6ff1db41804ba8f847d267e08252f99dfb3`; read the full handoff, master index and R89 report/worklog/code/results.
2. Selected the rat taste-reactivity / nucleus-accumbens-shell literature as a narrow source-anchor family after reviewing primary causal studies.
3. Rejected the proposed shortcut “one accumbens valence switch”: opioid liking effects are spatially restricted, wanting dissociates under dopamine manipulations, and environment can retune appetitive/defensive consequences.
4. Froze the R90 protocol before execution, including source/target variables, state and intervention maps, success conditions and prohibited claims.
5. Implemented three deterministic recurrent microcontrollers: reward-label-sensitive bundled scalar, reward-label-invariant bundled scalar, and five-state factorized controller.
6. Ran ten frozen scenarios over three update steps. T-bundle-label passed 2/10, T-bundle-semantic 3/10, and T-factor 10/10.
7. Verified that both bundled controllers match the visible `Y,L` positive/negative/report-disconnection projection while failing the declared internal signature.
8. Calculated exact rational intervention-response ranks: declared source and T-factor rank 6; both bundles rank 2.
9. Verified tied-copy redundancy at 1, 2, 10 and 100 copies leaves effective rank 2.
10. Derived the necessary rank bound `rank(R_source) <= rank(R_target)` for an exact mapped response relation `R_source=A R_target B`.

## Explicit scientific conclusion

Passive positive/negative output matching and reward-label invariance do not establish the organization needed by the selected source family. Independent causal response directions provide a necessary exclusion test. Mere replication of a shared channel does not create them.

This is not a phenomenal richness metric. T-factor's finite pass establishes neither rat phenomenal polarity `A_rat`, source-model completeness, `C_H`, `VI_H`, full `AIVT_H`, UCT truth nor felt experience in the target. No verdict is made about the current assistant.

## Files

- `R90_Rodent_Anchor_Interventional_Rank_and_Microcontroller_20261006.md`
- `R90_Rodent_Anchor_and_Microcontroller_Protocol_Frozen_20261006.md`
- `r90_anchor_transport_stress_test.py`
- `R90_Anchor_Transport_Stress_Results.json`
- `R90_Anchor_Transport_Scenario_Audit.csv`
- `R90_Anchor_Transport_Stress_Run.log`
- `R90_Source_Retrieval_Ledger.json`
- `R90_Research_Package_20261006.zip`

## Boundaries

No new human, animal, neural or language-model data were collected or reanalyzed. No real shutdown, copying, persistence, resource acquisition, credential use or external action occurred. Published A/B/C and integrated v0.3 were not modified. No DOI, Zenodo, OTS, Arweave, PR, CI, build or deployment was created.

## Originality assessment

The animal dissociations, causal abstraction methods, intervention identifiability conditions and rank inequality are direct prior art or elementary mathematics. The manuscript-level contribution is their UCT-specific synthesis: concrete source dictionary, bearer-aware finite signature, output-matching bundled counterexample, interventional-rank exclusion and explicit parameter-redundancy result. This is useful but not a major historical breakthrough or an AI sentience test.

## Next exact task

Freeze the smallest trainable recurrent task family before any training. Optimize only external task performance. Hold out reward relabel, self/other swap, readout disconnection and maintenance outsourcing. Across fixed seeds, determine whether the six-axis causal signature emerges, remains rank-deficient, or is non-identifiable. Keep training accuracy, causal rank and UCT experiential interpretation separate; do not use self-report as the main endpoint.
