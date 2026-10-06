# R123 — Separate the observed channel from the proposed biological mechanism

**Hongju Liu / UCT research checkpoint — 6 October 2026**

**Continuation baseline:** `thechurchofagi/trinity-accord`, branch `uct-agent-consciousness-workspace`, commit `bf55557992b84f6df4dfc6a924f291dfde7b976b`.

## 1. What actually advanced

Two computations were executed, rather than stopping at a research plan: (i) an exact and simulated qualification of the R122 neural measurement filter; (ii) a post-hoc robustness/control audit of all twelve archived recording-session summaries. Neither repeats the R122 biological fits. Their joint consequence is that the next T2 attempt must explicitly model its measurement channel and test the incremental value of neural variables, rather than promote decoder smoothness or a positive standalone decoding score into an accumulator-state certificate.

This is a methodological checkpoint, not a claim of a major empirical breakthrough. T2 remains open; no new neural transition model or biological intervention transport was fitted.

## 2. Foundational versions and reading scope

The latest **verified** Paper A is UCT I **v1.2**, TA-TR-2026-20, DOI `10.5281/zenodo.23131575`. Its release receipt records successful public readback. The published manuscript is on `research/uct-paper-a-v1-2-20261004`, pinned at `f8750d32afeea9209e6d53ad3cfbd5bbde7a8126`, under `research/unified-consciousness-theory-i/versions/v1.2/published/`. A version named v1.3 has not been verified. An intermediate RC release note must not override the later publication receipt.

Paper B is UCT II **v1.1**, DOI `10.5281/zenodo.23030320`, at branch `research/uct-ab-v1-1-20260929`, subsequently resolved to `562a5d16745e5e7e6cb4bc8f2c53a2f62e05875a`. Its manuscript blob is `c4734243b6dfd75255c14b99f333c52e7d7b7a58`. Paper C is UCT III **v1.0**, TA-TR-2026-23, DOI `10.5281/zenodo.23137088`; its published Markdown blob at the continuation baseline is `be7c7a952aa88831c6660187586d92a3da707cdf`.

This round read A's main text through its conclusion/compatibility section, B's main argument through its conclusion, and C's main text through its conclusion plus its residual-prediction appendix. Overlapping retrievals filled truncated main-text portions. A's entire reference list/appendices and every B/C supplementary artifact were **not** independently re-audited. This is not a claim to have read every byte of all released packages.

The requested fourth **medical/clinical paper** has not been identified by a title, DOI and source path. Repository research directories, relevant research branches, and prior-context retrieval did not resolve it. This limited search does not establish absence. RLC is mathematical research and has not been substituted for the missing medical paper. No patient-level or medical conclusion is drawn.

## 3. The exact UCT dependency used

A §§3.1–3.5 distinguish complete constitutive organization, scientific views, estimates, and subjects; §5.3 supplies probe invariance; §§10–12 separate finite bridges from C1. B §§2 and 4 require pointed, port-aware, non-oracular translation, and §17 requires held-out recovery beyond relevant baselines. C §§4.3, 5 and 10 distinguish actual processes, retrospective reports, capability fibers, and finite measurements; Appendix B separates genuine conditional information from fitted-model error and repair of an incomplete baseline.

Accordingly, let `K_bio` denote the selected actual biological organization, `n(t)` the recorded neural signal, and `z(t)=M[n](t)` an analysis-derived channel. A property introduced by M is not automatically a constitutive property of K_bio. Implementing M is itself physical computation, but its physical existence does not relocate its memory into the rat's selected process. This is an application of the already published boundary/view discipline, not a new UCT axiom.

The corresponding empirical tests concern finite mechanisms only. E remains latent. Poor decoding does not imply absent experience; good decoding does not prove human-like experience. Access, selfhood, and report are not experience-existence gates. Nothing here changes the four remaining deep bridge problems or collapses content into valence.

## 4. Executed measurement-channel calibration

The pinned `b2_decode.py` defines 50 ms bins, a 100 ms readout delay, and a causal half-Gaussian with sigma 75 ms truncated at four sigma. Its seven normalized weights, in current-to-past order, are:

`[0.4201765661, 0.3364510923, 0.1727397505, 0.0568647146, 0.0120025540, 0.0016243690, 0.0001409535]`.

For temporally independent, equal-variance raw bins x, the filtered signal is `z_k = sum_j w_j x_(k-j)`. Direct covariance expansion gives

`rho(h) = sum_j w_j w_(j+h) / sum_j w_j^2`.

This is standard linear-filter algebra, not a new theorem or a biological model. At lag one:

- population correlation: **0.6502595392**;
- population optimal one-lag linear prediction R²: **0.4228374683**.

Two fixed-seed independent Gaussian-input checks (seeds 123 and 124, 400,000 input bins each) gave filtered lag-one correlations **0.6492764460** and **0.6494586991**. Their raw lag-one correlations were approximately 0.001413 and −0.001268. All checked lag correlations agreed with the exact calculation within the declared numerical check tolerance of 0.012.

Thus substantial adjacent-bin predictability can arise from this observation channel with no time dependence in the underlying input. This does **not** show that rat neural memory is artifactual. The white-input null is not the neural null: colored inputs, slow drift and genuine dynamics require separate controls. Its R² predicts a different target from the R122 cumulative-evidence decoder; **0.422837 must not be subtracted from, or compared as explained variance against, the biological 0.054277/0.036449 scores**.

The source code also fixes a relevant timing fact. A target cumulative-count endpoint t uses spikes with total support approximately **[t−250 ms, t+100 ms)**. The filter is causal relative to the delayed neural observation, but the feature is not available at target time t. Calling that feature an online state at t would introduce an undeclared future observation. A 100 ms biological encoding delay is an analysis assumption, not an independently established equality of biological and artificial clocks. C4 must represent these clocks explicitly.

## 5. Executed audit of the retained biological results

The input was `R122_Biology_B1_B2_20261006/b2_results/B2_session_metrics.csv`, 2,998 bytes, Git blob `5d398ea4fc530b5418ba84fd133ba6fd03cedba3`, SHA-256 `750e68df8b04bffaa3151cbb17efd27dcd9f6e9abbf956295ee9291ad7ecfdb4`. The local copy passed an exact Git-blob digest check before analysis.

All twelve sessions/five rats were retained: 3,319 B2 trials and 32,656 held-out bins. Means were taken over sessions within each rat, then equally over rats.

| Archived predictor | Equal-rat held-out R² |
|---|---:|
| FOF neural-only | 0.0542768811 |
| ADS neural-only | 0.0364488317 |
| Eventual-choice/time/duration diagnostic | 0.2005731897 |
| Same diagnostic plus recent evidence | 0.4958806630 |

FOF and ADS each lose to the first diagnostic in **12/12 sessions and 5/5 rat averages**. These are not 24 independent animals. The comparison is exploratory; no confirmatory significance claim is made.

This is a **standalone-model** comparison. It does not show that adding neural information to the baseline has zero predictive value. That question requires the joint model `baseline + neural`, evaluated against the same baseline on the same held-out trials. Nor is the diagnostic an online memoryless agent: it includes eventual choice, which is a future outcome. These two invalid inferences are explicitly excluded.

Leave-one-rat-out sensitivity was computed for every rat, not only the favorable exclusion. Excluding A297 yields mean neural R² of **0.0130066417** (FOF) and **0.0200640156** (ADS), with choice/time-centered descriptive correlations **−0.0071803964** and **−0.0126715163**. Full-sample centered correlations are 0.0492376215 and 0.0421035237. This identifies material sensitivity to one rat, not absence of biological information or a reason to discard that rat. All five exclusion results are saved.

## 6. Consequence for the actual next experiment

Retain the same evidence-accumulation domain. First qualify the observation model and compare baseline-only, neural-only, and joint predictors on a common cohort. Use raw-bin features as the primary observation and the existing half-Gaussian as a declared sensitivity analysis; keep source rows, masks, folds, and neuron selection matched so that changing a filter does not silently change the sample. Separate retrospective eventual-choice diagnostics from predictors legally available at each online state time.

Only then fit and compare biological/artificial transition laws with frozen state/input/output/time maps. Predict held-out transitions and admissible perturbation responses rather than fit a new map separately to each outcome. A positive observational joint-model result still does not certify causal use or C2/C3.

The twelve recording sessions contain no laser-on trials. B3 therefore remains unreplicated. Projection silencing, whole-region silencing, accumulator reset, and external click insertion remain different interventions. Randomized external clicks may support an input-port analysis under separately justified assignment assumptions, but cannot stand in for a missing internal neural perturbation.

`NEXT_EXPERIMENT.md` records the bounded prospective test and fail conditions. Its real-data fits were **not** executed in R123. The current environment could read GitHub through the connector but could not resolve the raw download host from the execution container; the verified small retained CSV allowed useful work to proceed. The historical successful R122 download remains valid. No new domain, DOI, CI run or published-file modification was introduced.

## 7. Completion and anti-stall discipline

Completed: version-grounded main-text reading, measurement-null computation, exact-digest-verified retained-data audit, and a concrete revision of the next experiment. Not completed: identification/reading of the fourth medical paper, every supplementary source, the prospective neural joint-model fit, biological/artificial T2 closure, T3/G4, or an external test of C1/U1.

On continuation, fetch HEAD and follow a newer round if present. Do not repeatedly reformulate this plan. A failed retrieval route gets a bounded number of attempts; then change the route or run a useful analysis on verified available artifacts, preserving the failure. A planning document is not execution, an uploaded blob is not a branch commit, and a numerical check is not a major scientific result. The next substantive milestone must report actual held-out joint-model or transition/perturbation results with the stated limitations.
