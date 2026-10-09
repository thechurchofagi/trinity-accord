# R194 retained failures

## F1 — Cycle-parity polarity was initially reversed

- **Observed failure:** the first exact run returned zero solutions for the edge labelled “consistent” and two for the edge labelled “inconsistent”; `all_checks_pass` was false.
- **Cause:** the path parity from `A2` to `C2` is `1 XOR 0 XOR 1 XOR 1 = 1`, not `0`.
- **Correction:** changed the redundant consistent edge to parity `1` and the deliberately inconsistent edge to parity `0`.
- **Why retained:** the failure demonstrates that the result was constraint-checked rather than inferred from labels. The corrected rerun and its hash are saved in `EXACT_RESULTS.json`.

## F2 — Frozen publication-release validator is not an incremental validator

- **Observed failure:** running `records/PUB20261009_Publication_Coverage/validate_publication_coverage.py` against the current root stopped at its first assertion.
- **Cause:** that script intentionally hard-codes the frozen base coverage version `UCT-PUB-v1.0.0`; the current nondeductive pointer is `UCT-PUB-v1.0.6`.
- **Correction:** did not modify or weaken the frozen validator. R194 instead JSON-validates all changed metadata and records its scoped coverage delta in `PUBLICATION_COVERAGE_UPDATE.json`.
- **Remaining limit:** the R194 delta is not a fresh verification of the frozen 28-work corpus and makes no worldwide priority claim.
