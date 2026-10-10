# Reconstruction of the 180 published temporal binding widths

**Status:** Retrospective source-estimator audit for CTD v0.2. This report corrects the interpretation of the earlier reconstruction failure. The frozen v0.1 record remains unchanged. No inferential p value was used to choose reconstruction procedures.

## Main result

The large v0.1 mismatch was principally caused by fixing the additive Gaussian baseline at zero. One four-parameter, unweighted least-squares curve,

\[
q(s)=b+A\exp[-(s-\mu)^2/(2\sigma^2)],
\]

with freely signed baseline, positive height, free center and positive standard deviation, reproduces **176 of 180 published widths within 0.01 ms and 178 within 0.1 ms**. The median absolute difference is 0.0001443 ms. This is a near reconstruction, not exact reproduction to the source table's five decimal places: 77 values are within 0.0001 ms and 152 within 0.001 ms.

| Participant | Task and condition | Published SD (ms) | Reconstructed SD (ms) | Absolute difference (ms) |
|---|---|---:|---:|---:|
| 1 | Simultaneity, 8 Hz | 169.55807 | 196.65136 | 27.09329 |
| 24 | Ownership, 13 Hz | 127.66943 | 120.48444 | 7.18499 |

The other two differences exceeding 0.01 ms are small: participant 27 ownership/sham differs by 0.05479 ms and participant 30 simultaneity/8 Hz by 0.01334 ms. No count, participant identity or condition mapping was changed. No alternative estimator was inserted for the two exceptional values.

In the original conspicuous example, participant 1 ownership/8 Hz, freeing the baseline changes the fitted SD from approximately 399.23 ms to 151.2751 ms, against the released 151.27367 ms. The reconstructed offset is approximately 0.5820 and height 0.4357. A high response baseline can coexist with a narrow Gaussian component; a zero-baseline fit makes its width account for both features.

## Sources and definitions

The source is D'Angelo, Lanfranco, Chancel and Ehrsson (2026), [Nature Communications 17:53](https://doi.org/10.1038/s41467-025-67657-w). Its Methods define the descriptive TBW through a Gaussian SD fitted to yes-response proportions. The inspected Methods and supplement do not specify the complete descriptive curve equation, fitting software, bounds, starting values or stopping tolerances.

The public Experiment 3 file contains 30 participants, six task-by-stimulation curves, seven signed asynchronies (−400, −200, −100, 0, 100, 200, 400 ms) and ten judgments per count cell. Counts occupy B4:AQ33; released widths occupy BL4:BQ33. The latter order is ownership 8 Hz/sham/13 Hz followed by simultaneity 8 Hz/sham/13 Hz.

Publisher Source Data blocks Fig 6a and Fig 6c identify the width task labels, resolving duplicate OSF headers. Fig 6b and Fig 6d identify the count blocks. All analyzed values in these four publisher blocks equal the OSF values. Participant row order is retained; actual trial chronology and block identifiers are unavailable.

| Input | Source | SHA-256 |
|---|---|---|
| Experiment_3.xlsx | [Author download](https://osf.io/download/p5un6/) | d3b2fef22f077788e5299dedb68737d453c09b005d9360bab8dfbe6c35852bc9 |
| NatComm2026_SourceData.xlsx | [Publisher Source Data](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41467-025-67657-w/MediaObjects/41467_2025_67657_MOESM4_ESM.xlsx) | 3202d68439ad502ff95e7a4d59535a4e8ff9072d5c6a76b5aebf7dde90228a82 |

Unchanged portable copies are under inputs/. RECONSTRUCTION_PROVENANCE.json records the URLs, checksums, context sources and runtime.

## Procedure and candidate comparison

RECONSTRUCTION_PLAN.json was saved before these fits. It is a retrospective local audit plan, not a prospective preregistration. The script crosses zero, freely signed and nonnegative baselines with free or zero centers. All candidates minimize ordinary unweighted squared error on the seven proportions.

Asynchronies are scaled by 400 and SD is represented on a log scale. Every curve uses the same three predetermined starting widths. Analytic derivatives are provided. The freely signed-baseline bounds are deliberately broad: baseline [−10,1], height [0,20], center [−500,500] ms and SD [1,4000] ms. Recovered baselines range from approximately −0.9712 to 0.5820, well inside those bounds. The published SD is never used as an initial value.

| Candidate | Median absolute difference (ms) | RMSE (ms) | Number within 0.01 ms |
|---|---:|---:|---:|
| Free baseline, free center | 0.000144 | 2.0892 | 176 |
| Nonnegative baseline, free center | 0.7630 | 25.3734 | 76 |
| Zero baseline, free center | 6.7111 | 49.2970 | 0 |
| Free baseline, zero center | 6.1061 | 81.7037 | 6 |
| Nonnegative baseline, zero center | 6.5465 | 31.2556 | 4 |
| Zero baseline and zero center | 10.4735 | 51.3655 | 1 |

Gaussian SD, the square-root-of-two coefficient in MATLAB gauss1, FWHM, HWHM, twice SD and half SD were explicitly compared. None of the scale conventions improves the direct-SD reconstruction.

Changing free height to free area is a one-to-one nuisance reparameterization, area = height × SD × sqrt(2π), and leaves the optimal SD unchanged under equivalent constraints. Likewise, scaling every ordinate by a common denominator rescales the free offset, height and objective, not the optimal center or SD. These arguments concern unweighted fitting with equivalent constraints; they do not apply to arbitrary weights or changed bounds.

Fixing the center at zero covers the strongest symmetric-centering simplification. Merely changing the coordinate origin while keeping the center free cannot change SD. Collapsing positive and negative delays with changed weights would introduce a different estimator; it was not used to repair the table.

All 720 global permutations of the six released width columns were checked diagnostically. Identity is optimal, with total squared error 785.674 ms²; the next-best order gives 56,400.902 ms². No permutation was applied.

## The two material discrepancies

The unresolved count curves are [4,6,9,9,8,6,2]/10 for participant 1 simultaneity/8 Hz, and [1,3,8,10,8,3,1]/10 for participant 24 ownership/13 Hz.

For each curve, 60 additional predetermined combinations of baseline, center and width were fitted. All converged to the same four-parameter solution. The resulting SD ranges were 196.651324–196.651367 ms and 120.4844374–120.4844383 ms, respectively.

Fixing SD at the source value and profiling offset, height and center provides a conditional numerical diagnosis:

| Curve | Best attained unrestricted SSE | Profiled SSE at source SD | Increase |
|---|---:|---:|---:|
| P1 simultaneity/8 Hz | 0.02049969 | 0.02211676 | 0.00161706 |
| P24 ownership/13 Hz | 0.00609771 | 0.00806470 | 0.00196699 |

The SSE derivatives with respect to SD at those source-width profiles are approximately −0.00015158 and +0.00052558 per ms. Thus the released values are not stationary solutions of the ordinary least-squares profiles examined here. This does not exclude every possible unreported preprocessing rule or software path.

Fixed-zero baselines, fixed-zero centers, fixed peaks, two common observed-variance weighting choices, and a probability-constrained binomial Gaussian were also examined for these two curves. None recovered the source values. These are retained diagnostics, not a mixture of procedures passed off as one pipeline.

The missing original Gaussian fitting implementation and its exact input history prevent a complete reconstruction. Possible causes include different unreported treatment of those curves, numerical termination, or a mismatch between released counts and those originally fitted. The evidence does not select a cause and does not justify an accusation of source-data error.

## Descriptive fits and lawful probabilities

The reconstructed descriptive curves are not automatically Bernoulli probability functions:

- 100 of 180 freely fitted baselines are negative.
- On the seven observed asynchronies, 96 reconstructed curves have at least one value outside [0,1]. Across 1,260 fitted cells, 125 values are below zero and 75 are above one.
- On the whole real stimulus line, 129 curves fail the probability-range condition. With positive height, the global infimum is the baseline and the maximum is baseline plus height.

These are properties of our least-squares reconstructions, not released author nuisance parameters. Negative offsets can be legitimate in a descriptive approximation; this calculation does not show that the source authors treated their curves as legal generative probabilities. It does explain why imposing binomial probability constraints can change the fitted SD.

A bootstrap cannot simply generate binary data from the unconstrained reconstructed curves. A source-anchored uncertainty analysis would require an explicit lawful sampling model and a justified connection to the descriptive estimator. The two remaining discrepancies and unknown trial dependence still matter.

## Code inventory and BCI interpretation

Both the [author data project](https://osf.io/ytga5/) and [author BCI project](https://osf.io/s5p4v/) were re-inventoried through their public APIs. The data project has four listed folders. Its three EEG script ZIPs were downloaded and matched to OSF hashes; all 40 member names and relevant text/code were inspected.

The BCI project contains Master_BCI.m, modelprediction_log_BCI.m, three negative-log-likelihood helpers and a ReadMe. The EEG archives concern data preparation, preprocessing and spectral analysis. No DatatACS1905.xlsx or descriptive TBW Gaussian-fitting program was located in this complete visible inventory. The public Experiment 3 workbook is listed as version 1. This is a statement about inspected materials, not universal absence.

Master_BCI.m refers to a combined source workbook, reading tACS from sheet 1 and EEG from sheet 2. The separate released tACS block matches its declared dimensions and publisher values, but the exact combined workbook bytes were not found.

The main Methods explicitly describe Gaussian fitting to reported proportions. The BCI sensory-uncertainty model instead has one noise SD per stimulation condition shared across tasks plus task-specific priors. That generative noise SD is not automatically one of the six descriptive Gaussian widths. Near-recovering 178 descriptive values directly from the counts supports the direct-fit reading; BCI-generated widths are unnecessary to explain the main pattern. No claim is made that every undiscovered transformation is logically excluded for the two exceptional cases.

The separate audit of BCI information criteria and response-level identifiability is owned by the literature and theory analyses and is not duplicated here.

## Changes required in CTD

The v0.1 explanation of the reconstruction gap needs correction: freeing the baseline explains almost the entire numerical discrepancy. Two material exceptions and smaller solver-level differences remain. The v0.1 zero-baseline binomial sensitivity model is still a separately specified model; it is not a reproduction or error correction of the source descriptive estimator.

Arithmetic on the original released widths and the exact distance formulas are unchanged because those widths were never edited. Their interpretation remains limited: proportional Gaussian width is an added measurement bridge, not a necessary prediction of the original BCI model or direct evidence for a biological clock.

The stronger next analysis belongs at the response level. Explicit lawful models should include clearly stated nuisance asymmetries, and predictive evaluation must use training-only initialization. An exact equivalence between sensory variability and another physical location of variability would show a substantive identification limit without relying on a Gaussian width convention. The parent analysis is pursuing this direction.

## Reproduction and package scope

Run from this directory:

~~~bash
python reconstruct_gaussian_widths.py
python audit_reconstruction_residuals.py
python audit_two_case_metrics.py
~~~

Keep the scripts, inputs, plan, provenance, this report, result CSV/JSON files and public-inventory receipt files. The downloaded EEG archives are context-only and are not required for computation or core redistribution. Preserve source attribution and original rights; do not assign a new license to author code or archives.

No new participants were tested, no author was contacted, no participant was reassigned, and the frozen v0.1 record was not changed.
