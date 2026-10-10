# Secondary analysis of intervention effects on body ownership and simultaneity

Version: 1.0 completed empirical appendix for the UCT continuation paper. Analysis date: 10 October 2026.

## Main finding and evidential status

The public data support a useful, limited result: the average proportional effect of 8 Hz versus 13 Hz stimulation on the two released psychometric widths is similar, while individual point estimates need different amounts of adjustment to satisfy an exact common multiplicative scale. An independently specified analysis of the released response counts does not reject its common-gain constraint at the conventional 5% level. Neither result identifies a unique internal information pathway, proves a common biological clock, or distinguishes UCT from major consciousness theories.

This work actually downloaded and analyzed author-released human experimental data. It did not collect a new human experiment. The response-count file contains counts pooled over repeated trials, not ordered trial-level records. The released widths and the counts are treated as two separate analysis layers because our ordinary Gaussian refits do not uniformly reproduce the released widths.

The new contribution appropriate for a methods paper is the explicit comparison of three claims: a correlated treatment effect, an exact shared multiplicative scale, and a more permissive common ordering through task-specific monotone response functions. The exact distance from the released estimates to each model produces a concrete target for future independent error calibration. It is not itself a calibrated error estimate.

## 1. Sources, access, and scope

### Main experiment

D'Angelo and colleagues, *Parietal alpha frequency shapes own-body perception by modulating temporal integration of bodily signals*, Nature Communications 17, 53 (2026), DOI [10.1038/s41467-025-67657-w](https://doi.org/10.1038/s41467-025-67657-w).

The analyzed Experiment 3 includes 30 participants who passed a rubber-hand-illusion screening procedure, from 37 recruited. Each participant completed body-ownership and visuotactile-simultaneity judgments under 8 Hz, sham, and 13 Hz tACS, with seven asynchronies. Stimulation order was pseudorandomized. This is a real intervention on stimulation condition, with report-based operational endpoints. It does not independently establish the particular neural mediator through which the treatment operates. See the [primary article](https://www.nature.com/articles/s41467-025-67657-w) and its [supplement](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41467-025-67657-w/MediaObjects/41467_2025_67657_MOESM1_ESM.pdf).

Author data: [OSF ytga5](https://osf.io/ytga5/). Author modeling code: [OSF s5p4v](https://osf.io/s5p4v/).

Core public inputs:

| File | Content and origin |
|---|---|
| `Experiment_3.xlsx` | Author OSF file [p5un6](https://osf.io/download/p5un6/): 30 participant rows with response counts, d-prime quantities, and six released TBWs. |
| `NatComm2026_SourceData.xlsx` | Official [Nature Source Data workbook](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41467-025-67657-w/MediaObjects/41467_2025_67657_MOESM4_ESM.xlsx). |

The author script [Master_BCI.m](https://osf.io/download/pnmsx/) was inspected read-only to verify data ranges, task order, and the denominator of ten judgments per count cell. It is externally cited, is not required to run the present independent scripts, and is not redistributed or relicensed in the core package. The computational-model workbook and unrelated supporting studies are also outside this core package.

The main OSF workbook has SHA256 `d3b2fef22f077788e5299dedb68737d453c09b005d9360bab8dfbe6c35852bc9`, identical to the hash supplied by the OSF file API. Complete download URLs, sizes, and hashes are in `DATA_PROVENANCE.json`.

The article states a Creative Commons Attribution 4.0 license. The official Source Data file accompanies that article. The downloaded OSF project metadata did not expose a separate node license. For a public reproduction package, prefer the official Source Data, the present independent scripts, derived tables, and source URLs. The author MATLAB code should be cited and linked rather than assigned a new license or silently included under a blanket license for our code. No author content was modified.

## 2. Data validation and a consequential unresolved link

The Nature experiment has 30 rows, two tasks, three stimulation conditions, and seven asynchronies: 1,260 count cells, each with ten nominal trials, corresponding to 12,600 binary judgments before pooling. Every count is an integer between zero and ten. No row or cell is missing in the analyzed ranges. The author `Master_BCI.m` reads `B4:AQ33`, declares the first 21 columns ownership and the next 21 simultaneity, and sets `tACS_n_trials=10`.

The last three width headers in the OSF workbook repeat the names used for ownership. This was resolved by an independent official source: Nature Source Data sheets `Fig 6a` and `Fig 6c` explicitly distinguish ownership and simultaneity. Their six width columns are exactly equal to the corresponding OSF values, row by row. Sheets `Fig 6b` and `Fig 6d` likewise match all count values exactly. `results/source_data_crosscheck.json` records these four exact comparisons. The raw headers remain preserved in `results/published_tbw_tidy.csv`; the source workbook was not edited.

The released width means were reproduced:

| Task | 8 Hz | Sham | 13 Hz |
|---|---:|---:|---:|
| Body ownership | 208.2555 ms | 164.9820 ms | 137.9282 ms |
| Simultaneity | 156.3052 ms | 125.3151 ms | 101.4154 ms |

However, fitting an ordinary three-parameter Gaussian curve to the corresponding count proportions did not reproduce all released widths. For example, the first ownership/8 Hz response sequence is `[7, 8, 9, 10, 10, 7, 5]` out of ten. Our ordinary Gaussian fit has an SD of approximately 399.23 ms, whereas the released width is 151.27 ms. Across rows, the correlations between these refits and the released widths range from approximately 0.366 to 0.992 across the six conditions. The disagreement is also present when the official Source Data is used, because both public workbooks agree exactly.

This finding does not establish an error by the source authors. It establishes that the link between this particular refitting procedure and the released estimates has not been reproduced. Differences in the exact estimator, preprocessing, fitting constraints, or other unreported-to-us details remain unresolved. The downloaded author scripts implement the BCI model rather than the Gaussian estimator needed to resolve this link. A diagnostic numerical row assignment was computed only as a check and was not used to change participant identities or repair data.

Consequently, uncertainty estimated from a newly fitted count model is not attached to the published TBW table. Both are retained and identified separately below.

## 3. What is inherited and what is newly tested

The source authors already established across-task correlations of the stimulation effects and compared BCI models in which stimulation changes sensory uncertainty versus common-cause priors. Reproducing those ideas is not the present originality claim. From the released widths, we reproduced the reported across-task correlations of the 8 Hz/sham and sham/13 Hz differences: r = 0.727800 and r = 0.547145, respectively. The source paper's original BCI comparison must receive its own credit.

We instead specify a stronger operational bridge:

\[
W_{itf}=c_{it}\tau_{if},\qquad c_{it}>0,\quad\tau_{if}>0.
\]

Here the width `W` is the psychometric quantity, task is `t`, and stimulation condition is `f`. The task multiplier must remain fixed across stimulation conditions. For an individual with two tasks and three conditions, the six free log-widths are restricted to four parameters. There are two independent equality constraints. Equivalently,

\[
D_{if}=\log W_{i,O,f}-\log W_{i,S,f}
\]

must be constant across all three frequencies. An across-task correlation, even a large one, does not imply this equality.

The constraint is deliberately stronger than the source authors' common-sensory-uncertainty BCI model. That model has a nonlinear observation rule with task-specific prior parameters; a shared uncertainty parameter does not automatically imply a fixed ratio between Gaussian psychometric widths. Testing the present constraint therefore cannot by itself refute that BCI model, a more general common clock, or a consciousness theory.

`analysis_plan.json` was saved before the local inferential calculations. This is a retrospective secondary analysis, not a prospectively preregistered experiment. The exact-distance and error-budget extensions were added afterward at the direction of the theory analysis and are explicitly exploratory.

## 4. Released-estimate analysis

The primary contrast specified in the retrospective local plan was

\[
\Delta_i=\log\frac{W_{i,O,8}}{W_{i,O,13}}-\log\frac{W_{i,S,8}}{W_{i,S,13}}.
\]

For 30 participants:

| Quantity | Result |
|---|---:|
| Mean log-gain difference | −0.014563 |
| SD across participants | 0.210960 |
| 95% t confidence interval | [−0.093337, 0.064211] |
| t statistic and degrees of freedom | t(29) = −0.378104 |
| Two-sided p | 0.708107 |
| Bootstrap 95% CI of population mean | [−0.089892, 0.059244] |
| Geometric ratio of task gains | 0.985543 |
| 95% interval on that ratio | [0.910887, 1.066317] |

The two secondary log contrasts, 8 Hz/sham and 13 Hz/sham, had Holm-adjusted p values of 0.610673. A TOST sensitivity analysis with an illustrative symmetric log margin of ±log(1.10) gave p = 0.022438. This supports only a population-mean equivalence statement at that chosen operational margin. The 10% margin is not an independently established perceptual or phenomenological threshold. It must not be described as a calibrated resolution of experience.

Failure to reject a population mean of zero does not establish individual equality. Fourteen individual primary contrasts were positive and sixteen were negative. Opposing individual discrepancies can cancel in a population average. The point estimates also have unavailable fitting uncertainty, and the quoted population confidence interval does not supply that missing participant-level uncertainty.

## 5. Exact distances to two operational models

### Strict multiplicative model

For each participant, the exact minimum uniform log-cell adjustment required to fit the strict multiplicative model is

\[
\epsilon_i^{\mathrm{clock}}=\frac{\max_f D_{if}-\min_f D_{if}}{4}.
\]

An error tolerance `epsilon` corresponds to allowing each width to change by a factor between `exp(-epsilon)` and `exp(epsilon)`. Reporting `100[exp(epsilon)-1]` expresses the upward multiplicative tolerance; the corresponding downward percentage is different and is not silently equated to it.

On the released estimates, the upward tolerance has median 4.1982%, interquartile range 1.9134%–6.0461%, and maximum 13.3913%. Twenty-seven of the thirty rows can be brought onto this model using a uniform log-cell tolerance no larger than log(1.10).

These are geometric distances of released estimates, not estimates of actual measurement error, and not confidence statements about an individual's true mechanism.

### Common ordering with task-specific monotone response functions

A less restrictive model permits each task its own increasing response function of a common latent variable. With only three stimulation conditions, this requires a compatible common order. For each of the six candidate frequency orders, the minimum uniform log-cell adjustment is half the largest positive inversion within either task. Taking the minimum over these six orders gives `epsilon_monotone`.

Twenty-five participants already have the same stimulation ranking in both released task estimates, so this weaker distance is zero. The other five rows require upward tolerances of approximately 0.7296%, 4.6901%, 0.8260%, 0.0462%, and 1.5157%. The maximum is 4.6901%. This contrast illustrates why departing from a proportional-width model is insufficient to reject a common source with task-specific nonlinear mappings.

The exact distance formula concerns the closure with weak monotonicity. A zero distance at incompatible task ties is an infimum statement rather than an exact witness of strictly increasing task maps; matching ties can be represented by a tied latent input. There are no width ties relevant to the zero-distance rows here.

### Hypothetical calibration budgets

`results/hypothetical_lognormal_calibration_budgets.csv` gives a sensitivity grid for externally supplied, centered Gaussian log-error SDs. It supplies both an exact independent-normal maximum bound and a Bonferroni bound requiring only normal marginals. Both six-cell individual coverage and 180-cell family coverage are distinguished. These SDs were not estimated from the public experiment.

For illustration, a log-error SD of 0.01 with Bonferroni 95% coverage across all 180 cells gives a log tolerance of 0.036352, or an upward factor of 3.7021%. Seventeen released rows lie farther than this from the strict proportional model and one lies farther from the monotone model. At log SD 0.02, the corresponding counts are four and zero. These are conditional planning calculations. They become empirical exclusion statements only if an appropriate independent calibration justifies the assumed error distribution, scale, bias control, and coverage scope.

## 6. Independent count-level sensitivity model

To assess one explicit form of measurement noise without transferring errors to the released widths, a separate binomial Gaussian-response model was fitted directly to the 1,260 counts:

\[
Y_{itfs}\sim\operatorname{Binomial}\left(10,
A_{itf}\exp\left[-\frac{1}{2}\left(\frac{s-\mu_{itf}}{w_{itf}}\right)^2\right]\right).
\]

Both models allow six task-by-condition amplitudes and six centers per individual. The null has four log-width parameters, two task baselines plus two shared condition gains relative to sham, for 16 parameters per person. The alternative has six independent log-widths, for 18 parameters. Thus the comparison adds two degrees of freedom per participant, or 60 across 30 participants.

All 30 original null and alternative fits converged. The alternative was explicitly initialized from the nested null if needed to enforce the likelihood ordering. The Gaussian likelihood is evaluated in stable log space, avoiding an inconsistent probability-floor gradient at extreme tails. Numerical audit and the bootstrap use the same model and hypotheses; numerical corrections were not selected according to significance.

| Quantity | Result |
|---|---:|
| Null negative log likelihood | 4670.1145 |
| Alternative negative log likelihood | 4633.2078 |
| Likelihood-ratio statistic | 73.8135 |
| Nominal chi-square reference | 60 df, p ≈ 0.10837 |
| Alternative deviance versus saturated count probabilities | 696.2130 |
| Nominal alternative deviance reference | 720 df, p ≈ 0.73114 |

The chi-square distributions are reference calculations, not an asserted finite-sample calibration. The optimization reports the best attained objectives among the specified starts, not a proof of global optima. At least one amplitude reaches the upper numerical bound in 29 null fits and all 30 alternative fits (93 and 99 curves, respectively). There are many individual nuisance parameters, and some Gaussian curve parameters can be weakly identified. These facts limit the usual regular asymptotic argument. The parameter-level counts are retained in `results/count_model_boundary_diagnostics.json`.

A parametric bootstrap generates all 30 participants from the fitted null, then refits both models for every replicate. There are 199 replicates using a fixed seed. The final reported p and convergence status are recorded in `results/count_model_summary.json`. The completed numerical check gives 20 bootstrap statistics at least as large as the observed statistic, a plus-one p value of 0.105. The exact binomial interval for Monte Carlo uncertainty in the underlying simulated tail probability is approximately [0.06248, 0.15095]. All 5,970 participant-level null/alternative fit pairs converged after ten automatic numerical continuations. This interval describes finite simulation error, not the uncertainty of the scientific model or its assumptions.

The nominal 12,600 trials are conditionally independent only by model assumption. Trial order, block-specific counts, and session-level dependence were not released in this file. Unmodeled dependence or overdispersion can change the calibration. A bootstrap conditional on a fitted Gaussian/binomial model is not a distribution-free test of a biological clock.

The present count-model mean widths differ from the released-width means. This difference is retained rather than hidden. It provides a second reason to avoid describing the count analysis as uncertainty correction of the source authors' TBW estimates.

## 7. Implications for a paper and for the next experiment

The defensible paper claim is methodological: treatment correlations, exact cross-task transport constraints, and tolerance-calibrated exclusions are different levels of evidence. This dataset offers a genuine human-intervention case in which those levels can be calculated and kept separate. Its released estimates show approximate population proportionality, heterogeneous individual discrepancies, and substantially smaller distances to a permissive monotone model. The independent count model leaves the strict shared-gain constraint statistically unresolved under its assumptions.

No UCT-versus-GNW/IIT/HOT conclusion follows. None of those broad theories was independently committed here to a unique numerical gain ratio, an exclusive neural consumer, or a unique report-to-experience map. The common signal assumed by a statistical model is not automatically the same physical carrier required by a source-use theorem. Likewise, an effect of tACS on reports does not by itself establish mediation by a measured alpha signal.

A concrete next study should release ordered repeated trials, block identifiers, session identifiers, and fitting code; calibrate width-estimation error and drift independently; precommit the cross-task bridge; and hold out a stimulation condition or task for prediction. A source-use experiment would additionally need an intervention and measurement design that validates the particular carrier, recipient, causal role, and timing. The present existing data do not replace those requirements.

The proposed title should describe shared psychometric scales, calibration, or intervention-based model comparison. It should not advertise a demonstrated neural route, an experimentally verified consciousness mechanism, or a refutation of broad consciousness theories.

## 8. Reproduction and output inventory

Runtime used for the calculations: the installed primary Python runtime with NumPy, SciPy, pandas, and the Excel-reading dependency. The original workbooks are read-only throughout. Paths in the scripts resolve relative to their script directory.

Run, in order:

```bash
python check_gaussian_alignment.py
python analyze_published_widths.py
python compute_calibration_budgets.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python fit_count_clock.py --bootstrap 199 --workers 4
python make_empirical_figure.py
python reproduce_existing_checks.py
```

The BLAS thread settings and spawned worker context prevent nested native-thread oversubscription during the bootstrap. They do not change the statistical model.

Main outputs:

| Output | Purpose |
|---|---|
| `results/published_widths_summary.json` | Primary and secondary released-estimate results, inherited correlations, and limits. |
| `results/published_tbw_tidy.csv` | Six released widths per person, with task mapping and original headers retained. |
| `results/aggregate_counts_tidy.csv` | Author count observations in a flat table, with explicit denominator. |
| `results/individual_clock_and_monotone_distances.csv` | Exact exploratory model distances for each released row. |
| `results/hypothetical_lognormal_calibration_budgets.csv` | Conditional error-budget grid, explicitly not measured calibration. |
| `results/count_model_plan.json` | Independent secondary model, bounds, parameter counts, and bootstrap design. |
| `results/count_model_summary.json` | Final count-model fit, bootstrap, convergence, and Monte Carlo results. |
| `results/count_model_fits.npz` | Fitted parameters, probabilities, and count input for reproducibility. |
| `results/count_model_bootstrap.npz` | Bootstrap likelihood-ratio statistics. |
| `DATA_PROVENANCE.json` | Download origins and integrity evidence. |

The complete deliverable should preserve the distinct roles of source data, analysis plans, our scripts, derived results, and the unresolved estimator link. This report is suitable as an empirical appendix or detailed research handoff; the manuscript should foreground the formal contribution and use the data as a carefully delimited application.

## Figure

`results/empirical_shared_scale.pdf` is a vector figure, with corresponding PNG and SVG versions. Panel A plots paired released 8 Hz/13 Hz log gains against the equality line. Panel B shows exact adjustment distances of the released point estimates, not measured uncertainty. Panel C shows the independent count model's fitted-null bootstrap. These three panels deliberately do not present the count bootstrap as an error bar on the released widths.
