# Response-level BCI comparison: final execution report

**Record:** CTD v0.2, 10 October 2026. **Status:** completed retrospective secondary analysis, with a documented uniform numerical repair. The final results are in results/bci_response/. The earlier results in results/pre_nested_cv_repair/ are superseded and must not be used for the manuscript's predictive conclusions.

## 1. Main result and its scope

Within the four specified Bayesian causal-inference (BCI) response families, adding one stable response center for each task improves aggregate held-out prediction. After the numerical repair described below, the condition-varying-noise model with task centers has total held-out negative log likelihood (NLL) **5238.549911**, compared with **5299.434505** for the condition-varying-prior model with task centers. Their difference, noise minus prior, is **−60.884595**, or **−2.029486 per participant**. The descriptive participant-level 95% paired t interval is **[−3.267624, −0.791349]**; 21 of 30 participants favor the noise family.

This is a comparison of explicitly restricted response families, conditional on one fixed partition of public aggregated counts. It neither identifies a sensory locus for the changing variance nor constitutes an independent replication. The exact sensory/criterion-jitter counterpart developed in the accompanying theory preserves each model probability pointwise, so every full-data or held-out score based on those same marginal probabilities is also identical. A predictive preference over the selected prior family does not discriminate that exact counterpart.

The new centered fits still have substantial count-table deviance. The nominal chi-square references are not treated as calibrated definitive tests because there are only ten responses per cell, nonlinear parameters, boundary fits, possible dependence, and no original trial chronology. The separate parameter-free symmetry analysis addresses a necessary restriction of the original unshifted models under its stated binomial observation law. It must remain distinct from both predictive ranking and physical implementation identification.

## 2. Sources, subjects, and count mapping

The primary study is D'Angelo, M., Lanfranco, R. C., Chancel, M., and Ehrsson, H. H. (2026), *Parietal alpha frequency shapes own-body perception by modulating the temporal integration of bodily signals*, Nature Communications 17:53, DOI [10.1038/s41467-025-67657-w](https://doi.org/10.1038/s41467-025-67657-w). Public study materials are at [the authors' data project](https://osf.io/ytga5/) and [the authors' BCI code project](https://osf.io/s5p4v/).

The source recruited 37 people for Experiment 3 and included the 30 who met the rubber-hand-illusion inclusion criterion. The data therefore concern the selected source sample. The experiment applied 8-Hz, sham, and 13-Hz tACS in sessions on different days. Ownership and simultaneity judgments were collected in separate, counterbalanced blocks. Our analysis uses no new human observations and does not reconstruct a same-trial joint response.

All executable inputs reside in empirical/inputs/:

| Local file | Source | SHA256 |
|:--|:--|:--|
| Experiment_3.xlsx | [OSF p5un6](https://osf.io/download/p5un6/) | d3b2fef22f077788e5299dedb68737d453c09b005d9360bab8dfbe6c35852bc9 |
| Experiment_3_Computational_modelling.xlsx | [OSF yc4k2](https://osf.io/download/yc4k2/) | 32e58a814b7d33f52f3dc994a753715d4ddfa21c8ec7424b80ebef43c6d560e4 |
| NatComm2026_SourceData.xlsx | [Publisher Source Data](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41467-025-67657-w/MediaObjects/41467_2025_67657_MOESM4_ESM.xlsx) | 3202d68439ad502ff95e7a4d59535a4e8ff9072d5c6a76b5aebf7dde90228a82 |

The count workbook's first worksheet, rows 4–33 and columns B–AQ, contains 30 × 42 counts. Each row is reshaped as six curves × seven SOAs. The curves are ownership 8 Hz, ownership sham, ownership 13 Hz, simultaneity 8 Hz, simultaneity sham, simultaneity 13 Hz. SOAs are −400, −200, −100, 0, 100, 200, and 400 ms. The denominator is ten for every cell: 1,260 count cells, 420 binary judgments per participant, and 12,600 judgments in total.

The saved-parameter workbook supplies the Prior block in rows 2–31, columns B–J, with NLL in K; the Sigma block is in rows 36–65, B–H, with NLL in I. We preserve its numerical order. A misleading task header is resolved by the actual helper-function mapping and exact saved-likelihood reproduction, not by relabeling participants or selecting a scientifically favorable result.

The three workbook copies are byte-identical to their downloaded sources. RECONSTRUCTION_PROVENANCE.json records full source URLs, hashes, runtime, and retrieval context. The BCI reconstruction uses the actual counts and source likelihood, independently of the released descriptive Gaussian-width estimates.

## 3. Four explicit response models

Let t denote task, f stimulation condition, s signed SOA, λ total fair-guess lapse probability, and Φ the standard-normal distribution function. The model probability is

$$
p_{tf}(s)=\lambda/2+(1-\lambda)
\left[\Phi\{(k_{tf}-s+\mu_t)/\sigma_{tf}\}
-\Phi\{(-k_{tf}-s+\mu_t)/\sigma_{tf}\}\right].
$$

The halfwidth is determined by the source Bayesian rule:

$$
k_{tf}^2=\left[
\frac{2v_{tf}(v_{tf}+V_S)}{V_S}
\left\{\operatorname{logit}\pi_{tf}
+\frac12\log(1+V_S/v_{tf})\right\}
\right]_+,\qquad v_{tf}=\sigma_{tf}^2.
$$

Here V_S = 84,000 ms² is fixed to the sample variance of the six nonzero SOAs, matching the source code. When the expression is nonpositive the decision interval is empty and the nonlapse response is zero. The original two families set both centers to zero.

| Model identifier | Priors | Standard deviations | Task centers | Effective parameters per participant |
|:--|:--|:--|:--|--:|
| sigma | Two, one per task, fixed across stimulation | Three, one per condition, shared between tasks | Fixed at zero | 6 |
| prior | Six, task × condition | One, shared throughout | Fixed at zero | 8 |
| sigma_shift | As sigma | As sigma | Two, each fixed across stimulation | 8 |
| prior_shift | As prior | As prior | Two, each fixed across stimulation | 10 |

Every model has one lapse parameter per participant. The source scripts counted the fixed stimulus-prior scale in their vectors, giving seven versus nine nominal entries; the effective fitted dimensions are six versus eight. Adding task centers is an explicitly restricted location correction, not a new observer-model principle. It does not add condition-specific centers, change the source threshold policy, or absorb arbitrary curve shapes.

The independent Python likelihood minimizes positive NLL,

$$
\mathcal L=-\sum_j \{y_j\log p_j+(n_j-y_j)\log(1-p_j)\}.
$$

Binomial combinatorial constants are omitted consistently. This makes the sum of held-out fold scores equal to the binary predictive log score; the omitted constants cannot affect comparisons on the same held-out observations.

### Numerical domain

Prior logits are bounded by [−16,16], log standard deviations by [−10,10] **with standard deviations measured in milliseconds**, total lapse by [10⁻⁸,1−10⁻⁸], and centers by [−800,800] ms. Only center parameters are internally scaled in units of 100 ms. Explicit lapse bounds keep probabilities strictly inside (0,1); the likelihood does not clip probabilities and then apply an inconsistent derivative.

These finite bounds are part of the independent fit, and differ from the full feasible domain of the original source optimization. Optimizer status, gradients, multistarts, and nesting checks are numerical evidence, not proofs of global optimality.

## 4. Execution plan and fixed partitions

BCI_EXECUTION_PLAN.json was written before the new held-out scores were inspected. This was after access to the source data and other exploratory work, so the project is retrospective rather than preregistered. The model list, seeds, finite bounds, and number of generic starts were fixed for this execution.

Full-data fits use 16 predetermined scrambled Sobol starts, the fitter's canonical start, and the matching released parameter vector projected into the declared finite box. Each shifted full-data fit also uses its own unshifted full-data fit with two zero centers as a starting point.

For cross-validation, each cell's ten binary outcomes is independently permuted once and divided into five pairs using seed 2026101017. Each fold fits eight observations and evaluates the other two; every nominal binary judgment is held out exactly once. The full count is necessarily used to construct this allocation. Once allocated, only training counts enter fitting; neither source parameters, full-data fits, nor held-out counts initialize or select any training fit.

Each fold uses eight predetermined Sobol starts plus the canonical start. The eight-start budget was chosen before inspecting scores. The final rule also includes the same-training-fold unshifted fit with zero centers for every shifted fit. Generic fit seed 2026101019 is deterministically offset by participant, fold, and model. The saved partition and all initialization vectors make these decisions inspectable.

Artificial allocation is possible because a binomial count is sufficient for this likelihood under conditional exchangeability. It does not restore actual response order, block identifiers, learning, fatigue, serial dependence, or joint ownership/simultaneity observations. The target is prediction of further exchangeable judgments at the same participant/task/condition/SOA cells. No person or stimulus level is held out.

## 5. Numerical nesting repair and independent review

The initial execution found successful optimizer statuses and acceptable projected gradients for all selected fits. Independent review nevertheless identified three sigma_shift CV training objectives worse than the contained same-fold sigma fit:

| Participant | Fold | Initial shifted-minus-unshifted training NLL |
|--:|--:|--:|
| 16 | 3 | 51.712174 |
| 21 | 4 | 50.513156 |
| 22 | 2 | 99.666405 |

This revealed poor local solutions that status and gradient checks alone did not detect. BCI_CV_NESTING_REPAIR_DECISION.json records the response: archive the original output and code, add the same-training-fold unshifted parameter vector with zero centers to **all 300 shifted fold fits**, and refit them using the original generic starts, seeds, and bounds. The 120 full-data fits and 300 unshifted CV fits were retained unchanged. The trigger and uniform rule used training nesting, not held-out scores. The rule was adopted after the initial execution; it is not retrospectively represented as the original plan.

The implementation supplies the embedded point as an optimizer start and checks the final objective against its contained-model reference. It does not claim an unoptimized point is independently retained as an eligible final candidate. After repair, all 300 fold nesting comparisons and 60 full-data nesting comparisons pass. Five sigma_shift fits improve their training objectives by more than 0.001; prior_shift changes are at small numerical scales. The main manuscript must use the final score difference of −60.884595, not the superseded near-tie.

The final 720 selected fits all have successful status and zero declared numerical quality flags; the maximum projected gradient is 0.000395652, below the declared 0.001 threshold. An independent signed-SOA implementation recomputed all probabilities, training/full NLLs, and held-out NLLs with maximum probability discrepancy 5.55 × 10⁻¹⁶ and maximum objective discrepancy 3.55 × 10⁻¹³. The initial independent gradient check covered 52 cases, with maximum scaled discrepancy 3.60 × 10⁻⁶; the later independent audit covered 28 additional cases with maximum scaled discrepancy 3.34 × 10⁻⁷.

Audits are recorded in results/bci_response/execution_integrity_audit.json and the accompanying theory/RESPONSE_COMPARISON_AUDIT.json. They also verify that all 300 shifted CV initializations are exactly their respective training-fold base fits followed by two zeros.

### Boundary counts

| Phase | Model | Fits with any bound | Prior-logit bound | Log-SD bound | Lapse bound | Center bound |
|:--|:--|--:|--:|--:|--:|--:|
| Full, 30 fits | sigma | 12 | 1 | 0 | 11 | 0 |
| Full, 30 fits | prior | 14 | 1 | 0 | 13 | 0 |
| Full, 30 fits | sigma_shift | 13 | 1 | 0 | 12 | 0 |
| Full, 30 fits | prior_shift | 14 | 2 | 0 | 12 | 0 |
| CV, 150 fits | sigma | 71 | 8 | 5 | 60 | 0 |
| CV, 150 fits | prior | 74 | 11 | 0 | 63 | 0 |
| CV, 150 fits | sigma_shift | 72 | 6 | 0 | 66 | 0 |
| CV, 150 fits | prior_shift | 78 | 11 | 0 | 67 | 0 |

Categories can overlap. No center reaches the ±800-ms bound. The full-data center ranges are −32.88 to 96.69 ms for ownership and −39.77 to 90.38 ms for simultaneity in sigma_shift; the corresponding prior_shift ranges are −41.77 to 105.24 and −38.54 to 85.79 ms.

## 6. Final numerical comparison

All scores below are sums over the 30 source participants. The machine-readable compact table is results/bci_response/proof_facing_model_comparison.csv.

| Model | Effective k / person | Full NLL | Held-out NLL | Held-out NLL / judgment | Full count deviance |
|:--|--:|--:|--:|--:|--:|
| sigma | 6 | 5138.949902 | 5465.166346 | 0.433743 | 1707.697164 |
| prior | 8 | 5142.924911 | 5427.816041 | 0.430779 | 1715.647182 |
| sigma_shift | 8 | 4894.506112 | 5238.549911 | 0.415758 | 1218.809584 |
| prior_shift | 10 | 4891.247909 | 5299.434505 | 0.420590 | 1212.293178 |

The saturated count NLL is 4285.101320. Nominal deviance degrees of freedom are 1080, 1020, 1020, and 960 respectively. Reference chi-square tail probabilities are approximately 4.14 × 10⁻³¹, 3.35 × 10⁻³⁸, 1.60 × 10⁻⁵, and 4.81 × 10⁻⁸. They are supplied for transparency and described as nominal references, not as exact calibrated conclusions about human data.

| Paired held-out contrast, first minus second | Total difference | Mean / participant | Descriptive 95% interval for mean | Participants favoring second |
|:--|--:|--:|:--|--:|
| sigma − prior | 37.350304 | 1.245010 | [−1.275749, 3.765770] | 16 / 30 |
| sigma_shift − prior_shift | −60.884595 | −2.029486 | [−3.267624, −0.791349] | 9 / 30 |
| sigma − sigma_shift | 226.616435 | 7.553881 | [3.506699, 11.601064] | 22 / 30 |
| prior − prior_shift | 128.381536 | 4.279385 | [0.826701, 7.732068] | 17 / 30 |

The intervals use 30 participant differences after summing folds within participant. They do not treat 150 folds as independent subjects. Their scope is conditional on this fixed allocation and fitting procedure in the selected sample; they do not estimate an independent replication distribution. We do not select additional random splits based on these intervals.

Summed conventional AIC values are 10637.899804, 10765.849822, 10269.012224, and 10382.495818. BIC values using 420 binary observations per participant are 11365.145652, 11735.510953, 11238.673354, and 11594.572231. Standard asymptotic interpretations can be affected by the noted boundaries and nonregular parameter regions. Full-data AIC and held-out scoring are different criteria: for example, unshifted sigma has lower summed AIC but higher aggregate held-out NLL than unshifted prior.

## 7. Distinguishing source-fit arithmetic from independent refits

The separate literature/SOURCE_BCI_AUDIT.md evaluates all released parameter vectors without optimization. It reproduces the saved NLL sums, 5138.960411 for Sigma and 5142.889991 for Prior, and traces the source's information-criterion sign discrepancy through all 30 publisher rows. Correcting the saved-fit arithmetic changes summed Sigma-minus-Prior AIC from −112.140840 to −127.859160 and BIC from −354.556123 to −370.274442, preserving the aggregate Sigma preference. These are source-fit results and must not be confused with the independent bounded-fit table above.

The new bounded sigma full NLL is 0.010509 lower than the released sum. The new bounded prior full NLL is **0.034920 higher**. This is not a mismatch in the reproduced source likelihood: the saved vectors are evaluated separately in the source audit. The explicit finite parameter box excludes some source values near a prior probability of one.

The clearest contribution is participant 6: the released Prior NLL is 203.176603, while the bounded fit gives 203.230073, a difference of +0.053470. Its first released prior is approximately 0.999999999550471, whose logit exceeds the declared upper bound of 16. Projecting the source vector into our box initially gives NLL 204.859673; the bounded optimization recovers most, but not all, of this loss. Improvements elsewhere offset part of it, leaving the aggregate +0.034920 difference. Every new full-data original-family fit is no worse than its own source initialization evaluated within the finite box.

This identifies a bound-related contribution and explains why the released and new fit sums should be kept separate. It is not a proof that either implementation has found a global unrestricted optimum. No further bounds, starts, or scientific comparisons were selected to force agreement with the saved objective or a desired model ranking.

## 8. Relation to the Gaussian-width audit

WIDTH_RECONSTRUCTION_REPORT.md treats a different estimator: ordinary least-squares Gaussian response widths. A free baseline and free center recover 176 of 180 released widths within 0.01 ms and 178 within 0.1 ms, leaving two material differences unresolved. Its unconstrained descriptive curves are not necessarily valid probabilities. Their fitted width is not the latent SD used by the BCI count law.

The current likelihood analysis does not import Gaussian-width uncertainties, discard the two exceptional source rows, or choose a different curve family just for them. It retains all 30 participants and all 1,260 count cells under the declared BCI models. Conversely, exact reconstruction of a count-model objective does not retroactively establish the missing original Gaussian fitting procedure.

## 9. Reproduction, packaging, and interpretation

The portable analysis layout is one record containing empirical/, root_analysis/, theory/, and literature/. All empirical executable defaults locate their inputs relative to their own file, with raw workbooks in empirical/inputs/. Our canonical runner imports root_analysis/fit_response_models.py. The historical absolute paths in receipts identify the original session; they are not computational input dependencies. The fitter's optional self-check has been relocated to the same local inputs. Its original execution bytes are preserved in history/execution_source/; RELOCATION_PROVENANCE.json records the old and current hashes and verifies that every likelihood/fitting function's AST is unchanged. Both score audits check this provenance rather than assuming a path-only source change must have the same file hash. The old execution summary is not edited.

With Python and the dependencies recorded in RECONSTRUCTION_PROVENANCE.json, the core commands from the record root are:

~~~bash
python empirical/run_bci_response_comparison.py
python empirical/audit_bci_execution.py
~~~

The first command executes the final rule directly, including same-training-fold starts for shifted models. The separate repair_cv_nesting.py reproduces the documented uniform repair from results/pre_nested_cv_repair/ and retains the historical fit record. It is not necessary to run both fitting paths to reproduce the final scientific result. Floating-point optimization and package versions may produce small platform-dependent differences; all fitted parameters and probabilities are retained for exact score auditing without refitting.

The final package should retain our Python code, the three unchanged workbooks, execution plans, full fit records, fixed partitions, summaries, audit reports, input and source provenance, and the superseded numerical record clearly labeled as such. Author MATLAB files, downloaded article PDFs, EEG archives, and extracted whole-article text are context material rather than runtime requirements and need not be redistributed. Their URLs and hashes preserve source attribution. The public BCI code project's OSF node metadata explicitly links CC BY 4.0; the separate data project's node metadata contains no assigned license. The primary article is CC BY 4.0. These are distinct metadata observations, not a new license assigned by this project. The exact node records and resolved license are in author_inventory/LICENSE_METADATA_CHECK.json. Any retained source files preserve attribution and original terms.

The results establish a reproducible ranking among four declared response families and show why necessary response restrictions, numerical adequacy, and implementation identification must be assessed separately. They do not show that a particular neuron, pathway, sensory consumer, subjective experience, or consciousness theory was identified. The accompanying paired-readout theorem proposes additional information under explicit independence and calibration assumptions; the source's separately blocked marginal counts do not already contain that information.
