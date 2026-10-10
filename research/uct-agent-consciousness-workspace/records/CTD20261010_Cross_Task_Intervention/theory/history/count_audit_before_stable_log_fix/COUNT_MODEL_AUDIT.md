# Independent audit of the count-based sensitivity model

**Date:** 10 October 2026.  
**Audited code:** `empirical/fit_count_clock.py`.  
**Action:** read-only review plus finite-difference checks; no source code changes and no bootstrap rerun.

## Validated points

- The analytic gradient is correct away from probability-clipping points. Twelve perturbed fitted parameter vectors (six participants in each model) were checked by central finite differences; the largest absolute discrepancy was \(2.94\times10^{-8}\).
- The null model embeds exactly into the alternative. Applying `null_to_alt` preserves every predicted probability, with maximum difference exactly zero in the saved fits. The entire null parameter box maps into the alternative log-width box: null log widths range from \(-6\) to \(5.3\), within \([-6,6]\).
- Per participant, both models contain six amplitudes and six centers. The null has four width parameters and the alternative has six, giving 16 versus 18 parameters and two restrictions. For 30 fixed participants the nominal difference is 60. The alternative deviance's nominal cell-count difference is \(1260-30\times18=720\).
- The saved count array is integral and has shape \(30\times2\times3\times7\). Recomputed aggregate LRT is 73.5722999421. Every participant's fitted alternative likelihood is at least as good as its null likelihood; the smallest participant LRT is positive.
- Bootstrap generation is conditional on each participant's fitted null parameters, with independently generated binomial cell counts. It is not a participant-resampling bootstrap and does not model extra within-person dependence, overdispersion, or serial effects. That conditional model is explicit in the script.

## Numerical issue that should be repaired

`decode` clips probabilities below \(10^{-12}\), but `lossgrad` differentiates the unclipped response formula. Consequently the returned gradient is not the gradient of the returned loss in clipped regions. An admissible narrow-width example gives an analytic log-width derivative of about \(-428134\), while the finite-difference derivative of the clipped loss is exactly zero.

The final saved fits contain only one clipped null cell and two clipped alternative cells, so the issue need not materially affect the original fit. It can nevertheless affect optimization paths or bootstrap fits. A stable calculation with `logp = log_expit(amplitude_parameter) - 0.5*z*z`, evaluating the likelihood from `logp` and `log(1-exp(logp))`, avoids lower clipping while retaining the correct derivative. Setting clipped-region derivatives to zero would instead make the existing clipped objective internally consistent, but leaves artificial flat regions. The stable-log implementation is preferable.

## Boundary and convergence limitations

Every one of the 30 null participant fits and 29 of 30 alternative participant fits has at least one amplitude parameter at the imposed upper bound of 14. No final center or width parameter hits its stated bound. These common nuisance boundaries mean the 60-df chi-square reference should remain a reference calculation rather than an assertion that all regularity conditions hold. The fitted-null parametric bootstrap is the better finite-model calibration, subject to optimization and model-fit qualifications.

The saved 199-replicate bootstrap has 18 replicates containing one unconfirmed optimizer convergence each: 5,952 of 5,970 participant fit pairs were marked converged. Of those 18 replicates, two exceed the observed LRT. There are 19 exceedances among the fully converged replicates. If the 18 flagged values were treated as completely unknown, the add-one Monte Carlo p-value would range from 0.10 to 0.19. Thus even that worst-case classification does not change a 0.05-level nonrejection, but the reported 0.11 should not silently include unresolved optimization failures. Targeted regeneration and refitting of those 18 replicates is sufficient; a full bootstrap rerun is unnecessary for this specific problem.

Flagged zero-based replicate indices: 2, 5, 17, 39, 46, 49, 55, 96, 112, 124, 125, 138, 170, 179, 183, 195, 196, 197.

The optimizer usually stops on relative objective improvement rather than the gradient threshold. Maximum projected gradients among saved fits are approximately \(4.16\times10^{-4}\) for the null and \(2.13\times10^{-3}\) for the alternative. The review does not certify global optima of these nonlinear likelihoods. Multistart fits, exact null embedding, and transparent convergence records support the numerical result but do not replace that qualification.

## Correct inferential wording

The 60-restriction likelihood comparison tests the specified participant-specific multiplicative psychometric-width bridge within the newly fitted independent-binomial Gaussian-response model. Nonrejection means these counts do not reject that complete constrained model against its stated width-relaxed alternative under the analysis assumptions. It does not confirm proportionality, establish equivalence, identify a common neural clock, reproduce the original study's estimator, or validate a UCT experiential bridge.

This is stronger in scope than checking whether the group mean of one log-ratio contrast differs from zero: that single mean is only one necessary implication and can vanish by cancellation when individuals violate the model. The full likelihood test still has finite sensitivity, nuisance boundaries, curve-shape assumptions, and possible response-criterion limitations. Failure to reject is therefore an informative boundary on the current evidence, not proof of a shared mechanism.

All machine-readable details are in `COUNT_MODEL_AUDIT.json`, generated by `audit_count_model.py`.
