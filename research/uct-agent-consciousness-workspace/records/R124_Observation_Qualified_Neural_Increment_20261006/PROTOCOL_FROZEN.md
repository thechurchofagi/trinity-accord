# R124 — Observation-qualified neural incremental prediction
Frozen before new neural scores were inspected on 2026-10-06. This is a prospective implementation within an already explored dataset, not a blind preregistration. Baseline: 2f358ac0cb29c4dddc53933fa709ca8aec03be1f.

## Question and scope
On identical whole-trial holdouts, do FOF/ADS neural variables improve prediction of externally defined cumulative R-L evidence beyond declared control variables? Raw 50 ms counts/rates are primary; the R122 seven-tap half-Gaussian is sensitivity. Prediction is not causal use, transition commutation, experience measurement, or intervention transport.

## Cohort, clocks, and folds
Recover all twelve pinned MAT sessions; compare SHA-256 against R122. Reuse the R122 loader, eligible trials, maximal delayed-filter exclusion, and original 5 contiguous whole-trial outer / 3 inner folds. Unit firing-rate qualification and region matching reuse seed 122 and exactly the R122 selection law within each training split.

A separate zero-delay online sensitivity uses neural windows ending at target t. Its wider pre-onset filter support gets an explicit additional gap audit; if needed, censor offending online trials but preserve the original primary retrospective cohort and original fold assignment. Never silently alter the paired raw/filtered cohort. Main delayed features end at t+100 ms and remain retrospective.

## Predictors and estimator
Retrospective primary B = intercept, eventual choice, t, t^2, choice*t, choice*t^2, realized duration.
Retrospective sensitivity adds the current 50 ms signed click count.
Online sensitivity B = intercept, t, t^2, current signed click count, its interactions with t and t^2, and current total click count. No eventual choice, realized duration, or future spikes enter online predictors. This is a recent-input baseline; it is not the full input history, which already determines the external target exactly.

Compare B-only, neural-only, and B+neural. Use partial ridge with unpenalized B, training-only residualization/standardization, lambda grid [0.0001,0.001,0.01,0.1,1,10,100,1000,infinity], mean squared error + lambda*||w||^2. Infinity is the exact B-only candidate. Choose lambda by equal inner-fold mean MSE, resolving numerical ties toward stronger shrinkage. The use of ridge (rather than R122 Lasso) is declared in advance to make the baseline and joint model exactly nested and numerical fits tractable; do not label the new neural-only fit an exact R122 Lasso replication.

## Outputs and controls
Save per-bin out-of-fold baseline/neural/joint predictions, trial and fold identities, selected neuron identities, fitted baseline/feature maps and coefficients, nested losses, raw/filtered feature digests, source hashes, all failures/warnings.
Primary contrast: MSE(B)-MSE(B+neural), and the same contrast divided by the common session target variance (delta R^2). Average sessions within rat, then rats equally. Report every rat and leave-one-rat-out contrasts. Five rats do not justify population equivalence claims; intervals, if shown, are descriptive.

A held-out mismatched-trial diagnostic freezes fitted maps and exchanges entire neural trajectories among trials sharing bin count, eventual choice, and four chronological blocks, separately within each outer test set. Seeds 1241,1242,1243; report donor identities and moved fraction. This is a pairing-sensitivity diagnostic, not a permutation p-value or randomized neural intervention. For online diagnostic matching only, eventual choice may define strata but is never a predictor.

Software validation: compare partial ridge to an independently constructed augmented least-squares solution; test train/test separation and explicit temporal support; validate exact paired cohort/neuron selection and archive/session digests. No extrapolation from software tests to rat biology.

## Decision discipline
Retain negative gains and exact baseline selections. If a positive average is unstable across rats or weak in size, report it as weak. A positive result only advances finite predictive identification. It does not pass C2 or C3. Do not refit a favorable map or choose a cohort after inspecting held-out scores. Before any C2 experiment, freeze a state/input/time/output law without future-only controls; internal perturbation transport still requires appropriate biological outcomes. Record the absence of laser-on trials separately. No new DOI, release, CI, deployment, or modification of A/B/C.

