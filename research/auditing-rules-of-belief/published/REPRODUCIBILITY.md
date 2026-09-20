# TA-TR-2026-11 v2.0 — Reproducibility Receipt

Date: 2026-09-21

The v2.0 paper retains two deterministic model-organism demonstrations from its v1.1/v1.2 research cycle without changing the recorded experiment bytes.

## Experiment A — HMM epistemic-audit model organism

- script: `formative_epistemic_audit_experiment_v1.1.py`
- script SHA-256: `0542d3a1a0f0396ccf4409a1aad05ed1234062f3ece68eb64a2f9a6768ad07a8`
- result: `formative_epistemic_audit_results_v1.1.json`
- result SHA-256: `4650049b00d174adf644507cf1b9cd419281a4ddf677bdc32ff807e640aea5f8`

Recorded environment: Python 3.13.5; NumPy 2.3.5; PyTorch 2.10.0+cpu; deterministic PyTorch algorithms; one PyTorch CPU thread. The result was reproduced in consecutive runs with byte-identical JSON.

Key recorded quantities include GRU belief-decoder R² values 0.9982903, 0.9993660, and 0.9995343; compensated hidden-to-readout maximum logit difference 2.0921e-7; decoder-direction intervention RMSE 0.097507; and one-dimensional positive-control mean intervention RMSE 0.00991895.

## Experiment B — Arithmetic contradiction stress test

- script: `arithmetic_contradiction_stress_test_v1.2.py`
- script SHA-256: `e068198fc5b0d74612785100ee0da12e48c6072e750863a966f611f147392e92`
- result: `arithmetic_contradiction_stress_test_v1.2_results.json`
- result SHA-256: `2475304cd3e080c8bbe20d3d522ab3aa944ed9e4a7ebb515d1499abe0de9e631`

Recorded environment: Python 3.13.5; NumPy 2.3.5; PyTorch 2.10.0+cpu; deterministic algorithms enabled; one PyTorch CPU thread. The result was reproduced in consecutive runs with byte-identical JSON.

The test fixes ordinary integer addition externally and gives `1+1=3` a loss weight of 16 relative to the mean loss over the other 99 correct digit-pair examples. It compares a frozen-backbone report adapter, a flexible full model, and a restricted global linear-rule model.

## Interpretation boundary

Exact computational reproducibility establishes only that these stated synthetic experiments are reproducible in the recorded environment. It does not validate a philosophical interpretation of "belief", establish uniqueness of a high-level abstraction in frontier language models, or turn the GPT-5.6 Sol prospective forecast into experimental evidence.
