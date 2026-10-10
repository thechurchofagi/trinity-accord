# Independent audit of the count-based sensitivity model

**Date:** 10 October 2026.  
**Audited code:** `empirical/fit_count_clock.py`.  
**Status:** The probability-clipping defect found in the initial review has been repaired and independently verified. All final original and bootstrap fit pairs report convergence. The numerical issue is closed for the delivered analysis; the inferential limitations below remain.  
**Action:** Read-only review, finite differences, and recomputation from saved parameters. This audit neither changed the empirical model code nor reran its optimization or bootstrap.

## Initial finding and completed repair

The initial implementation clipped probabilities below $10^{-12}$ while returning derivatives of the unclipped Gaussian response. In narrow admissible curves, the returned objective could therefore be flat where its reported gradient was large. The initial audit and its diagnostic output are preserved under `history/count_audit_before_stable_log_fix/`. Those files describe a superseded run and must not be quoted as the final analysis.

The repaired code computes

$$
\log p=\operatorname{log\_expit}(\alpha)-\tfrac12 z^2
$$

and evaluates the binomial log likelihood from this finite log probability together with `log1p(-p)`. It does not apply the former lower floor. Within the recorded parameter box, the amplitude upper bound keeps $p<1$, and all log probabilities remain finite. Numerical underflow of `exp(logp)` in extreme tails therefore does not erase the corresponding finite negative log-likelihood term or its width derivative.

Independent verification of the repaired implementation found:

- Twelve perturbed fitted vectors, covering six participants under each model, agreed with central finite differences to a maximum absolute gradient error of $3.71\times10^{-8}$.
- Four admissible extreme-curve cases covered both models, positive counts in the tails, and zero counts. Each returned finite loss and gradient, even with 24–36 probabilities numerically underflowing to zero. Maximum scaled width-gradient error was $1.18\times10^{-10}$. For these very large objectives, the maximum absolute error across all derivative entries was approximately $1.00\times10^{-4}$; the maximum error scaled by $1+|g|$ was $5.03\times10^{-6}$.
- Repeating the former narrow-width probe produced analytic derivative $-428133.392076$ and numerical derivative $-428133.392090$, a scaled discrepancy of $3.13\times10^{-11}$. Its loss was finite despite 37 underflowed probabilities. The original objective-gradient inconsistency is absent.

The source-code checksum and full diagnostic values are recorded in `COUNT_MODEL_AUDIT.json`. The empirical agent reran the same 199 seeded bootstrap replicates after the repair and continued unsuccessful optimizer runs with an increased iteration allowance; no scientific null, response family, or parameter domain was changed for the repair.

## Model nesting and final numerical results

The null embeds exactly into the alternative. Applying `null_to_alt` preserves every predicted probability; the maximum difference over the saved null fits is exactly zero. The entire null parameter box maps inside the alternative box: null log widths lie between $-6$ and $5.3$, within the alternative interval $[-6,6]$. Both models retain six amplitudes and six centers per participant. Their width dimensions are four and six, giving 16 versus 18 parameters and a nominal difference of two per participant, or 60 across 30 fixed participants. The recorded parameter bounds are part of the implemented models; the dimension count alone does not establish regular chi-square calibration.

The final saved counts exactly match the original integral array, with shape $30\times2\times3\times7$. Recomputing probabilities and likelihoods from the saved parameter vectors reproduces the delivered values:

| Quantity | Independently checked final value |
|:--|--:|
| Aggregate likelihood-ratio statistic | 73.81345191953241 |
| Minimum participant likelihood-ratio contribution | 0.0077896293 |
| Original participant fit pairs reporting convergence | 30 / 30 |
| Bootstrap replicates | 199 |
| Bootstrap participant fit pairs reporting convergence | 5,970 / 5,970 |
| Unresolved bootstrap convergence flags | 0 |
| Reported numerical continuations in final bootstrap | 10 |
| Simulated statistics at least as large as observed | 20 |
| Plus-one bootstrap tail estimate | $(20+1)/(199+1)=0.105$ |
| Exact 95% binomial interval for simulated tail probability | [0.06247738, 0.15094613] |

All saved original alternative likelihoods are at least as good as their corresponding null likelihoods. All 199 saved bootstrap statistics are finite. The audit checked the recorded bootstrap fit statuses and statistic arithmetic; it did not independently repeat the 5,970 optimization pairs. The Monte Carlo interval quantifies simulation uncertainty in the conditional tail probability, not uncertainty about the scientific model or its assumptions.

## Remaining numerical and inferential qualifications

Twenty-nine of 30 null participant fits and all 30 alternative participant fits reach the amplitude upper bound of 14 in at least one curve. There are 93 such null curves and 99 alternative curves. No final original center or width parameter reaches its stated bound. These common nuisance boundaries preclude treating a dimension count as verification of ordinary chi-square regularity. The 60-df chi-square calculation should remain descriptive; the fitted-null bootstrap provides calibration conditional on the explicitly implemented bounded model.

The maximum projected gradient over original fits is $9.50\times10^{-4}$ for the null and $1.61\times10^{-3}$ for the alternative. The median projected maxima are $1.43\times10^{-4}$ and $2.11\times10^{-4}$. Optimizer success can reflect small relative objective improvement rather than the nominal gradient threshold. The review therefore does not certify global optima of the nonlinear likelihoods. Multiple starts, exact null embedding, and recorded convergence improve numerical transparency but do not replace that limitation. No remaining numerical issue requiring a further full bootstrap run was identified in this audit.

Bootstrap counts are generated independently from binomials conditional on each participant's fitted null parameters. This is neither a participant-resampling bootstrap nor a model of additional within-person dependence, serial effects, changing criteria, or overdispersion. The analysis has 30 participants; 12,600 nominal judgments do not supply 12,600 independently sampled people. The Gaussian response shape, stable probabilities, bounds, and optimization procedure remain analysis assumptions.

The newly fitted width parameters and the source's released width estimates must not be assumed interchangeable. Different fitting procedures can estimate the same underlying parameter when a common response family is correctly specified; under misspecification they can target different limiting values. The source-estimator reconstruction remains incomplete. Consequently the present count-model uncertainty is not transferred to the released-width distances.

## Correct inferential statement

The likelihood comparison tests the full specified participant-specific proportional psychometric-width restriction within the newly fitted independent-binomial Gaussian-response models and their recorded parameter domains. At the conventional .05 threshold it was not rejected by the stated conditional bootstrap. This does not confirm proportionality, establish equivalence, identify a common neural clock, reproduce the original estimator, or validate a UCT experiential bridge.

The scope is stronger than testing whether the group mean of one log-gain contrast vanishes: that mean can be zero by cancellation even when participants violate the proportional model. A joint test of all 60 restrictions remains limited by finite sensitivity, boundary behavior, response-shape assumptions, and the task-to-endpoint bridge. Nonrejection is a statement about this comparison and its assumptions, not proof of a shared physical mechanism.

Machine-readable results are in `COUNT_MODEL_AUDIT.json`; the current generator is `audit_count_model.py`. The superseded clipping and convergence diagnoses are retained solely as review history.
