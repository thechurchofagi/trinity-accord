# Empirical manuscript review

**Manuscript:** manuscript/noise-identifiability-bodily-judgments-v0.2.0.md.

**Review date:** 10 October 2026. **Reviewer role:** internal empirical implementation and numerical provenance audit; this is not external peer review. **Scope:** abstract, empirical Sections 2–4, the source-parameter instantiation in Section 5, empirical statements in the discussion and declarations, and Appendix A. The identification proofs and literature priority claims receive separate reviews.

## Disposition

**PASS for the empirical claims in the revised manuscript and the scoped portability checks.** The source count mapping, released-fit arithmetic, width-reconstruction limits, final repaired cross-validation results, boundary caveats, and stated inferential scope agree with the underlying records. Two earlier implementation-description errors were reported and have been corrected in the current text. The optional self-check input path and score-audit provenance have also been made portable without changing the likelihood or fitting code.

No new fits, model searches, partitions, or scientific tests were performed for this review. The final fit audit from the theory reviewer independently recomputes all 720 full/training fits and held-out scores and verifies all 360 relevant nesting comparisons.

## 1. Source and design checks

The following statements match the primary article and public workbooks:

| Item | Verified value or scope |
|:--|:--|
| Experiment | D'Angelo et al., Nature Communications 17:53 (2026), DOI 10.1038/s41467-025-67657-w |
| Source sample | 37 recruited for Experiment 3; 30 included after illusion-susceptibility screening |
| Design | Both tasks and three conditions within each included participant; tasks in separate counterbalanced blocks |
| Conditions | 8 Hz, sham, 13 Hz |
| Count array | 30 participants × 2 tasks × 3 conditions × 7 SOAs |
| SOAs | −400, −200, −100, 0, 100, 200, 400 ms |
| Denominators | Ten per cell, 420 per participant, 12,600 total binary judgments |
| Workbook region | First sheet, rows 4–33, B–AQ |
| Missing observations | Original response chronology, block-level trial records, and simultaneous paired task responses are not reconstructed from this table |
| Analysis status | Retrospective; execution plans precede the corresponding new numerical runs, not original data access |

The row and column mappings are fixed by workbook identities and the source likelihood helper. The original saved-objective reconstruction is an independent check of that mapping. The manuscript does not treat aggregate counts as though they were ordered trial records or the separate task blocks as a paired consumer experiment.

## 2. Released observer and information-criterion audit

Equations (1)–(3) reproduce the source interval predictor, halfwidth rule, total-lapse convention, and positive negative log likelihood. The fixed stimulus-prior variance 84,000 ms² correctly uses the sample variance of six nonzero SOAs. Sigma has six fitted parameters and Prior eight after excluding the fixed scale. The sign discrepancy is correctly traced through the double negation and checked against all 30 publisher rows.

The saved-fit sums 5138.960411 and 5142.889991, corrected Delta AIC −127.859160, corrected Delta BIC −370.274442, and the participant preference counts match literature/source_bci_reconciliation.json. The draft correctly states that the aggregate preference is preserved. It does not claim that the original stimulus effect disappears, or that all bootstrap and group-model-selection execution details have been reconstructed.

The new bounded full-data fits are kept separate. The Prior full-data sum is +0.034920 relative to the source saved sum. The explicit prior-logit boundary explains an identified contribution, notably participant 6's source prior near one; this does not prove global optimality within either feasible domain. The manuscript's qualifications are appropriate.

## 3. Descriptive width reconstruction

Section 3.2 and Appendix A correctly state **176/180 within 0.01 ms; 178/180 within 0.1 ms**, rather than exact reconstruction. The two unresolved values and directions are correct:

| Case | Released SD, ms | Reconstructed SD, ms |
|:--|--:|--:|
| Participant 1, simultaneity, 8 Hz | 169.55807 | 196.651359 |
| Participant 24, ownership, 13 Hz | 127.66943 | 120.484438 |

The free-baseline Gaussian is an ordinary least-squares descriptive estimator. The count of reconstructed curves leaving [0,1] is **96 at observed SOAs** and **129 somewhere over the real line**. The draft properly attributes these nuisance parameters to our reconstruction rather than implying that the author released them. It does not treat Gaussian SD as identical to the BCI latent SD, use the descriptive curves as Bernoulli laws, or silently repair the two exceptions.

The original fitting implementation was not found in the inspected public inventory. That is an inventory-limited statement, not an allegation that the source counts are wrong or that no such original implementation exists.

## 4. Final predictive results and numerical repair

The final score table agrees with results/bci_response/response_comparison_summary.json:

| Model | Full NLL | Held-out NLL |
|:--|--:|--:|
| Sigma | 5138.949902 | 5465.166346 |
| Prior | 5142.924911 | 5427.816041 |
| Sigma + center | 4894.506112 | 5238.549911 |
| Prior + center | 4891.247909 | 5299.434505 |

The shifted-family held-out contrast is **−60.884595**, with mean **−2.029486**, descriptive participant interval **[−3.267624, −0.791349]**, and 21/30 participants favoring Sigma + center. The location gains 226.616435 and 128.381536 are correct. The unshifted contrast +37.350304 favors Prior in aggregate, so the text appropriately identifies sensitivity to the original common-centering restriction.

The five-fold construction trains on eight and tests two responses per existing cell. Its fixed seed, participant-level summation before interval calculation, and lack of full-data/source initialization in training folds are correctly stated. The manuscript now expressly notes that the location models were motivated by examining these data, so these scores are not selection-adjusted or externally validated generalization estimates.

The numerical repair is accurately documented. Three original shifted CV fits failed objective nesting despite nominal convergence. The final rule uniformly adds the same-training-fold unshifted solution with zero centers to all 300 shifted CV fits. The initial outputs remain archived. Final fits pass all 300 CV and 60 full-data nesting comparisons; a gradient certificate alone is not presented as establishing this.

The count-table deviances 1218.809584 and 1212.293178 for the shifted families are correct. Nominal chi-square references are not overclaimed as exact calibrated rejection tests. The report preserves the relevant finite-boundary counts and explicitly does not certify unrestricted global optima.

## 5. Resolved wording corrections

Two substantive wording corrections were sent to the manuscript owner and are present in the current text:

1. **Units of log-SD bounds.** The original draft said log-SD bounds were in 100-ms units. In the actual fitter, SD is measured in milliseconds; only the center coordinates are internally divided by 100 ms. Section 4.1 now states the correct units.
2. **What the nested start guarantees.** The original appendix implied that an unoptimized zero-shift point was independently retained as an eligible final candidate. The implementation supplies that point as a start, selects among optimized endpoints, and then checks final nesting. Appendix A.3 now describes that actual procedure.

The updated wording “all four response families” also avoids implying four completely separate implementations where the four families share a common independent Python fitter.

## 6. Interpretation boundaries

The source-parameter probability-equivalence counts and errors in Section 5 match the root's theorem illustration. The text explicitly preserves the task/condition threshold policy in the constant-sensory-variance counterpart. It does not conflate that counterpart with changing criterion noise while fixing all thresholds, or claim to prove that actual participants used decision noise.

The predictive comparison is not against the exact counterpart. This distinction is essential: two pointwise-equivalent marginal families cannot be separated by refitting or by the current held-out marginal scores. The paper also correctly distinguishes the source-centered illustrations from future observations and does not turn prospective model-generated joint responses into human measurements or a power calculation.

The current data do not contain simultaneous paired task responses, shared-draw verification, independent criterion/lapse measurements, or a neural mediator check. The paper properly keeps its proposed paired-readout result conditional. Claims about sensory localization, experiential structure, UCT, or AI consciousness are not empirically established by this reanalysis.

## 7. Portability and third-party materials

All six current empirical Python scripts use their own directory and the preserved empirical/inputs/ directory or local result paths. The BCI runner imports the sibling root_analysis/fit_response_models.py. It does not require the old scratch empirical folder. Both the direct final-rule runner and the historical repair runner are present.

**Portability item resolved:** the optional self_check() input path now points to the record's empirical/inputs/ directory. The original 8,812-byte fitter is preserved in history/execution_source/fit_response_models.py with execution hash 6f616f9065b9641df92eb6d50288474a3cf3b88a9212520374cde8119d1696b6. The current 8,821-byte file has hash 397aaf7711160314176a8703340844c55ab58becdf02a2de94d337b734bc46f4. RELOCATION_PROVENANCE.json confirms the one path change, identical ASTs for all nine likelihood/fitting functions, and identical whole-module ASTs after removing self_check. The old execution summary and its source_model_sha256 are unchanged.

Both score audits now verify the current source and the preserved execution source against this provenance and the unchanged core AST. The independent audit also reads its canonical counts from the record-local original workbook rather than the old external tidy CSV. The optional self-check and both stored-score audits pass after relocation; no fit or CV partition was regenerated. Old audit scripts and receipts are retained in history/pre_relocation/. The self-check's inherited prospective-CV wording is a historical note; the actual final rule is unambiguously defined by the canonical runner and the execution-plan/nesting-repair records.

The current license metadata check found:

| Material | Observed public metadata |
|:--|:--|
| Article | CC BY 4.0 |
| BCI code project s5p4v | Explicit license relation to CC BY 4.0 |
| Separate data project ytga5 | No assigned node license in the inspected API metadata |

Evidence is in empirical/author_inventory/LICENSE_METADATA_CHECK.json, s5p4v_node_metadata.json, s5p4v_license.json, and ytga5_node_metadata.json. The earlier absence of a license in the data-node record must not be generalized to the code project. The package may still omit complete MATLAB files, PDFs, EEG archives, and extracted full articles because the independent Python implementations run without them. Retain their stable URLs, hashes, source attribution, and any original licensing notices. Do not apply a new blanket license to third-party source files.

The empirical reports and reproduction inputs are now sufficient for the manuscript's core empirical results, with all fitting outputs and the superseded run preserved. This review does not assess final PDF layout or replace author approval and external peer review.
