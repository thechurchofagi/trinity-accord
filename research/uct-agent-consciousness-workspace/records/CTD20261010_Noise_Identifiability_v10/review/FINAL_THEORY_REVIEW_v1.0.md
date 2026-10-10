# Final mathematical and inferential review: CTD v1.0.0

**Review date:** 10 October 2026.  
**Reviewer role:** AI-assisted internal theoretical review; not external peer review.  
**Disposition:** No unresolved mathematical error found in the reviewed claims after the four scope/unit corrections below. The finite-sample implementation correction is closed and its execution provenance has been updated. This receipt is not approval of the unvalidated human measurement assumptions or a claim of new general statistical mathematics.

## Reviewed version and scope

The complete manuscript was read, with detailed re-derivation of Proposition 1, Theorems 2–4, Sections 6.1–6.4, and Appendix B. Particular attention was given to the new Section 6.4 and Appendix B.5. The review also read `finite_sample/PROOF.md`, the executable confidence-set module, the fixed operating-characteristic plan and runner, its final summary, and the module's numerical-check receipt.

Reviewed manuscript: `manuscript/noise-identifiability-bodily-judgments-v1.0.0.md`. Its SHA256 immediately after the four review corrections is:

`5dca835b8e39078cc2f1d1a038fd6cf77d2885cc8677b757d6569aef41ad2785`.

Later insertion of release identifiers or layout changes must be tracked separately. This receipt applies to the scientific text reviewed here, not to an unseen later substantive revision.

## Mathematical chain and scientific interpretation

**Proposition 1 — exact marginal counterpart.** Gaussian convolution depends on the total variance `a+b`; retaining every halfwidth, center, and lapse therefore reproduces the full marginal probability law, not just a fitted summary. The manuscript explicitly retains the condition-dependent threshold policy and does not claim that changing criterion jitter alone with all thresholds fixed reproduces the source family. The fixed construction `a_i = .5 min_f v_if` adds no independently fitted prediction parameter. This is an application of an inherited sensory/criterion-noise ambiguity.

**Theorem 2 — prospective population inverse.** Positive finite halfwidths, known positive effective variances, a calibrated common center, one same internal sensory draw, independent Gaussian criteria, and independent known lapse processes imply a strictly increasing centered rectangle for nonnegative total correlation. The four-corner derivative, endpoint continuity, and positive affine lapse coefficient establish the unique inverse. The manuscript distinguishes one additional population probability from one physical trial. The degree-of-freedom minimality claim concerns an observation law with fixed marginals, not a minimum sample size or an optimal procedure. The original separate-block dataset supplies no paired observation, and its failed centering restriction does not calibrate the proposed center.

**Theorem 3 — bounded criterion correlation.** Joint Gaussianity of the criterion vector and its independence from the sensory draw are retained explicitly. The negative total-covariance branch is included correctly: any admissible negative branch also permits the positive branch because `|R-a| <= R+a`. The covariance inequality defines zero-criterion-variance cases without an undefined correlation division. Gaussian positive-semidefinite constructions attain every point in the stated set. Equal-variance endpoints, the kappa=1 case, and the unequal-variance quadratic agree with the proof module. The single paired statistic is not allowed to estimate an unconstrained criterion correlation and shared sensory variance simultaneously.

**Weak identification.** The expansion has coefficient `2 r_O r_S phi(r_O) phi(r_S)` multiplying squared total correlation. Under independent criteria, this gives squared dependence on the shared variance and the `n^(-1/4)` local separation rate. The KL derivation in Appendix B is consistent with the four fixed-marginal cell changes. The off-center derivative restores first-order local sensitivity under a shared calibrated shift, while the manuscript correctly avoids claiming global monotonicity there. None of these facts validates the required same-sample or lapse premises.

**Theorem 4 — finite-sample projection.** The closed Clopper–Pearson interval covers the true binomial probability with at least the nominal probability. On that one event, its model preimage contains the entire true-calibration population identified set, not merely one selected value. The equal-variance union endpoints are correct. Disjointness from the full attainable probability range produces an empty set, not a clipped boundary estimate. Its probability is at most alpha under the combined valid family. The finite-sample claim is neither a posterior probability for a mechanism nor a shortest-confidence-set result. The full four-cell paired likelihood is not claimed to be exhausted by the paired-yes count.

**Calibration uncertainty.** Appendix B.5 correctly takes the union over the entire calibration set. Valid individual guarantees imply coverage at least `1-alpha-gamma` by a union bound without requiring independence between those two events. Its `.025 + .025` example targets 95%; the fixed-calibration enumeration uses gamma zero. Plug-in nuisance estimates are not silently treated as known. Exact finite calibration sets and continuous uncertainty only in kappa are separated from an arbitrary continuous multivariate domain; no sampled grid is called a certified envelope. The analytic continuous-kappa union is attained at the upper bound because admissible covariance sets are nested.

**Degeneracies and numerical language.** Zero halfwidth and unit lapse produce a constant paired readout under the stated independent-lapse law. The correct outcomes are the full physical domain or the empty set. The no-observation case is full domain. The manuscript correctly separates real-arithmetic coverage from double-precision evaluation and does not claim interval-arithmetic certification. The proposed quantity remains a stipulated variance component, not a measured experiential scale, anatomical mediator, or UCT-specific prediction.

## Four manuscript corrections applied with the parent's agreement

1. The abstract now states second-order sensitivity near **zero total correlation**, instead of making that statement unconditionally near zero shared variance. With nonzero criterion covariance, zero sensory variance need not be zero total correlation.
2. Section 6.3 now starts “Under independent criteria, the unique centered inverse is weak near independence,” explicitly locating its variance-rate conclusion in Theorem 2's contract.
3. Section 6.2's kappa=1 interval is explicitly an interval for `a/v`.
4. Section 6.4's kappa=1 interval is explicitly an interval for `C/v`.

No empirical result, theorem formula, source-model fit, or significance calculation was changed by these edits. Before-edit manuscript SHA256 was `e678898800f02b2b283418e659f42d3c789a52683724a2ed9dc3dceaebdccf03`.

## Numerical correction and closed verification

An extended unequal-variance test exposed a full-domain rounding/status issue: at `v_O=.5, v_S=.6, kappa=1` and probability interval `[0,1]`, the first implementation returned the upper endpoint `.4999999999999996` and status `informative`. The mathematical set is exactly `[0,.5]`. Module version 1.0.1 now returns the physical domain directly whenever the input probability interval contains the entire attainable range. This is an analytic shortcut and endpoint correction, not a change to the inference model. The prior module and receipt remain under `finite_sample/history/before_full_domain_guard/`, with the reason documented in `finite_sample/NUMERICAL_CORRECTION_NOTE.md`.

The final module SHA256 is:

`cefe69f6fec5b26fb8935e2fa1e0c9db7e9b47ac003b4c16a9412ccae02f4272`.

`finite_sample/CONFIDENCE_SET_CHECKS.json` reports:

- 336 Gaussian rectangle evaluations compared with independent conditional-normal quadrature; maximum absolute difference `4.44e-16`.
- 228 Clopper–Pearson endpoint comparisons with SciPy's separate root-inversion routine; maximum difference `4.98e-13`.
- 279 direct finite-binomial coverage checks, all at or above their nominal levels.
- 42 equal- and unequal-variance calibrations; analytic global-correlation maxima differ from independent bounded maximization by at most `1.41e-13`.
- 75,990 decisive direct candidate-probability-intersection checks; 366 boundary checks too close to probability saturation or the declared floating tolerance were explicitly not counted as decisive. These do not serve as a substitute for the real-arithmetic proof.
- Seven degenerate-readout cases, exact no-observation full-domain checks for all 42 calibrations, signed-covariance equivalence, a finite calibration union preserving two disjoint intervals, and the continuous-kappa endpoint construction.

The empirical owner then reran only the fixed 480-case binomial enumeration against the final module. `finite_sample/EXECUTION_PROVENANCE.json` records that final hash, unchanged plan/code during execution, and zero original fits, symmetry simulations, or human observations added. The earlier finite-sample execution is preserved under `finite_sample/history/pre_module_1_0_1_rerun/`.

The final scenario counts are 240 valid, 120 wrong-independence-bound controls, 60 independent-sensory-resampling controls, and 60 shared-lapse-and-guess controls. Valid true-variance coverage is at least `0.9502345620800363`; coverage of the entire valid population identified set is at least `0.9501514694716469`. All 163,320 fixed-candidate probability-intersection checks pass. The main text's four reported mean widths, rounded to `0.9273`, `0.3772`, `0.9395`, and `0.4904`, match the final summary. Binomial mass-sum error is at most `1.78e-15` before its explicitly recorded normalization.

The negative controls are interpreted correctly: binomial probability coverage can remain valid while target inclusion under a false mechanism contract fails. In particular, the independent-resampling control evaluates a per-task variance, not an actually shared component, and is separately labeled. No power recommendation or human-calibration success is inferred from the synthetic grid.

## Release-facing conclusion

The finite-sample addition closes a real inferential gap in the existing conditional theorem: the new readout now has an explicit uncertainty procedure rather than only a noiseless inverse. The combined paper remains a bounded methods contribution and retrospective audit. Gaussian noise addition, Plackett differentiation, Clopper–Pearson intervals, projection, and the union bound are credited as inherited tools. The missing real paired experiment, external calibration, complete physiological interpretation, and experiential bridge remain missing; the manuscript does not conceal them behind its mathematical coverage guarantee.


## Narrow addendum: final frozen manuscript

**Date:** 10 October 2026. **Scope:** final-byte verification of one Figure 4 caption clarification. The earlier review and its manuscript snapshot above are retained unchanged.

The final manuscript was read back from `manuscript/noise-identifiability-bodily-judgments-v1.0.0.md` and has **61,065 bytes**, SHA256:

`6bc9dad5add7612735358236c9b7533cc8f54f6aa535443ee2d9e9f5d219c734`.

The only change from the manuscript snapshot reviewed above is the Figure 4 caption phrase `is 0.024862.` becoming `is less than 0.024862.`. The final phrase occurs exactly once. Reversing that single substitution in memory yields exactly **61,055 bytes** and SHA256 `5dca835b8e39078cc2f1d1a038fd6cf77d2885cc8677b757d6569aef41ad2785`, reproducing the previously reviewed snapshot byte for byte. No manuscript file was changed during this verification.

The revised caption expresses the reported valid-grid maximum empty-set probability as an upper bound. It introduces no change to the model, theorem, confidence construction, computed data, or inferential scope. The mathematical review disposition above therefore extends to this final frozen scientific text. This addendum performs no new mathematical derivation, numerical rerun, or external write, and does not imply external peer review.
