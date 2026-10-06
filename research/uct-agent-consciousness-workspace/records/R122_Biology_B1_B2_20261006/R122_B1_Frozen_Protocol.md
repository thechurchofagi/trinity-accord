# R122 B1 analysis protocol — frozen before choice-effect fitting

Date: 2026-10-06. Scope: only Gupta et al. (Neuron 2026) 12 public recording sessions, and comparison to the already executed R117 support experiment. The first A294 session's structural schema and click-count identities were inspected before this protocol; no B1 choice-effect model was fitted before writing it.

## Estimand and provenance

This is a new independent psychophysical-kernel analysis requested in R117. The pinned author repository and the complete final paper/supplements do not provide a corresponding author psychophysical temporal-kernel estimator. Do not call it a replication of an author kernel. It is an observational choice analysis and cannot identify a neural intervention response or rule out every intermittent/snapshot strategy.

Primary time coordinate: 10 equal fractions of the observed `Trials.stim_dur_s_actual`, after the author's explicit click transformation `raw[1:] - raw[0]`. The removed first click is shared stereo onset. Each feature is the right-minus-left click count in one fraction. NumPy histogram intervals are left closed/right open, with the final right endpoint included. Store physical duration and raw counts; normalized fractions are not the R117 fixed 10-bin physical clock. Coefficients in raw click units and standardized feature units will both be saved. Do not compare absolute coefficient magnitude or the AI causal +1-pulse effect directly to an uncalibrated rat behavioral slope.

## Eligibility and identities

Retain source file, source MATLAB row (1-based), source session ID, rat and SHA-256. Preserve every raw trial and every exclusion in the audit. Fit accumulation trials (`trial_type='a'`), nonviolations, binary observed choices, finite positive duration/on-off events, finite sorted click vectors, shared first click, and exact agreement between computed R-minus-L and stored `click_diff`. Require the recorded laser `isOn` flag to be zero; exclude a positive pharmaceutical dose if present. Missing drug metadata is not proof of a particular pharmacological state. Source `Trials.rat/date` opaque MATLAB types are not decoded; plain top-level and `rec` metadata must agree.

Keep both correct and error trials. Keep ties in choice-model fitting. Omit ties only from a separately labeled descriptive agreement with the sign of total evidence; neither a tie nor a choice becomes an experiential label. Do not infer source correctness labels from UCT.

## Models and controls

Fit each recording session separately, using a logistic model with intercept and fixed L2 regularization `C=1.0`, LBFGS, tolerance `1e-8`, maximum 2000 iterations. Standardize predictors using training rows only for every held-out fold. The modest fixed penalty avoids unstable/separated short-session fits; it is not selected after inspecting biological effects.

The four prespecified models share nuisance predictors: actual stimulus duration, prior rewarded signed choice, prior error signed choice, and prior-history missing indicator. Prior history refers to the immediately previous source row and is marked unknown when that source row is not a valid accumulation choice; no default rewarded-right first trial is fabricated.

1. **full10:** all ten temporal evidence-count predictors.
2. **lastbin:** only the final normalized-bin evidence count.
3. **total:** one total-evidence count predictor, a constant-weight accumulation control.
4. **nuisance:** no evidence-count predictor, only the common nuisance terms.

The primary predictive contrast is `full10` versus `lastbin`. Report `total` versus `lastbin` and `full10` versus `total` as controls; a well-predicting total model is consistent with broad constant temporal weighting. A failure of the flexible full10 model to beat total is preserved rather than treated as failure of accumulation.

## Held-out prediction and aggregation

Use five contiguous blocks in source-trial order per session. Hold out entire trials. Purge the immediately adjacent retained trial on each side of the held-out block from training to reduce boundary dependence from one-step history. No test choice affects fitting or scaling. This is blocked within-session prediction, not prediction on new rats and not prospective forecasting. Do not fit pooled identity intercepts and then claim leave-rat generalization.

Save trial-level out-of-fold probabilities, source IDs, fold membership, log loss, Brier score, accuracy and paired per-trial loss differences. If a training fold lacks both choice classes, record the failure explicitly; do not fill invented probabilities. Any small/invalid session is preserved as a failure with its eligible count.

Report per-session outputs, then average sessions within rat, then average rats equally. Five rats, not thousands of bins, are the independent biological units for aggregate uncertainty. Give across-rat variation and an explicitly small-sample descriptive t interval (df=4 when all five are available); avoid definitive population-level claims from five clusters. Fitted kernels are descriptive regularized estimates, not causal effects.

## Prespecified timing sensitivity

If at least 50 eligible trials across at least three rats have actual duration >=0.8 s, fit an additional descriptive model on that fixed long-duration subset: four 200 ms absolute evidence bins spanning [0,0.8] s, plus post-0.8-s evidence as a nuisance predictor and the common nuisance terms. This separates absolute physical time from normalized trial fractions without treating absent late evidence as measured zero. This check is secondary; its sample and any inability to run it are reported. No search over bin counts, duration thresholds or preferred coefficients is allowed after results.

## Interpretation limits

The kernel tests whether temporal evidence history improves held-out choice prediction relative to a final-bin control. Together with B2 it can strengthen T1 and the observational grounding/baseline components of a T2 certificate. It does not by itself identify biological transition commutation, transport a neural lesion to an AI reset, establish T2 closure, establish T3/G4, measure E or V, or prove ordinary phenomenal equivalence.
