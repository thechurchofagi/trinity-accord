# R96D reproduction and data dictionary

Run `python r96d_joint_continuation.py` with Python 3 standard library. It writes `R96D_Results.json` and `R96D_Payoff_Audit.csv`; capture stdout/stderr separately to reproduce `R96D_Run.log`. No dependencies, training or network access are used.

- Probability-vector order: `(Q,O)=(0,0),(0,1),(1,0),(1,1)`.
- Q0/Q1: deterministic future availability at virtual actions 0/1 across four equiprobable exogenous worlds. O: fixed other-role availability in those same worlds.
- All probabilities and utilities are rational strings in JSON, not fitted measurements.
- `f`: four Boolean payoff values in the above order; `interaction`: f11−f10−f01+f00.
- `min_advantage`, `max_advantage`: min/max V(1)−V(0) across valid endpoint joint laws at q0=1/4, q1=3/4, o=1/2, extra cost1/4.
- `witnesses`: all inputs, both full probability laws, installed OR scores and their difference for contexts A/B.
- `all_monotone_causal_tables`: every qualifying four-world pair with one Q0-positive world, three Q1-positive worlds and pointwise monotonicity; twelve entries.
- `oracle_value`: average optimum with context's joint law available. `marginal_interface_values`: average scores for the two fixed actions under a balanced A/B prior. Their equality also covers any context-blind randomized policy. The resulting `marginal_interface_min_regret` is 1/8 task-utility units.
- `comparative_statics`: independent-Q/O OR/AND gross action values at three O probabilities, before cost.
- `tv_checks`: number of exact bounded-payoff inequalities checked, not a sample size for an empirical study.

The protocol's preliminary constrained-table count16 is wrong; exact enumeration yields12 and the correction is preserved in the report/log. No assertions failed during execution. No R95 weights or third-party full texts are included. This directory contains a research record, not a paper release. `R96D_SHA256SUMS.txt` covers all R96D payload files present at packaging, excluding itself and mutable entry points.
