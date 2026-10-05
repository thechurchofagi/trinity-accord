# R92 reproducibility and data dictionary

Version 1.0, 2026-10-06. Read the research report and frozen protocol before interpreting any number. This package contains tiny networks actually trained on synthetic grids, not LLM or subjective data.

Extract the ZIP into its own directory. Python 3.12.14 and NumPy 2.3.5 were used. No GPU, network, model API or credentials are required. To reproduce in a separate copy (commands overwrite generated results in that copy):

```sh
python r92_delayed_retention.py > R92_Run.log
python r92_readout_diagnostic.py > R92_Posthoc_Run.log
```

The second command is explicitly a post-result diagnostic, not a replacement for the original fixed-budget experiment. Do not run code merely to save the package.

## Files and fields

- `R92_Data_and_Environment.json`: exact train/test/audit grids, environment versions, protocol SHA256 and gradient validation maximum. Targets equal inputs.
- `R92_All_Training_Losses.csv`: 96,000 records with run identifier, step 0–2999 and MSE **before** that update. Step-3000 final metrics are in the full records. Raw MSE differs from normalized N.
- `R92_runs/*.json`: all32 records. Run ID encodes activation, state dimension, training mode and seed. `initial`/`final` include held-out predictions, h0..h3 state arrays, nine Jacobians and singular values. `checkpoints` include E/A/B, Adam first/second moments and metrics at nine steps. `failure` is null for all runs; this does not mean task pass. `interventions` contains `all`, `restore` and each coordinate index at h1. `restore` is the unmodified-state reference, not an independent repair implementation. `checks` include numerical discrepancies and weight-change norms.
- `R92_Summary.csv` and `R92_Results.json`: run summaries, N, maximum derivative error, sampled minimum singular value, thresholds and checks. Numerical rank uses tolerance 1e−9. Task threshold N<0.01; local threshold maximum derivative error<0.2. No missing-value imputation or seed selection.
- `R92_Gradient_Check.json`: pretraining analytic and central-difference values and absolute differences. Final endpoint derivative-check maxima are in each full record.
- `R92_Posthoc_Readout_Results.json`: eight diagnostic fits using train-only least squares; fitted B, singular values/condition number of the training hidden matrix, training/held-out metrics, predictions and states. Diagnostic fits do not alter the original model records.
- The `.log` files retain all printed outcomes, including task failures. Source ledger records actual reading scope, inherited theory audit and inaccessible material. No third-party full texts are redistributed.

`R92_SHA256SUMS.txt` lists SHA256 for every payload file except itself. The ZIP contains that manifest; a separate `R92_Package_SHA256.txt` identifies the finished ZIP. HANDOFF/MASTER_INDEX are updated at workspace root and are not archived inside this experiment package. The archive excludes Python bytecode and transient transfer files.

## Limits

Two-dimensional state and linear output constraints are explicit. The one-state 1/2 bound does not rule out arbitrary nonlinear scalar coding/decoding. Nine derivative contexts are not a continuum certificate. Scores/ranks/singular values are not experience measurements. C1 interpretation remains conditional on actual tokens and a common complete physical signature.
