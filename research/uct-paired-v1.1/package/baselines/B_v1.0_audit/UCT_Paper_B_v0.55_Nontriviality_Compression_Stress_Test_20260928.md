# UCT Paper B v0.55 — Nontriviality / Compression Stress Test

**Date:** 2026-09-28  
**Status:** TRANSPARENT PROXY TEST — NOT A TRUE MDL MEASUREMENT

## 1. Coding rule

The test uses six shared generic operator classes: Res, DoResp, Diff, Comp, Struct, Opt.

Across the nine translators there are **44** generic operator uses and approximately **43** theory-specific signature atoms in the explicit proxy accounting.

If each theory is described independently with one unit per generic operator use and one unit per signature atom, the standalone proxy cost is:

**L_sep = 87.**

This is not Kolmogorov complexity and not a true MDL score. The atomization is researcher-defined.

## 2. Sensitivity analysis

UCT can appear to compress simply because the shared core is counted once and bridge complexity is underpriced. We therefore vary both the shared-framework overhead and the per-theory translator overhead.

|   shared_framework_overhead |   per_theory_translator_overhead |   standalone_proxy_cost |   unified_proxy_cost |   gain_units |   gain_percent |
|----------------------------:|---------------------------------:|------------------------:|---------------------:|-------------:|---------------:|
|                       10.00 |                             1.00 |                   87.00 |                62.00 |        25.00 |          28.74 |
|                       10.00 |                             2.00 |                   87.00 |                71.00 |        16.00 |          18.39 |
|                       10.00 |                             3.00 |                   87.00 |                80.00 |         7.00 |           8.05 |
|                       14.00 |                             1.00 |                   87.00 |                66.00 |        21.00 |          24.14 |
|                       14.00 |                             2.00 |                   87.00 |                75.00 |        12.00 |          13.79 |
|                       14.00 |                             3.00 |                   87.00 |                84.00 |         3.00 |           3.45 |
|                       20.00 |                             1.00 |                   87.00 |                72.00 |        15.00 |          17.24 |
|                       20.00 |                             2.00 |                   87.00 |                81.00 |         6.00 |           6.90 |
|                       20.00 |                             3.00 |                   87.00 |                90.00 |        -3.00 |          -3.45 |
|                       24.00 |                             1.00 |                   87.00 |                76.00 |        11.00 |          12.64 |
|                       24.00 |                             2.00 |                   87.00 |                85.00 |         2.00 |           2.30 |
|                       24.00 |                             3.00 |                   87.00 |                94.00 |        -7.00 |          -8.05 |

## 3. Result

Under a favorable but nonzero-overhead coding with shared-framework overhead 10 and translator overhead 1, the proxy gives:

- L_UCT = 62
- gain = 25 units
- gain ≈ 28.7%

But under a conservative coding with shared-framework overhead 20 and translator overhead 3:

- L_UCT = 90
- L_sep = 87
- gain = -3 units

Therefore **robust explanatory compression has not yet been demonstrated**.

The current evidence supports only this weaker claim:

> real shared formal reuse exists, but its net description-length advantage depends on coding assumptions.

## 4. Per-theory baseline illustration

Using shared-framework overhead 10 amortized across nine theories and one translator-overhead unit per theory:

| Theory                                   |   generic_operator_uses |   signature_atoms_proxy |   standalone_proxy_cost |   UCT_marginal_proxy_cost_baseline |   illustrative_gain_percent |
|:-----------------------------------------|------------------------:|------------------------:|------------------------:|-----------------------------------:|----------------------------:|
| IIT 4.0                                  |                       6 |                       6 |                      12 |                               8.11 |                       32.41 |
| RPT                                      |                       4 |                       4 |                       8 |                               6.11 |                       23.61 |
| GNWT                                     |                       5 |                       5 |                      10 |                               7.11 |                       28.89 |
| HOT                                      |                       4 |                       3 |                       7 |                               5.11 |                       26.98 |
| Predictive Processing / Active Inference |                       6 |                       7 |                      13 |                               9.11 |                       29.91 |
| DIT                                      |                       4 |                       5 |                       9 |                               7.11 |                       20.99 |
| MToC                                     |                       5 |                       5 |                      10 |                               7.11 |                       28.89 |
| AST                                      |                       5 |                       4 |                       9 |                               6.11 |                       32.10 |
| TTC                                      |                       5 |                       4 |                       9 |                               6.11 |                       32.10 |

These percentages are illustrative only.

## 5. Coding-insensitive structural reuse result

Six shared operator classes are reused across 44 translator-operator occurrences.

However theory-specific signatures remain substantial (43 proxy atoms in this accounting).

Therefore the current unification is not a collapse of nine theories into six operators.

## 6. Three-theory detailed interpretation

### IIT

Shared machinery reuse is high, but IIT-specific priors, metrics, partitions, exclusion and composition rules remain a substantial bridge burden.

### GNWT

There is plausible shared formal economy in causal access, consumer composition, reachability and dynamics, but theory-specific consumer/workspace/ignition commitments remain.

### HOT

The generic causal core is small; representation/aboutness grounding dominates the explanatory burden.

## 7. What would count as stronger compression evidence

Paper B should not claim explanatory compression until at least one of the following is achieved:

1. encode standalone target theories in a common formal language independently of UCT and compare literal description lengths;
2. show one fixed UCT law predicts quantitative effects across multiple theory domains without re-fitting;
3. derive a cross-theory prediction that would require separate extra assumptions in standalone theories;
4. demonstrate held-out prediction where shared UCT parameters replace multiple theory-specific parameters.

## 8. Verdict

**Shared formal reuse: PASS.**

**Robust compression gain: NOT ESTABLISHED.**

This blocks Paper B from advancing to publication-candidate rc1 at present.