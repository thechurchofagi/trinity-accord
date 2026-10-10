# CTD v0.2 — Identifiability of Noise Sources in Bodily Judgments

**Hongju Liu · 10 October 2026**

This is the complete paper and reproduction record for CTD-PAPER-v0.2.0 / CTD-RESULT-v0.2.0. It is a revision of the unpublished CTD paper, with a new response-level identification focus. It is not a new journal publication, a new DOI, a human paired-report experiment, or a completed admission to the UCT formal graph.

Read the English PDF in manuscript/ first, followed by HANDOFF_ZH.md for the Chinese research handoff. MANUSCRIPT_DECISION.json states the publication-value judgment and its limits.

## Main findings

- The public BCI likelihood is reconstructed at all 60 saved parameter vectors. A sign discrepancy in the information-criterion calculation is traced through every publisher source-data row. Correcting it retains the aggregate Sigma preference.
- The independent-binomial centered response family fails a parameter-free conditional symmetry check: T = 984.304236, 19,999 conditional draws, plus-one p = 0.00005.
- Under the final fixed within-cell five-fold procedure, Sigma + task centers predicts better than Prior + task centers: held-out NLL 5238.549911 versus 5299.434505; total difference −60.884595. This is retrospective conditional prediction, not independent replication.
- A constant-sensory-variance, variable-criterion implementation preserves all 1,260 original marginal cell probabilities to floating-point precision, with the source's threshold trajectory retained.
- A prospective paired response identifies shared variance only under the specified Gaussian, common-internal-sample, calibrated-center, independent-criterion, and lapse premises. Bounded criterion correlation gives a sharp interval, and the centered inverse is weak near zero shared variance.

The generic Gaussian variance ambiguity, location-bias models, and joint-noise identification have close prior literature. The new contribution is the concrete audit, application, and conditional additional-measurement boundary. No empirical sensory locus, experiential scale, UCT-specific support, or AI-consciousness result is claimed.

## Directory guide

| Path | Contents |
|---|---|
| manuscript/ | Complete English manuscript, PDF, LaTeX source, preamble |
| empirical/inputs/ | Three unchanged public workbooks |
| empirical/results/bci_response/ | Final full fits, 600 training fits, partitions, scores, diagnostics |
| empirical/results/pre_nested_cv_repair/ | Superseded first CV execution; never use its scores as final results |
| empirical/ | Width reconstruction, four-model runner, historical repair, plans and reports |
| root_analysis/ | Independent likelihood, source-response twins, figure builder, execution-source verification |
| theory/ | Complete proofs, conditional symmetry analysis, theorem checks, independent score audit |
| literature/ | Source arithmetic audit, prior-art comparison, independent CV review, licensed source-code snapshot |
| history/ | Exact original execution source and pre-relocation audit history |
| review/ | Internal technical reviews and final PDF quality record |
| governance/MAP_EXTENSION.json and governance/MAP_AUDIT.md | Disabled candidate claims and precisely scoped formal review |

Original research papers and EEG archives were inspected as background where available but are not redistributed here. Their retrieval URLs and hashes are preserved in provenance records. Some reports retain paths from the analysis session as historical evidence; runnable input defaults are relative to this record.

## Reproduce the calculations

Use Python 3.12 with requirements.txt. The recorded versions are in RUNTIME.json. From the extracted record root:

~~~bash
python -m pip install -r requirements.txt
python literature/reconcile_source_bci.py
python root_analysis/instantiate_response_twins.py
python theory/check_bci_identification.py
python empirical/audit_bci_execution.py
python theory/audit_response_comparison.py
~~~

These commands check the released arithmetic, exact probability counterparts, theorem calculations, and all stored final scores without refitting. They may refresh derived audit files in the working copy; retain the original ZIP or Git commit as the frozen edition.

To regenerate the new analyses:

~~~bash
python empirical/reconstruct_gaussian_widths.py
python theory/test_source_symmetry.py
python empirical/run_bci_response_comparison.py
python root_analysis/make_figures.py
~~~

The final runner includes the same-training-fold unshifted start for all shifted fits. Running the separate historical repair is unnecessary when executing this final runner. Floating-point optimization may yield small platform-dependent differences; archived parameter vectors permit deterministic likelihood readback independently of refitting.

The source-fitter self-check is optional:

~~~bash
python root_analysis/fit_response_models.py --self-check
~~~

Its input path has been made portable. The actual original fitting source is retained in history/execution_source/; RELOCATION_PROVENANCE.json and RELOCATION_VERIFICATION.json show that the likelihood and fitting functions are unchanged. The historical source_model_sha256 in execution outputs has not been rewritten to conceal that packaging change.

## Build the paper

The PDF is already supplied. To rebuild it, install Pandoc and XeLaTeX with the Latin Modern and DejaVu fonts, then run:

~~~bash
python root_analysis/build_paper.py
~~~

Figures are standard Matplotlib PDF/PNG artifacts. Every page of the delivered 18-page PDF was rendered and visually inspected; review/PDF_QA.json records the checked edition.

## Numerical repair and unsuccessful results

Three first-run shifted Sigma CV fits had training losses worse than their contained unshifted fits, despite successful convergence flags. The uniform training-only nested-start repair corrected all shifted folds. All remaining 60 full-data and 300 CV nesting comparisons pass. The pre-repair records and decision are retained.

Free-baseline Gaussian least squares nearly reconstructs 178 of 180 source widths at 0.1-ms tolerance, with two unresolved cases. Its curves need not be lawful probabilities. The bounded independent Prior fit also differs slightly from the saved source optimum, partly because of a near-one prior outside the declared logit box. The paper preserves these limits.

## Scientific and publication status

The manuscript is judged to have sufficient substance for a methods and secondary-analysis preprint or research note. That judgment is based on explicit, auditable findings and internal technical review. External peer review, human author approval, and venue-specific declarations remain separate steps. No new DOI-backed preprint release, journal submission, or external communication was performed in this revision. Research checkpoint storage is recorded separately.

The UCT completed map remains v1.1.2; all CTD2 candidate items are disabled. The v0.1 record and concurrent A3M research remain preserved. FILE_MANIFEST.json fixes this scientific record; a later PERSISTENCE_RECEIPT.json documents successful saves and readbacks without circularly including itself in the frozen scientific manifest.

## Attribution

The original experiment and its data are the work of D'Angelo, Lanfranco, Chancel, and Ehrsson, Nature Communications 17:53 (2026), DOI 10.1038/s41467-025-67657-w. See THIRD_PARTY_NOTICES.md for distinct source licenses and attribution. No new blanket license is applied to third-party materials. AI-assisted preparation is disclosed in the manuscript; the internal reviews are not external peer review.

The governance/build_map_candidate.py builder requires the preserved full research repository and its pinned map capsule. It is a governance-history tool, not a standalone scientific reproduction command. THEORY_INPUT_RELOCATION_PROVENANCE.json records the final symmetry input-loader change; the original Monte Carlo output and its execution hashes remain unchanged.
