# CTD / TA-TR-2026-26 v1.0.0 — Identifiability of Noise Sources in Bodily Judgments

**Hongju Liu · 10 October 2026**

This is the paper and reproduction record underlying the first public edition, CTD-RESULT-v1.0.0 / TA-TR-2026-26 v1.0.0. It combines the archived v0.2 response-model audit with an explicit finite-sample confidence-set construction. Publication metadata and exact DOI-bound files are maintained in the separate release record; a working source placeholder is not a published DOI. The archived v0.1 and v0.2 editions remain unchanged in their original repository records. Historical copies in this package retain their old status labels and are not the current release decision.

Read the v1.0.0 English manuscript first. The final DOI-bound PDF, citation files, release manifest and publication receipts identify the public edition. No new human paired-report experiment or completed admission to the UCT formal graph is claimed.

## Main findings

- The public BCI likelihood is reconstructed at all 60 saved parameter vectors. A sign discrepancy in the information-criterion calculation is traced through every publisher source-data row. Correcting it retains the aggregate Sigma preference.
- The independent-binomial centered response family fails a parameter-free conditional symmetry check: T = 984.304236, 19,999 conditional draws, plus-one p = 0.00005.
- Under the final fixed within-cell five-fold procedure, Sigma + task centers predicts better than Prior + task centers: held-out NLL 5238.549911 versus 5299.434505; total difference −60.884595. This is retrospective conditional prediction, not independent replication.
- A constant-sensory-variance, variable-criterion implementation preserves all 1,260 original marginal cell probabilities to floating-point precision, with the source's threshold trajectory retained.
- A prospective paired response identifies shared variance only under the specified Gaussian, common-internal-sample, calibrated-center, independent-criterion, and lapse premises. Bounded criterion correlation gives a sharp interval, and the centered inverse is weak near zero total correlation (near zero shared variance under independent criteria).

- Exact binomial confidence-set projection propagates finite-sample and bounded criterion-correlation uncertainty; 480 prespecified synthetic scenarios include 240 valid observation contracts and 240 deliberate assumption violations. This is not a human power calculation.

The generic Gaussian variance ambiguity, location-bias models, and joint-noise identification have close prior literature. The new contribution is the concrete audit, application, and conditional additional-measurement boundary. No empirical sensory locus, experiential scale, UCT-specific support, or AI-consciousness result is claimed.

## Directory guide

| Path | Contents |
|---|---|
| manuscript/ | Complete English source template and preamble; the DOI-bound PDF/Markdown are the separate primary release assets |
| empirical/inputs/ | Three unchanged public workbooks |
| empirical/results/bci_response/ | Final full fits, 600 training fits, partitions, scores, diagnostics |
| empirical/results/pre_nested_cv_repair/ | Superseded first CV execution; never use its scores as final results |
| empirical/ | Width reconstruction, four-model runner, historical repair, plans and reports |
| root_analysis/ | Independent likelihood, source-response twins, figure builder, execution-source verification |
| theory/ | Complete proofs, conditional symmetry analysis, theorem checks, independent score audit |
| literature/ | Source arithmetic audit, prior-art comparison, independent CV review, licensed source-code snapshot |
| history/ | Exact original execution source and pre-relocation audit history |
| review/ | Internal technical reviews and final PDF quality record |
| governance/MAP_EXTENSION.json and governance/MAP_AUDIT.md | Preserved CTD2 disabled candidate and prior review |
| governance/CTD3_MAP_EXTENSION.json and governance/CTD3_MAP_AUDIT.md | New finite-sample disabled candidate and scoped compatibility review |
| finite_sample/ | Complete confidence-set proof, implementation, fixed plan, exact binomial tables, controls and numerical checks |

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
python finite_sample/run_operating_characteristics.py
python finite_sample/check_confidence_sets.py
~~~

These commands check the released arithmetic, exact probability counterparts, theorem calculations, and all stored final scores without refitting. They may refresh derived audit files in the working copy; retain the original ZIP or Git commit as the frozen edition.

To regenerate the new analyses:

~~~bash
python empirical/reconstruct_gaussian_widths.py
python theory/test_source_symmetry.py
python empirical/run_bci_response_comparison.py
python root_analysis/make_figures.py
python finite_sample/make_finite_sample_figure.py
~~~

The final runner includes the same-training-fold unshifted start for all shifted fits. Running the separate historical repair is unnecessary when executing this final runner. Floating-point optimization may yield small platform-dependent differences; archived parameter vectors permit deterministic likelihood readback independently of refitting.

The source-fitter self-check is optional:

~~~bash
python root_analysis/fit_response_models.py --self-check
~~~

Its input path has been made portable. The actual original fitting source is retained in history/execution_source/; RELOCATION_PROVENANCE.json and RELOCATION_VERIFICATION.json show that the likelihood and fitting functions are unchanged. The historical source_model_sha256 in execution outputs has not been rewritten to conceal that packaging change.

## Build the paper

The exact DOI-bound PDF is supplied separately in the same public record. This reproducibility archive is frozen before the one-time DOI reservation, so its manuscript source retains the explicit __DOI_RESERVED_AT_RELEASE__ token. To recreate the typesetting, install Pandoc and XeLaTeX with the Latin Modern and DejaVu fonts, then run:

~~~bash
python root_analysis/build_paper.py
~~~

Figures are standard Matplotlib PDF/PNG artifacts. To edit the separately published DOI-bound Markdown, place it at the extracted archive root so its figures/ links resolve; the source template in manuscript/ uses ../figures/ instead. The exact DOI-bound PDF is rendered and visually inspected before release. The prior 18-page v0.2 quality record is historical; the final-release visual review pins the current PDF hash.

## Numerical repair and unsuccessful results

Three first-run shifted Sigma CV fits had training losses worse than their contained unshifted fits, despite successful convergence flags. The uniform training-only nested-start repair corrected all shifted folds. All remaining 60 full-data and 300 CV nesting comparisons pass. The pre-repair records and decision are retained.

Free-baseline Gaussian least squares nearly reconstructs 178 of 180 source widths at 0.1-ms tolerance, with two unresolved cases. Its curves need not be lawful probabilities. The bounded independent Prior fit also differs slightly from the saved source optimum, partly because of a near-one prior outside the declared logit box. The paper preserves these limits.

## Scientific and publication status

The author explicitly requested finalization and DOI publication followed by OTS and Arweave preservation on 10 October 2026. The manuscript is released as a methods and retrospective secondary-analysis preprint after internal AI-assisted technical review. This status does not imply journal acceptance, independent external peer review, or final human line-by-line checking. The public release record separately reports DOI publication, anonymous byte readback, OTS Bitcoin verification, Arweave fees and anonymous archive readback. Never infer one of these states from another.

Finite-sample guarantees remain conditional on a correct paired observation and calibration contract. The complete historical UCT map audit remains AUDIT_INCOMPLETE, all CTD2 and CTD3 candidates are disabled, and the completed map remains UCT-MAP-v1.1.2.

The v0.1/v0.2 records and concurrent A3M/A3N research remain preserved. FILE_MANIFEST.json fixes the public scientific archive inventory; operational publication and persistence receipts are separate and are not inferred from this pre-reservation archive. Historical publication and persistence receipts, when retained under history/, describe their own earlier snapshots only.

## Attribution

The original experiment and its data are the work of D'Angelo, Lanfranco, Chancel, and Ehrsson, Nature Communications 17:53 (2026), DOI 10.1038/s41467-025-67657-w. See THIRD_PARTY_NOTICES.md for distinct source licenses and attribution. No new blanket license is applied to third-party materials. AI-assisted preparation is disclosed in the manuscript; the internal reviews are not external peer review.

The governance/build_map_candidate.py and governance/build_ctd3_candidate.py builders require the preserved full research repository and its pinned map capsule. It is a governance-history tool, not a standalone scientific reproduction command. THEORY_INPUT_RELOCATION_PROVENANCE.json records the final symmetry input-loader change; the original Monte Carlo output and its execution hashes remain unchanged.
