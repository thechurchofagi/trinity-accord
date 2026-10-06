# R133 validation and review scope

## Executed checks

`python3 check_observable_control.py`: PASS, 22 named checks. Exact Fraction/set arithmetic; 756 comparisons of support recursion with exhaustive direct hidden-state evaluation across four probe models, 63 nonempty initial supports and horizons 0–2. Each horizon-two model has 193 deterministic observable policy trees, including early stopping. One model has noisy stochastic outputs, so positive-probability failure paths are exercised. This finite enumeration does not prove the general purification theorem.

The same script independently enumerates every nonempty-row 3-by-3 successful-action family (343) and every observation partition of three candidates (5), giving 1715 checks against direct decision-rule enumeration. The minimum message count is compared with exhaustive action-subset covers. It also checks the pairwise/full intersection distinction, incomparable sufficient partitions, avoidance witnesses, fixed-model versus stagewise traces, time-limited probes, common enabledness, and qualitative/quantitative support limits.

`python3 validate_formal_map.py`: PASS, 112 checks; 276 nodes, 127 rules. All 262 baseline nodes and 119 baseline rules preserved field-for-field. Four published snapshots retain their byte counts, SHA-256 and Git blob identities. All 53 explicit node scope fields are exported in the current full proof ledger. Rule endpoints, conjunctions, acyclicity, prohibited backflow and existing source-fidelity obligations pass their declared checks.

## Manual proof review

| Obligation | Review conclusion |
|---|---|
| Actual information available to policy | Only observed actions/outputs; no free menu or hidden-model access |
| Persistent model and sufficient state | Immutable model index; resources and phase must be included as required |
| Finite-horizon recurrence | Goal closure, stopping, impossible outputs and empty menus treated explicitly |
| Probability-one randomization | Positive action/transition factors propagate any failing continuation; finite induction supplies deterministic choices |
| One-shot encoder result | Both lower and upper cover constructions given; physical observation feasibility left as premise |
| Coarsest partition qualification | Task-relative counterexample does not alter the earlier full-interface theorem |
| Probe comparison | Sensor dynamics and consumed steps explicit; free-signal theorem not misapplied |
| Literature | Classic qualitative partial-observation methods credited; nearby 2026 full text retrieval failed, so comparison remains incomplete |
| Experience interpretation | No added existence gate, richness metric, subject count, valence or T2 closure |

This is a second pass by the same assistant, not independent peer review. The graph checks are bookkeeping and source/dependency checks; acyclicity is not a mathematical proof. The finite checks audit concrete examples, not all histories or all models outside their enumeration. The general results rest on the written conditional proofs. No theorem prover, new neural data, agent training, biological experiment or empirical intervention transport was run.

## Corrections and limitations retained

During preparation, added a genuinely stochastic probe example to exercise the positive-probability branch condition; all 756 resulting comparisons passed. No failed theorem or dropped negative result is concealed. Full-formalization completeness and historical originality remain unclaimed. T2 OPEN; C3 intervention transport NOT_TESTED; valence OPEN.

Storage verification is recorded separately in the package save receipt, after GitHub commit creation; it is not a scientific validation step.
