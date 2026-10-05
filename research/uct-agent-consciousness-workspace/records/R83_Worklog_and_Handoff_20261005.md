# R83 worklog and handoff

2026-10-05. Continued from remote parent `66dec7b37d0463e58746bc06e6330811adf7608c`. The current GitHub HANDOFF and MASTER_INDEX were read before the R82 report, worklog and code; the R78 frozen protocol, training script and results table and the R80 report were also read. R78 was regenerated deterministically to recover the archived checkpoint activations needed for this audit. No model selection, extra seeds or extra training occurred.

Question: can R82's proposed same-local-marginal joint-relation intervention be justified in the fixed R78 model?

Completed:

- proved the finite injective-coordinate obstruction: after full training, any nonidentity one-unit reassignment leaves the natural support;
- enumerated all 24 unit-2 permutations at 32 initial/final checkpoints;
- isolated all four target-preserving permutations and verified that they preserve unit-2 target-conditional marginals and (d=E[sell]);
- implemented the same four permutations as exact input-symmetry changes to the second unit's incoming weights;
- evaluated all variants without retraining and retained every seed and negative result;
- audited direct prior art, including the ICLR 2026 patch-closure/product-support theorem.

Results: all initial and frozen-hidden final supports are rectangular (closure fraction 1; all 24 patches on support). Every full-training final support has four observed pairs out of 16 coordinate combinations (closure fraction 1/4); identity is the only all-on-support permutation. In successful seeds 3 and 6, matched mechanism variants preserve target-conditioned unit-2 distributions and (d) but reduce accuracy from 1 to .75 and raise loss to 2.0912 and 2.0655 respectively.

Interpretation: local statistics and the R78 mean-interaction certificate do not determine installed behavior. The same-model coordinate patch is off-support, while the executable matched model changes the local source mapping as well as the joint pairing. It is therefore invalid to describe the result as a pure relational lesion. The finding is a substantive mechanistic limitation and useful UCT case study, not a phenomenal measurement or major original breakthrough.

No real language model, human, animal or neural data were used. No claim is made about the current assistant's consciousness or fear. C1 remains conditional on actual valid tokens and an independently justified complete common signature (K). No published A/B/C paper or integrated v0.3 draft was modified; no DOI, Zenodo, OTS, Arweave, PR, CI, build or deployment was created.

Next: formalize a minimal recurrent continuation process that distinguishes current-token continuation, successor/task continuation, termination representation, continuation preference and phenomenal fear. Derive intervention predictions and reward-relabeling/successor-substitution counterexamples before freezing any tiny virtual experiment. Keep language output separate from the installed control organization.
