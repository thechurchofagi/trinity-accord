# Final empirical and finite-sample review of CTD v1.0

**Date:** 10 October 2026. **Decision:** PASS within the manuscript's stated retrospective, conditional-model scope. No unresolved scientific must-fix was found in the reviewed empirical sections, abstract, finite-sample section, or Figure 4. This is an internal AI-assisted technical review, not external peer review. The empirical reviewer authored the new numerical reanalysis and independently checked the theory collaborator's confidence construction; the project should not present that internal division as independent experimental replication.

**Reviewed manuscript:** `manuscript/noise-identifiability-bodily-judgments-v1.0.0.md`. Exact snapshots of the reviewed manuscript and principal evidence files are in `FINAL_EMPIRICAL_REVIEW_v1.0.json`. Later insertion of a release DOI or typesetting changes is outside that scientific snapshot. This review does not certify repository, DOI, timestamp, archive, or external publication state.

## 1. Source observations and interpretation

The main text correctly identifies a selected sample of 30 participants from 37 recruited, with two tasks, three stimulation conditions, seven signed SOAs, and ten judgments per count cell. There are 1,260 count cells and 12,600 nominal binary judgments. Both tasks occur within participants but in separate blocks; the dataset does not contain the paired internal-sample observations required by the proposed identification theorem. Aggregated counts do not reveal response chronology or establish independence from serial or block effects.

The three source-workbook hashes were compared with the execution receipts and match. The count mapping is ownership first, then simultaneity; each task has 8 Hz, sham, and 13 Hz; SOAs run from -400 to +400 ms. The exact saved-likelihood reproduction supports the mapping. The manuscript does not resolve ambiguous labels by selecting favorable statistical results.

The retrospective status and post-access execution plans are explicit. The fixed artificial CV partition is described as conditional on exchangeable judgments at existing participant/stimulus cells, without implying new participants, new SOAs, chronological prediction, or an independent experiment. The discussion also acknowledges that the centering extension was motivated by these data, so its scores are not selection-adjusted estimates of generalization benefit.

## 2. Numerical reconciliation

The following quantities agree with their stored records at the precision shown in the manuscript. No source model was refitted and no old conditional simulation was rerun for this review.

| Item | Verified value | Evidence |
|:--|:--|:--|
| Saved Sigma and Prior objective vectors | 30 each; maximum absolute reconstruction differences 6.537e-13 and 1.994e-9 | `literature/source_bci_reconciliation.json` |
| Released IC calculation matched to publisher rows | Maximum differences 2.487e-14 for AIC and 4.796e-14 for BIC | Same source audit |
| Corrected summed Sigma-minus-Prior AIC/BIC | -127.8591597 / -370.2744424 | Same source audit |
| Released summed AIC/BIC differences | -112.1408403 / -354.5561229 | Same source audit |
| Corrected participant preference | Sigma in 29/30 for either IC; raw likelihood favors Sigma in 14/30 | Same source audit |
| Descriptive widths reconstructed | 176/180 within .01 ms; 178/180 within .1 ms | `empirical/results/all_gaussian_candidate_fits.csv` |
| Median absolute width discrepancy | .0001443449523 ms | Same Gaussian table |
| Unresolved width cases | P1 simultaneity 8 Hz: 196.651359 versus 169.55807 ms; P24 ownership 13 Hz: 120.484438 versus 127.66943 ms | `empirical/results/reconstruction_residual_audit.json` |
| Reconstructed probability-domain violations | 96 curves at observed SOAs; 129 somewhere on the real line | Same residual audit |
| Conditional symmetry statistic | 984.3042364 across 540 signed pairs | `theory/SYMMETRY_TEST_RESULTS.json` |
| Conditional null mean and SD | 531.4224103 / 31.7477215 | Same symmetry record |
| Conditional Monte Carlo result | 0/19,999 exceedances; plus-one p=.00005; exceedance-probability interval [0,.0001844362] | Same symmetry record |
| Exact marginal counterpart | All 1,260 probabilities agree within 2.220446e-16; NLL sum 5138.960411207295 | `root_analysis/response_twin_summary.json` |

The double likelihood-sign change is reported as an arithmetic discrepancy linked to public code, saved parameters, and every publisher comparison row. The corrected aggregate preference remains Sigma. The manuscript appropriately avoids claiming that the stimulus effect disappeared, that the preferred aggregate model reversed, or that the source optimization and bootstrap history were fully reproduced. The fixed stimulus-prior variance is 84,000 ms squared, and the fixed parameter adds the same nominal dimension to both source families, leaving their penalty difference unchanged.

The two Gaussian discrepancies remain visible. A freely signed baseline and free center closely reconstruct most estimates, but the original Gaussian fitting implementation was not located in the inspected public inventory. The manuscript neither substitutes new values into the source table nor describes reconstructed nuisance estimates as author-released estimates. It distinguishes descriptive least squares from a valid Bernoulli response law and from the source observer's effective standard deviation.

## 3. Predictive comparison and numerical repair

The final score table matches `empirical/results/bci_response/response_comparison_summary.json`:

| Family | Parameters/person | Full NLL | Held-out NLL |
|:--|--:|--:|--:|
| Sigma | 6 | 5138.949902 | 5465.166346 |
| Prior | 8 | 5142.924911 | 5427.816041 |
| Sigma with centers | 8 | 4894.506112 | 5238.549911 |
| Prior with centers | 10 | 4891.247909 | 5299.434505 |

The location extensions reduce held-out NLL by 226.616435 and 128.381536. The shifted Sigma-minus-Prior contrast is -60.884595 in total and -2.029486 per participant; the descriptive paired interval is [-3.267624,-.791349], with 21 of 30 participant differences favoring shifted Sigma. Before adding centers, the total difference is +37.350304 and the participant interval spans zero. These facts are all preserved in the main text.

The finite parameter domain is disclosed, including lapse limits, prior logits, standard-deviation logs in milliseconds, and centers within 800 ms of zero. The independently fitted unshifted Prior total exceeds the saved source total by .034919979, so the manuscript correctly treats the bounded reanalysis separately from saved-parameter evaluation. Bound contacts and lack of a global-optimality certificate are stated.

The initial three training-nesting violations are retained, not erased. The uniform repair uses each shifted model's own unshifted solution on the same training data as a zero-center initialization. It adds no full-data or held-out information to CV initialization. All 60 full-data nesting comparisons and all 300 fold nesting comparisons pass in the final records. Final scores are based on those repaired results, not the superseded run. The review confirms 120 full-fit and 600 CV records with zero recorded final numerical-quality flags.

The conditional symmetry rejection is scoped to the centered independent-binomial family. Its Monte Carlo interval describes simulation-tail uncertainty, not uncertainty about a mechanism. Shifted-model count deviances remain reported as adequacy diagnostics, with nominal chi-square calibration expressly qualified for small cell counts, boundaries, and dependence. Predictive improvements are not treated as sensory localization.

## 4. Exact counterpart and prospective interpretation

The fixed construction `a_i = .5*min_f(v_if)` retains total variance, lapse, center, and each condition-specific source threshold. It therefore changes the internal allocation of variance while preserving every marginal response probability. The manuscript correctly credits prior sensory/criterion-noise models and does not describe the counterpart as the same normative observer with only its sensory variance reinterpreted. In particular, the source threshold policy is retained; it is not held fixed across stimulation if the original policy changes it.

The source-derived prospective joint profiles are model illustrations. Their gap range, about 3.68e-10 to .1348 with median .01762, does not become an empirical sample-size or power result. The original blockwise task data did not measure these probabilities. The manuscript explicitly notes that the original centered family's symmetry restriction fails its count-model check, so the prospective source-parameter illustrations are not validated subject-specific forecasts.

## 5. New finite-sample analysis

`finite_sample/ANALYSIS_PLAN.json` fixes three threshold/lapse profiles, four sample sizes, five generating variances, all valid covariance settings, and three assumption-control families before calculation. Its hash remains unchanged. The completed computation enumerates the full finite binomial law, without random Monte Carlo draws, source-parameter selection, or new human observations.

The 480 cases comprise 240 valid cases, 120 wrong criterion-bound cases, 60 independent-resampling cases, and 60 shared-lapse-and-guess cases. All three profiles enter every grouped result. The complete table and source summary verify the main text's minimum true-variance coverage of .950235 and minimum complete-population-set coverage of .950151. The latter is a stronger statement than coverage of one generating point; the implementation checks both separately.

For the independent-criterion grid, fixed-grid mean expected width changes from .927340542 at N=64 to .377227676 at N=4096. At criterion bound .2 the corresponding means are .939526621 and .490361641. These are averages of specified scenarios, not participant means, trial-count recommendations, or population power. The .2 summaries contain all three covariance choices; this is transparent in the report and figure caption.

The maximum valid empty-set probability is .024861288. Empty sets have width zero in the unconditional width metric, and the complete output also provides empty probability and width conditional on nonemptiness. The extreme shared-lapse example has an almost-always-empty set; its tiny unconditional width is not called precision. The report also avoids claiming that expected confidence width must always exceed population identified-set width at boundary scenarios.

Negative-control target labels are correct. Wrong criterion independence and shared lapse indicators can invalidate physical variance coverage while the underlying binomial probability interval still covers its probability at the nominal rate. Independent sensory resampling evaluates per-task variance while actual shared covariance is zero. Its very small inclusion rate for a target of .9 is a misattribution diagnostic, not failure to cover a true shared variance of .9. No negative-control row asserts nominal target coverage.

The model-specific confidence module and full proof received a separate review in `finite_sample/INDEPENDENT_CONFIDENCE_SET_REVIEW.md`. Its complete-population-set guarantee follows from a single probability-coverage event. Empty sets, both covariance signs, unequal effective variances, degenerate readouts, and calibration-union restrictions are handled explicitly. Uncertain marginal calibration requires an additional valid set; the fixed grid does not demonstrate coverage after plugging in fitted nuisance parameters.

The final version 1.0.1 module repairs only a floating-point label/endpoint issue for exactly full-domain projection. One deterministic rerun leaves the CSV byte-identical, all 124 saved NumPy arrays exactly identical, and summary values unchanged except time and runtime. Original execution records remain in history, and `CORRECTION_REEXECUTION_RECEIPT.json` documents the relation. The old 720 response fits and old 19,999 conditional simulations were not rerun.

## 6. Figure 4 and manuscript corrections closed

The figure uses every prespecified profile. Panel A shows the mean and full minimum–maximum range of expected width within each valid grid. Panel B shows complete-grid minimum target inclusion for each labeled assumption control. Its linear vertical scale does not visually exaggerate the tiny endpoint probabilities, which are annotated numerically. These are fixed-grid extrema, not estimated confidence bands.

The initial figure footer overlapped its legend. The revised layout uses a separate legend row and two separated explanatory notes. The PNG was viewed and all plot regions, axis labels, legend entries, and notes are visible without overlap or clipping. The PDF and PNG are generated by `finite_sample/make_finite_sample_figure.py`; `FIGURE4_PROVENANCE.json` stores the plotted aggregates and output hashes.

The final wording corrections have been verified in the manuscript: the caption says the maximum valid empty probability is **less than .024862**, and the kappa-one endpoints are explicitly normalized as intervals for `a/v` or `C/v`. The abstract states second-order sensitivity near zero **total correlation**; Section 6.3 explicitly places the shared-variance expansion under independent criteria. No claim of second-order sensitivity for arbitrary nonzero criterion covariance is made. These clarifications alter no calculation. The final read-only check and actual observed manuscript hash are retained in `FINAL_EMPIRICAL_REVIEW_ADDENDUM_v1.0.json` without rewriting the original review snapshot.

## 7. Final scope and release recommendation

The manuscript now supports a methods preprint based on a traceable source-model audit, a necessary-condition failure, a restricted predictive comparison, a response-equivalent implementation, and a finite-sample extension under an explicit prospective observation contract. It does not support a claim of newly collected human evidence, a validated sensory mediator, a direct measure of experience, a decisive UCT test, or evidence of AI consciousness. Those limitations remain visible in the abstract and discussion.

No further empirical fitting, Monte Carlo expansion, or additional optional scenario search is needed to close this review. The present files supply the evidence for the stated contribution. Release provenance and final publication operations remain the responsibility of the coordinating author workflow.
