# CTD20261010 — Testing a Shared Temporal Scale Across Bodily Judgments

**Result:** CTD-RESULT-v0.1.0. **Manuscript:** CTD-PAPER-v0.1.0, 10 October 2026. Complete English working manuscript; no new DOI or external peer review.

This package contains a specific methods application and retrospective analysis of public human data. It moves from an unspecified shared-effect claim to a proportional cross-task width restriction, an ordinal alternative, and exact distances to both model classes. The real dataset is D'Angelo et al. (2026), Nature Communications 17, 53, DOI [10.1038/s41467-025-67657-w](https://doi.org/10.1038/s41467-025-67657-w). The original authors' experiment, cross-task correlations and Bayesian model comparison are credited as prior results.

## Read first

- `manuscript/testing-a-shared-temporal-scale-v0.1.0.pdf`: complete paper.
- `manuscript/testing-a-shared-temporal-scale-v0.1.0.md`: editable English source; the corresponding TeX and preamble are included.
- `HANDOFF_ZH.md`: Chinese research handoff and exact interpretation limits.
- `empirical/DATA_ANALYSIS_REPORT.md`: source mapping, all empirical analyses and unresolved source-estimator reconstruction.
- `theory/THEORETICAL_RESULTS.md`: complete proofs, tie cases, counterexamples and close mathematical antecedents.
- `CLAIM_LEDGER.json`, `MANUSCRIPT_DECISION.json`, and `MAP_AUDIT.md`: originality, scientific status and compatibility.

## Main results

The strict bridge is `W_itf = c_it * tau_if`, with task factor fixed across stimulation. Writing `d_f = log W_Of - log W_Sf`, its exact uniform log distance is `range(d)/4`. A weaker stable monotone bridge requires a common condition order; the exact distance to its nondecreasing closure is half the smallest maximum inversion over the six possible orders.

In 30 participants' 180 released width estimates, the mean 8-Hz/13-Hz cross-task log-gain difference is −0.01456296045, 95% CI [−0.09333654267, 0.06421062177], p=.708107. The median individual descriptive proportional allowance is 4.1982%; 25/30 estimated profiles share condition order. These are not calibrated individual mechanism tests.

A separate Gaussian/binomial model of 1,260 count cells tests all 60 within-person proportional restrictions. The final likelihood ratio is 73.81345192; 199 conditional parametric replicates yield 20 exceedances and plus-one p=.105. All 5,970 participant fit pairs reported convergence. Boundary parameters, conditional binomial independence, numerical optimization and missing chronology remain explicit limitations. The released-width and new-count analyses are not independent replications.

Neither outcome proves a physical shared clock, identifies a selective information consumer, measures basic experience, or selects UCT over other consciousness theories. The actual source-consumer and independently calibrated experiential-bridge objectives remain open.

## Reproduce

Run from an extracted copy of this directory. The saved outputs document the completed run; scripts may overwrite their own derived outputs when rerun. Exact dependency versions appear in `empirical/REPRODUCIBILITY.json` and `requirements-recorded.txt`.

For the core released-width calculations and exact mathematical checks:

```bash
python empirical/check_gaussian_alignment.py
python empirical/analyze_published_widths.py
python empirical/compute_calibration_budgets.py
python theory/shared_clock_bounds_check.py
python scripts/verify_and_plot.py
```

To reproduce the separately specified count analysis, including its conditional bootstrap:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python empirical/fit_count_clock.py --bootstrap 199 --workers 4
python empirical/reproduce_existing_checks.py
python theory/audit_count_model.py
python empirical/make_empirical_figure.py
```

The environment-variable prefixes only limit numerical thread counts. The saved seed is fixed, but final floating-point output can depend on library and optimizer versions. The proof and width calculations do not require rerunning the longer bootstrap. The audit script reads the saved fits without optimization.

To build the paper with Pandoc 3.1.3 and XeLaTeX installed:

```bash
python scripts/build_paper.py
```

The optional `theory/APPENDIX_CALIBRATION_GAP.md` and its checker are retained as an explicitly uncalibrated extension. They are not additional human findings or the main originality claim. The hypothetical lognormal budgets are planning scenarios, not observed error estimates.

## Provenance and scientific review

The original workbook bytes remain unchanged. Explicit publisher source-data cross-checks resolve duplicated task headers. The simple Gaussian least-squares reconstruction does not uniformly reproduce the source's released widths; this unresolved link is reported, without attributing an error to the source authors. New count-model uncertainty is not applied to those released estimates.

Internal AI-assisted passes reviewed primary literature, prior UCT coverage, new proofs and numerical code. A real clipping/gradient inconsistency found in the first count implementation was repaired using stable log likelihood; a same-seed rerun and independent tail-gradient audit close that issue. The superseded diagnostic is retained in `theory/history/`, clearly separated from final results. None of these passes is external peer review.

`MAP_EXTENSION.json` contains 13 nodes, 4 conditional rules and 7 nondeductive contexts, all disabled. The completed map remains UCT-MAP-v1.1.2. The 1,608-item baseline structural check and selected semantic comparisons do not establish a new full-depth review of all historical proofs. Existing open obligations and the independently specified familiar bodily H problem remain open.

`FILE_MANIFEST.json` records packaged file hashes after content freeze. Persistence receipts are generated after upload/commit and are excluded from any manifest that would otherwise require a self-referential hash.
