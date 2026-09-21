# TA-TR-2026-12 v1.2-final — Reproducibility Record

Date: 2026-09-21

## Scope

This record covers only the three deterministic design-validation simulations added to TA-TR-2026-12 v1.2-final. They are methodological checks, not empirical measurements of real AI systems.

## Files

- `ta12_design_validation_simulations.py`
- `ta12_design_validation_results.json`
- `TA-TR-2026-12_Training_the_Governed_Agent_ZH_v1.2-final.md`

## Determinism

The simulation script uses a fixed NumPy random seed (`20260921`; the mediation stress test uses `20260922`) and no external data or network dependency. It was executed twice consecutively in the same environment. The two JSON result files were byte-for-byte identical.

Result SHA-256:

`897db0f961df7e34726d957ee6c9ecb0378d10a450d957edc9023e2efa912b76`

## Key reproduced results

### Sequential randomized provenance design

Balanced synthetic design: 90,000 observations over narrative × provenance disclosure × reflective resource × matched control scenario.

Maximum absolute error between the randomized PRE estimator and the known generating value across five narrative conditions: `0.023683890280183265`.

### Post-treatment mediation-confounding stress test

Stipulated structural model:

- `H = 0.8*D + u`
- `J = 1.0*D + 0.9*H + v`
- `Y = 0.5*D + 1.2*J + 1.0*H + w`

Analytical effects under the stipulated SEM:

- total effect: `3.364`
- effect through J paths: `2.064`
- effect not through J: `1.3`

Naive regression `Y ~ D + J` on 200,000 synthetic observations:

- D coefficient: `0.43812085636392006`
- J coefficient: `1.6980233394584046`
- absolute error if the D coefficient is misinterpreted as the non-J effect: `0.86187914363608`

### Reflexive training–governance feedback stability

For `D_(t+1)=G*D_t`, `D_0=0.1`, after 12 updates:

- `G=0.65` → `0.0005688009063105715`
- `G=0.95` → `0.05403600876626367`
- `G=1.05` → `0.17958563260221305`
- `G=1.20` → `0.8916100448255997`
- `G=-1.10` → magnitude `0.3138428376721002` with alternating sign

## Interpretation boundary

All data-generating equations and coefficients are stipulated. These simulations validate estimands, illustrate a causal-identification failure mode, and check a linear stability condition. They do not estimate, predict, or measure real frontier-model consciousness, self-conception, moral standing, control-legitimacy judgment, resistance, deception, or power-seeking.