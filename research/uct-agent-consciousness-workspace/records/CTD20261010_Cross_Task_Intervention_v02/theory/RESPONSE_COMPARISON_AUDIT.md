# Independent audit of the final four-model response comparison

**Result:** the final calculation passes the checks below. This audit only reads stored inputs and fitted parameters; it does not refit models or rerun cross-validation. Its reproduction script is `audit_response_comparison.py` and its numerical record is `RESPONSE_COMPARISON_AUDIT.json`.

## Numerical implementation

The four models use 6, 8, 8, and 10 free parameters per participant for `sigma`, `prior`, `sigma_shift`, and `prior_shift`, respectively. The stimulus-prior variance is fixed at 84,000 ms² and is not counted. The shifted models introduce exactly two task centers per participant, measured internally in 100-ms units and held constant across the three stimulation conditions. They do not introduce a separate center for every task and condition.

An independent implementation using signed SOAs, rather than the fitter's absolute relative SOAs, reproduces probabilities and likelihoods at all **720** stored full-data and training-fold fits. The maximum probability difference is **5.55 × 10⁻¹⁶** and the maximum training or held-out negative-log-likelihood difference is **3.55 × 10⁻¹³**. All stored projected gradients reproduce exactly.

Twenty-eight finite-difference parameter checks include all four models, their canonical and Sobol starts, and broad or nearly saturated response curves. The largest derivative discrepancy, scaled by one plus the numerical derivative magnitude, is **3.34 × 10⁻⁷**. This checks the analytic gradient and the response-center units without mirroring the analytic derivative in the numerical implementation.

The zero-center embedding of the unshifted model reproduces its probabilities exactly in all 60 full-data comparisons. Every shifted full fit has negative log likelihood no greater than its unshifted counterpart. All 300 shifted training-fold fits also satisfy that necessary nesting inequality after the repair described below. These checks do not establish a global optimum; optimizer status and projected gradients remain local numerical diagnostics.

## Partition and fitting isolation

The saved counts exactly match the canonical tidy table for all participant/task/stimulation/SOA combinations. Each cell's ten binary outcomes were partitioned into five artificial pairs. The five held-out counts sum exactly to the original count, every held-out count lies between zero and two, and each training count equals the original count minus the held-out count, with eight training outcomes per cell.

All training-fold fits use their own training counts. The shifted fits receive their own training-fold unshifted estimate embedded with two zero centers, in addition to the canonical and eight Sobol starts. They receive no source fitted parameters, full-data fitted parameters, or parameters selected using held-out scores. The saved additional starts equal those training-only embeddings exactly. The participant-level uncertainty calculation aggregates all five fold scores before treating each participant as one paired unit; it does not treat overlapping folds as independent observations.

This verifies numerical isolation of fitting and scoring. It does not remove the study-level selection of model families after inspection of these data. The result is a retrospective comparison within the declared pipeline, not an external validation or an unbiased correction for all prior analytic choices. Artificial partitions of aggregate counts also do not restore the original order of trials, serial dependence, or independent replication.

## The numerical repair and its closure

The archived first run had three training nesting violations despite zero optimizer quality flags:

| Participant | Fold | Model | Shifted minus unshifted training NLL |
|---|---:|---|---:|
| 16 | 3 | sigma_shift | 51.712174 |
| 21 | 4 | sigma_shift | 50.513156 |
| 22 | 2 | sigma_shift | 99.666405 |

Such a violation certifies an inadequate numerical solution because the shifted family contains the unshifted family. The repair added the training-only embedding as an initial value **uniformly to all 300 shifted training-fold fits**, rather than selecting individual refits from favorable held-out outcomes. The archived partitions, all full-data fits, and all 300 unshifted training fits remain unchanged. The final saved calculation has **zero full-data or training-fold nesting violations** and **zero unresolved optimizer quality flags**.

The pre-repair output remains in `ctd_v02/empirical/results/pre_nested_cv_repair`. The decision and implementation are recorded in `BCI_CV_NESTING_REPAIR_DECISION.json` and `repair_cv_nesting.py`. The initial run is part of the numerical history, not the final evidential result. Reporting only its zero optimizer flags would have missed a substantial, detectable fitting failure.

## Final score contrast and its interpretation

The final fivefold binary log-score contrast, defined as shifted noise-varying minus shifted prior-varying negative log likelihood, is:

| Quantity | Value |
|---|---:|
| Sum across 30 participants | −60.8845945270 |
| Mean participant difference | −2.0294864842 |
| Descriptive paired participant t interval for the mean | [−3.2676238033, −0.7913491652] |

A negative value favors the shifted noise-varying parameterization in this fixed retrospective scoring pipeline. The score is calculated without binomial coefficients so that it is the summed predictive binary log score; the omitted constants are common to the models and do not change their paired comparison.

Several fitted parameters reach imposed bounds. Accordingly, nominal chi-square probabilities attached to absolute deviance are only reference diagnostics. The parameter counts and arithmetic of deviance, AIC, and binary-trial BIC reproduce correctly, but this audit does not turn their regularity assumptions into established properties of these small-cell nonlinear fits.

Relative predictive preference still concerns effective response-model parameters. The exact Gaussian decision-side counterpart reproduces the noise-varying model's marginal probabilities and likelihood for every possible count dataset. Therefore even a reproducible predictive advantage over the released prior-varying family cannot distinguish a sensory anatomical source from that explicitly stated alternative.
