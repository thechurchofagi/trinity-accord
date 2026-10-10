# CTD v0.2 development log

User explicitly requested deeper work on this unpublished paper. Base d9773d7; v0.1 files remain frozen. Initial questions and analysis commitments are in ANALYSIS_INTENT.json.

## Initial findings

An additive baseline in a four-parameter Gaussian recovers the first ownership width to approximately 0.0014 ms; all 180 widths remain to be checked. The public BCI master contains a possible information-criterion sign inconsistency; helper definitions and published values must be checked before interpreting it.

## Completed development and scientific decisions

The initial likelihood and estimator questions are now completed within their stated scope. The released BCI positive NLL is reconstructed at all 60 parameter vectors. Every reported IC difference is traced to a second sign negation; corrected AIC/BIC still favor Sigma in aggregate. This is an arithmetic and reporting correction, not a reversal of the principal winner. The original bootstrap/VBA inference is not claimed reproduced.

The Gaussian reconstruction reaches 178/180 widths within 0.1 ms with two unresolved cases and substantial probability-domain failures. This supports its use as a descriptive width estimator only. A parameter-free symmetry test over 540 signed pairs yields T=984.304236; none of 19,999 conditional replicates exceed it (plus-one p=.00005). The rejected class is centered independent-binomial responding, not every BCI account.

Four response families were fitted with explicit bounds and fixed reconstructed within-cell five-fold partitions. The first execution's three nesting failures were diagnosed, preserved and uniformly repaired using same-training-fold unshifted starts for every shifted fold. The final held-out losses are Sigma 5465.166346, Prior 5427.816041, Sigma-shift 5238.549911, Prior-shift 5299.434505. All 720 archived fitted records and 360 nesting comparisons were checked; independent probability/NLL audits agree to floating-point precision. Full-data and CV initialization have different documented admissibility rules. The comparison is retrospective, conditional and not independent replication.

A constant-sensory-variance criterion implementation reproduces all 1,260 source marginal probabilities, maximum gap 2.22e−16. It retains the source threshold trajectory; this does not show that changing criterion jitter alone with every policy parameter fixed reproduces the experiment. The exact Gaussian ambiguity is inherited; the source-calibrated construction and audit are this application.

Complete conditional results now establish identification from one added population joint probability under calibrated centers and independent criteria/lapses, a sharp set under bounded jointly Gaussian criterion correlation, and weak centered identification near zero shared variance. Correlated lapses, resampled internal evidence, imperfect centering and unbounded criterion dependence remain explicit defeaters. No paired human data exist in the source experiment.

## Manuscript, reviews and prior art

The 18-page English paper includes three scientific figures, full proofs and eleven references. Theory, empirical execution and literature/source-arithmetic were reviewed in separate internal AI-assisted passes. Required corrections were applied and checked; the reviews are not external peer review. The final PDF hash and complete page-render review are recorded in review/PDF_QA.json. Close prior work on criterion variance, bias, BCI and noise identification is explicitly credited. Broad mathematical or exhaustive first-priority claims are withheld.

The publication decision is WORTH_EXTERNAL_REVIEW_AS_METHODS_AND_SECONDARY_ANALYSIS_MANUSCRIPT. It rests on reusable empirical corrections, exact implementation counterparts and conditional measurement limits, not on length, graph growth or a consciousness assertion. MANUSCRIPT_DECISION.json answers the seven mandatory contribution questions. The original published SCU preprint remains distinct from this unpublished CTD revision.

## Formal scope, concurrency and preservation

The completed map remains UCT-MAP-v1.1.2. All 1,608 baseline structural items are visited and their records match the earlier receipt. The new CTD2 candidate has 20 nodes, 7 conditional rules and 13 nondeductive contexts, all disabled. Full historical semantic reproof is not completed; 1,034 IDs / 1,828 fields / 1,347 proof-ID debt and every inherited OPEN label remain. C1/U1 and actual-to-phenomenal bridge premises are unchanged.

Concurrent A3M commits a9bf0dc9 and 2faccb45 were fetched and fast-forwarded before navigation edits. The full stable master version 82 was materialized rather than overwriting from the older version 80. The A3M H objective is preserved independently. New CTD v0.2 fields point to a separate record; frozen v0.1 and all historical published bytes remain unchanged. Exact save versions, readbacks and commit IDs belong in PERSISTENCE_RECEIPT.json after those actions succeed.

## Portability and next question

Original fitting execution sources and hashes are preserved; the relocated fitter's numerical function ASTs agree. The symmetry loader is made record-local without rerunning its stored Monte Carlo results. The paper reproduction package excludes only contextual large source papers, EEG archives and layout scratch files, with omitted-file provenance retained. Failed or superseded numerical runs remain included.

Further extension of descriptive statistics is not needed to make this manuscript concrete. The next empirical advance requires independently validated same-internal-sample readouts, center/threshold calibration and an external bound on criterion or lapse dependence. The selected bodily familiarity H and a physical R≠L intervention remain open in the preserved A3M main line.
