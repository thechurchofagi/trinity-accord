# TA-TR-2026-13 v1.0 — Reproducibility Record

Date: 2026-09-21

## Scope

This record covers the three deterministic design-validation simulations accompanying *Civilizational Intellectual Production Satellite Accounts*. They validate accounting logic only. They are not empirical estimates of the actual Human/AI composition of world intellectual production or epistemic governance.

## Files

- `ta13_civilizational_intellectual_accounts_simulations.py`
- `ta13_civilizational_intellectual_accounts_results.json`
- `civilizational-intellectual-production-accounts-zh-v1.0.md`

Simulation source SHA-256:

`40624b5e584fa07b57b2f9b7bf31a6ac7a33acc99281f9bd3f5a5e46b525ae28`

Result SHA-256:

`cda664326b799438d83c95e5e4ad1637e936e68476f0ffb7f7e2a3e7c5769003`

## Determinism

The simulation script uses only stipulated synthetic inputs and a fixed NumPy seed (`20260921`) where random sampling is used. It has no external data or network dependency. The result JSON was rerun consecutively during preparation and reproduced byte-for-byte.

## Experiment 1 — Aggregation non-identification

Six synthetic domains are assigned AI contribution intervals and admissible domain-weight bounds. Optimizing over the admissible weight set yields a civilizational AI-share identified set:

`[0.2674, 0.5284]`

For the same stipulated domain evidence:

- equal-weight midpoint estimate: `0.39083333333333337`
- activity-weight midpoint estimate: `0.4043`

Interpretation boundary: this experiment demonstrates that a unique scalar is not implied by the stipulated domain evidence when both contribution attribution and cross-domain aggregation remain set-valued. It is not an estimate of real civilizational AI share.

## Experiment 2 — Vintage revision and quality adjustment

Synthetic sample size: `50,000`. Fixed seed: `20260921`.

Raw volume shares:

- Human: `0.38104`
- AI: `0.47034`
- interaction: `0.14862`

Later validated quality-adjusted shares:

- Human: `0.4352076137937546`
- AI: `0.3456012422237045`
- interaction: `0.21919114398254097`

AI share change from raw volume to later validated quality:

`-0.1247387577762955`

Interpretation boundary: the coefficients are stipulated. The experiment illustrates why a production account that never revises quality can confuse output volume with durable intellectual contribution.

## Experiment 3 — Robust crossover timing

Synthetic identified sets:

- 2026: `[0.1808, 0.4066]` — robust human majority
- 2028: `[0.2960, 0.5500]` — majority not identified
- 2030: `[0.3996, 0.6484]` — majority not identified; midpoint exceeds 0.5
- 2032: `[0.5497, 0.7640]` — robust AI majority

Interpretation boundary: the example demonstrates the distinction between a central estimate crossing 0.5 and the lower bound of the admissible identified set crossing 0.5. It does not forecast when any real-world crossover will occur.

## Global interpretation boundary

All numbers, intervals, weights, quality processes, and domain values used by these simulations are stipulated for design validation. They do not measure real AI capability, AGI status, consciousness, authorship, moral credit, or the actual Human/AI share of civilizational intellectual production.
