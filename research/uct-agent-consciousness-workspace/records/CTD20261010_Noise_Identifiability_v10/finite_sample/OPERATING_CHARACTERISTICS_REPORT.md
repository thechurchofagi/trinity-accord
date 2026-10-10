# Finite-sample operating characteristics of the paired-readout confidence set

**Status:** completed fixed numerical study, 10 October 2026. The analysis enumerates the complete finite binomial law. It contains no new human observations, no Monte Carlo draws, and no refitting of the source experiment.

## 1. Main findings

All **240 valid scenarios** in the prespecified grid meet the nominal 95% coverage requirement. The smallest coverage of the actual shared sensory variance is **0.9502345621**. The smallest probability of containing the **entire population identified set** is **0.9501514695**. These are finite sums evaluated numerically, rather than estimates from simulated repetitions.

Coverage does not imply a narrow or practically decisive set. With the total marginal variance normalized to one, the fixed-grid average confidence-set width for independent criteria is **0.92734 at N = 64** and **0.37723 at N = 4096**. Allowing a criterion-correlation bound of 0.2 gives corresponding widths **0.93953** and **0.49036**. These averages describe the specified finite grid with equal case weights; they are not averages over a human population or a power analysis.

The negative controls expose a separate issue. The binomial probability interval remains valid in all 480 scenarios, but its physical interpretation can fail when the consumer or lapse contract is false. With an incorrect independence bound, the generating shared variance has inclusion probability as low as **0.69392**. With a shared lapse indicator and shared guess, inclusion can fall to **2.22 × 10⁻¹²**, while the mapped set is empty with probability **0.9999999972**. Independent sensory resampling is reported separately: the evaluated target is the per-task sensory variance, which is not the actual shared component.

The contribution is a concrete implementation and audit of a classical confidence construction for the paper's observation contract. It is not a new general confidence-interval method. Clopper and Pearson introduced the underlying binomial interval [1]; the accompanying PROOF.md establishes the model-specific projection and its limitations.

## 2. Fixed design and scope

ANALYSIS_PLAN.json was saved before the operating-characteristic calculations. Its SHA256 is:

~~~text
7d2450ca98bf07de5732ad7c6b7c1327920619279204a0b1574d9984cefda1d3
~~~

This is a dated execution plan within retrospective methods development, not an external preregistration. The grid was not changed after seeing its results.

Both task variables have effective marginal variance one and center zero. The nonlapse response is a yes when the Gaussian decision variable lies within the task's interval. Three fixed profiles cover two threshold combinations and two lapse levels:

| Profile | Ownership halfwidth | Simultaneity halfwidth | Known marginal lapse |
|:--|--:|--:|--:|
| Asymmetric, low lapse | 0.8 | 1.3 | 0.05 |
| Unequal window, low lapse | 1.5 | 0.6 | 0.05 |
| Asymmetric, high lapse | 0.8 | 1.3 | 0.20 |

Every profile uses N = 64, 256, 1024, or 4096 independent paired trials, and generating per-task sensory variance a = 0, 0.1, 0.3, 0.6, or 0.9. No source parameter example was selected. The numerical values are dimensionless model specifications, not estimated human parameters.

Under the valid common-draw model, E has variance a and is shared by both reports. Criterion jitters have marginal variances 1−a and covariance c, independently of E. Each decision variable is E minus its criterion jitter, so its total variance is one and their total covariance is R = a+c. The bound is |c| ≤ κ(1−a). Independent lapse indicators and independent fair guesses occur with the known marginal rate. Different paired trials are independent.

The valid grid contains c = 0 when κ = 0, and c = −0.2(1−a), 0, or +0.2(1−a) when κ = 0.2. This gives 240 valid scenarios. The negative covariance boundary can make R negative; the construction includes this possibility rather than silently dropping its branch.

The other 240 scenarios deliberately violate one part of the interpretation contract:

| Negative-control family | Cases | What changes |
|:--|--:|:--|
| Wrong independence bound | 120 | The analysis assumes κ = 0, while actual criterion covariance is ±0.2(1−a). |
| Independent sensory resampling | 60 | Each report receives a separate sensory draw of variance a; criterion covariance is zero. |
| Shared lapse and guess | 60 | Both reports share one lapse indicator and, on a lapse trial, one fair binary guess. The marginal lapse rate remains the calibrated value. |

These controls remain independent across paired trials. The paired-yes count is therefore binomial even when the assumed decomposition or within-pair independence is wrong. This is why probability-interval coverage can remain correct while the downstream physical interpretation fails.

## 3. Confidence construction and exact enumeration

For K paired-yes outcomes from N pairs, the equal-tailed 95% Clopper–Pearson interval [L_K,U_K] is computed using beta-distribution quantiles, with the standard count-boundary conventions. For a fixed calibration, the program then retains all shared variances compatible with any paired-yes probability in that interval and any allowed criterion covariance.

At equal marginal variances one, the centered Gaussian rectangle depends on the absolute total correlation r = |R|. Its probability is increasing in r when both halfwidths are positive and lapses are below one. After intersecting the binomial interval with the attainable probability range and inverting that monotone function, let the remaining absolute-correlation interval be [r_L,r_U]. For κ < 1 the compatible variance set is

$$
\left[
\max\left\{0,\frac{r_L-\kappa}{1-\kappa}\right\},
\min\left\{1,\frac{r_U+\kappa}{1+\kappa}\right\}
\right].
$$

This is the full continuous covariance projection, including both signs of R. It is not a finite covariance grid. If the probability interval is wholly outside the model's attainable range, the result is the **empty set**, rather than an artificial boundary estimate.

Let S(p) be the population identified set for exact probability p. On every event where the binomial interval contains the true p, the projected confidence set contains all of S(p). Consequently its probability of containing the entire population set is at least 95%, and the actual shared variance is also covered when the generating package satisfies the declared contract. Point coverage can exceed whole-set coverage under partial identification because covering the generating point is less demanding than containing all compatible points.

For each of the 480 generating scenarios, the program evaluates every K = 0,…,N and sums each metric against Binomial(N,p). Thus a target-inclusion probability is

$$
\sum_{K=0}^{N}
\binom{N}{K}p^K(1-p)^{N-K}
\mathbf 1\{a_{\mathrm{target}}\in C(K)\}.
$$

The same enumeration gives empty-set probability, expected width, complete-population-set coverage, and exclusion rates for the fixed candidates 0, 0.1, 0.3, 0.6, and 0.9. No random repetitions are generated.

“Exact” here describes the finite probability law and enumeration. Special functions, inverse probabilities, and weighted sums are evaluated in floating-point arithmetic, not validated interval arithmetic. The maximum binomial mass-sum discrepancy before normalization is **1.78 × 10⁻¹⁵**. The plan and both code files remain unchanged during execution.

The implementation precomputes 32,664 projected count outcomes and checks inclusion of all five fixed candidate variances against a direct attainable-probability-range intersection. All **163,320 candidate checks** pass. The theory module independently verifies the Gaussian probability and continuous projection formulas; its numerical audit is a separate artifact.

## 4. Coverage across the valid grid

Every table row below contains all three profiles and all five generating sensory variances. A κ = 0 row contains 15 cases; a κ = 0.2 row contains 45 cases because it also includes all three criterion-covariance choices.

| N pairs | κ | Minimum point coverage | Minimum whole-set coverage | Fixed-grid mean expected width | Maximum empty-set probability |
|--:|--:|--:|--:|--:|--:|
| 64 | 0 | 0.955213 | 0.955213 | 0.927341 | 0.018170 |
| 64 | 0.2 | 0.965517 | 0.955213 | 0.939527 | 0.018672 |
| 256 | 0 | 0.953573 | 0.953573 | 0.804631 | 0.023955 |
| 256 | 0.2 | 0.957262 | 0.953168 | 0.843776 | 0.023955 |
| 1024 | 0 | 0.951999 | 0.951999 | 0.576365 | 0.024729 |
| 1024 | 0.2 | 0.958743 | 0.951070 | 0.656680 | 0.024729 |
| 4096 | 0 | 0.950235 | 0.950235 | 0.377228 | 0.024861 |
| 4096 | 0.2 | 0.962317 | 0.950151 | 0.490362 | 0.024861 |

“Expected width” assigns zero to an empty set. This convention is always accompanied by empty-set probability and by a separate conditional-on-nonemptiness width in the complete output. It must not be interpreted as improved precision when a model is frequently incompatible with the data.

The valid-grid results demonstrate the projected confidence guarantee in the specified scenarios. The theorem, rather than the finite grid alone, supplies the general guarantee under the stated assumptions. Nothing in the table tests whether those assumptions hold in a participant.

## 5. Width and partial identification

For the first prespecified profile, with actual c = 0, expected widths are:

| N pairs | Assumed κ | a = 0 | a = 0.3 | a = 0.9 |
|--:|--:|--:|--:|--:|
| 64 | 0 | 0.901523 | 0.915947 | 0.857601 |
| 64 | 0.2 | 0.916167 | 0.929217 | 0.883504 |
| 256 | 0 | 0.729804 | 0.774644 | 0.552059 |
| 256 | 0.2 | 0.773659 | 0.814263 | 0.636330 |
| 1024 | 0 | 0.525447 | 0.587677 | 0.262573 |
| 1024 | 0.2 | 0.603135 | 0.664036 | 0.331677 |
| 4096 | 0 | 0.376837 | 0.447043 | 0.158068 |
| 4096 | 0.2 | 0.479261 | 0.561923 | 0.206180 |

These widths show substantial finite-sample uncertainty even with exact marginal calibration. At a = 0 and κ = 0, the centered response probability changes only at second order in small shared variance, as derived in the accompanying proof. A unique population inverse therefore need not imply a precise finite-sample interval. This table is not a sample-size recommendation and does not claim these particular intervals are statistically optimal.

Allowing criterion correlation creates an additional population ambiguity. For exact probabilities generated by c = 0, the population sets under κ = 0.2 are [0,1/6] at a = 0, [0.125,5/12] at a = 0.3, and [0.875,11/12] at a = 0.9. Increasing the number of otherwise identical pairs does not turn those population sets into unique physical decompositions.

Population set width must also be distinguished from unconditional mean confidence-set width. Sampling errors can occasionally give a narrower or empty projected set, especially near the edge of the attainable range. The complete output therefore records population endpoints, empty-set probability, unconditional width, and nonempty conditional width separately. For example, the first profile at a = 0, κ = 0, N = 4096 has unconditional expected width 0.376837 and nonempty conditional expected width 0.386445, with empty-set probability 0.024861.

The method uses only the paired-yes indicator for its binomial confidence interval. The full four-category response table can contain additional finite-sample information. We do not claim minimal trial count, optimal use of all joint observations, or that Clopper–Pearson projection is the narrowest possible valid confidence procedure.

## 6. Deliberate violations

The following table gives the minimum target-inclusion probability across **all three profiles and all generating variances** within each specified negative-control family at each N. These are envelope summaries of the fixed grid, not selected cases or confidence guarantees.

| N pairs | Wrong independence bound | Independent sensory resampling | Shared lapse and guess |
|--:|--:|--:|--:|
| 64 | 0.951339 | 0.732292 | 0.853192 |
| 256 | 0.941656 | 0.204745 | 0.432273 |
| 1024 | 0.896045 | 0.000116520 | 0.00739829 |
| 4096 | 0.693919 | 3.42504 × 10⁻²¹ | 2.22197 × 10⁻¹² |

### 6.1 Incorrect criterion-independence bound

The Gaussian decomposition still contains a real shared sensory variance, but the declared κ = 0 excludes the actual criterion covariance. The worst inclusion in this fixed grid occurs in the low-lapse asymmetric profile at N = 4096, a = 0.6, and c = +0.08. The probability interval covers the true paired-yes probability with probability 0.951025, while the mapped variance set contains the actual a with probability only **0.693919**.

Its empty-set probability is approximately 2.21 × 10⁻¹⁶. Thus a wrong physical attribution need not produce an empty confidence set: another decomposition under the false independence restriction can match the probability. Better count precision does not repair the missing covariance exclusion.

### 6.2 Independent sensory resampling

Both reports have per-task sensory variance a, but their sensory samples are independent. Their actual shared sensory covariance is zero and their marginal total variances remain one. All values of the per-task a in this negative control therefore produce the same paired probability for a given profile.

The code deliberately evaluates whether a procedure interpreted as shared-draw inference would include the stipulated per-task variance. This is a **target-misattribution diagnostic**, not failed coverage of a true common variance. The CSV labels the target role and records actual shared variance as zero. Under the first profile at N = 4096 and per-task a = 0.9, inclusion of 0.9 is 3.43 × 10⁻²¹. This does not show that the interval fails to cover the actual shared covariance zero.

The result makes the consumer assumption explicit: presenting the same external event twice, or collecting two task reports, does not by itself establish that both reports used the same internal sensory draw.

### 6.3 Shared lapse indicator and shared guess

With shared lapses, the actual paired-yes probability is

$$
p_{11}^{\mathrm{shared\ lapse}}=(1-\lambda)J(a)+\lambda/2,
$$

where J(a) is the nonlapse Gaussian paired probability. The marginal lapse rates are unchanged, so knowing each report's lapse rate is insufficient to justify their independence.

The most extreme fixed-grid case is the high-lapse asymmetric profile at N = 4096 and a = 0.9. Actual paired probability is approximately 0.550163. Target inclusion is **2.22 × 10⁻¹²**, and the confidence set is empty with probability **0.9999999972** because the independent-lapse package cannot accommodate the observed coupling.

The unconditional expected width is approximately **1.10 × 10⁻¹⁰** in this case. That number is not high precision: almost every result is an empty set. Among the very rare nonempty results, expected width is approximately 0.039048. This example is why width-zero conventions must always be reported together with emptiness and conditional width.

Across all negative controls the Clopper–Pearson interval retains at least 95% coverage of the actual paired-yes probability. The failures concern the map from that probability to a physical component under a false contract.

## 7. Reproduction and numerical provenance

Run from the record root:

~~~bash
python finite_sample/run_operating_characteristics.py
~~~

The script uses only the fixed plan and the local confidence_sets.py module. It reads no public human-data workbook or old fit file. It produces:

- operating_characteristics.csv: all 480 cases and every prespecified metric.
- operating_characteristics_summary.json: complete grid summaries and verification counts.
- confidence_set_tables.npz: every count-dependent projected interval and the binomial intervals used to generate them.
- EXECUTION_PROVENANCE.json: plan/code hashes, runtime versions, output hashes, and explicit zero counts for new human data, random simulation, old response refits, and old symmetry reruns.

The recorded execution used Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0, and pandas 2.2.3. It completed in approximately 1.1 seconds. Probability integration and inversion are deterministic; floating-point differences across library versions remain possible. No simulation-based uncertainty interval is attached to these exact finite-law sums.

A final independent numerical check of unequal variances found a rounding issue in labeling an exactly full-domain set. Module version 1.0.1 adds the analytic rule that a probability interval containing the complete model range returns the exact supplied physical domain. The original module and first execution are retained in the history folders. One deterministic rerun of the unchanged 480-case plan against version 1.0.1 leaves the entire CSV byte-identical, all 124 stored NumPy arrays exactly identical, and every summary value unchanged apart from completion time and runtime. CORRECTION_REEXECUTION_RECEIPT.json records that comparison. No original response fit or conditional simulation was rerun.

Figure 4 is produced by `python finite_sample/make_finite_sample_figure.py`. Both panels use every profile in the fixed grid. The figure provenance preserves each plotted aggregate and the exact two very small endpoint probabilities; the PNG was visually checked after placing the legend and two notes in separate, uncropped rows.

## 8. Consequences for the manuscript

The finite-sample analysis makes the proposed additional observable operational: a paired count can be converted into a confidence set with a stated coverage guarantee. It also prevents three overstatements.

First, nominal coverage does not establish useful precision; many sets cover a large part of the variance domain. Second, allowing independently justified criterion correlation can preserve a nontrivial population set even with perfect knowledge of the joint probability. Third, accurate marginal calibration does not validate common sensory sampling or independent lapse processes.

The result supports a concrete methods contribution and a clearly bounded future experiment. It does not validate a physiological sensory mediator, identify subjective experience, distinguish consciousness theories, or supply evidence that an AI has consciousness. The source study's blockwise marginal data do not provide the paired observations or the consumer verification required by this construction.

## Reference

1. Clopper, C. J., and Pearson, E. S. (1934). The use of confidence or fiducial limits illustrated in the case of the binomial. *Biometrika*, 26(4), 404–413. [https://doi.org/10.1093/biomet/26.4.404](https://doi.org/10.1093/biomet/26.4.404). The model-specific confidence-set projection and its calibration qualifications are derived in the accompanying PROOF.md.
