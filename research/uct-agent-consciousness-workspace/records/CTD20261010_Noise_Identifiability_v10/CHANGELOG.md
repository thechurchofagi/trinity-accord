# CTD v1.0.0 change record

Research version: CTD-RESULT-v1.0.0. Manuscript version: CTD-PAPER-v1.0.0. Date: 10 October 2026. This record prepares the user's authorized methods and retrospective secondary-analysis preprint. Readiness is an internal decision, not a completed publication or external peer-review receipt.

## From v0.2 to v1.0

The response-model identification paper now contains an executable finite-sample confidence procedure for its prospective paired-response contract. A Clopper–Pearson probability interval is projected through the complete calibrated Gaussian model. The result covers the entire true-calibration population identified set, and hence the generating shared variance, with at least the nominal probability under the stated contract. Equal-variance endpoints are explicit, and unequal variances are projected analytically without a nuisance covariance grid. Empty, full-domain and constant-readout cases are distinguished.

The calibration extension uses the complete union over a valid nuisance region to give coverage at least 1-alpha-gamma. The implementation supplies exact finite calibration unions and the continuous case where only the criterion-correlation bound is uncertain. General certified projection over arbitrary continuous multi-parameter regions remains open. Clopper–Pearson intervals, Gaussian probability identities, confidence-set projection and the union bound are inherited principles; no new general statistical framework or shortest-interval result is claimed.

The dated finite_sample/ANALYSIS_PLAN.json fixed 480 dimensionless scenarios before calculation. All three threshold/lapse profiles, four paired sample sizes and five generating variances are retained. Exact finite-binomial enumeration supplies 240 valid cases and 240 labeled controls, without Monte Carlo draws, selected participant examples or new human observations. Minimum point and complete-set coverages in the valid grid are 0.9502345621 and 0.9501514695. Widths remain broad: at 4,096 pairs, fixed-grid means are .37723 for independent criteria and .49036 for kappa=.2. These are model-grid operating characteristics, not human power estimates or sample-size recommendations.

Figure 4 displays every profile. Controls separately address a wrong criterion bound, independent sensory resampling and shared lapse/guess events. The resampling target is per-task variance while actual shared covariance is zero. Empty-set width zero is reported alongside emptiness and width conditional on nonemptiness; an almost-always-empty set is not presented as precise estimation.

## Corrections and verification

Expanded unequal-variance checks found a floating-point endpoint and label issue for exactly full-domain projection. Module version 1.0.1 adds an analytic full-domain guard. The original module and execution remain in history. One short rerun of the unchanged plan leaves the CSV byte-identical, all 124 stored arrays exactly identical and all summary values unchanged except time and runtime. CORRECTION_REEXECUTION_RECEIPT.json records this. No original response fit or conditional symmetry simulation was rerun.

The text now explicitly normalizes kappa-one intervals as a/v and C/v, states the valid-grid empty probability as less than .024862, and restricts second-order sensitivity to zero total correlation, or zero shared variance under independent criteria. Figure 4's footer overlap was repaired with separate legend and note rows. The current pre-release draft has four figures and 21 pages; final document verification and release identifiers remain the coordinator's responsibility.

## Retained findings and open issues

The v0.2 likelihood/IC audit, 180-width reconstruction attempt, conditional centering test, bounded four-family comparison, marginal implementation counterpart and population paired-readout proofs remain unchanged scientific evidence. Corrected source IC arithmetic still favors Sigma in aggregate. Two descriptive widths, original chronology, source optimization execution and bootstrap/VBA history remain unresolved.

The first shifted CV run remains superseded because three fits violated training nesting. The uniform same-training-fold repair and all failed records are retained. The final shifted Sigma-minus-Prior held-out difference remains -60.884594527 NLL, a restricted retrospective response-model comparison rather than proof of a sensory locus.

Human same-internal-sample routing, common-center calibration, independent lapses, an independently justified criterion-dependence bound, prospective replication, an anatomical mediator and an experiential bridge remain open. FAILURES.md and the claim ledger retain these limits.

## Preservation and release boundary

The six earlier root metadata files are preserved exactly under history/v0.2_release_metadata/. ANALYSIS_INTENT.json remains the unchanged historical plan; its earlier no-publication commitment is not edited to manufacture a different history. The current user authorization is separate.

CTD2 retains 20 nodes, 7 rules and 13 nondeductive contexts. CTD3 adds 5 nodes, 2 rules and 6 contexts. All 53 candidate items remain disabled. UCT-MAP-v1.1.2, inherited open obligations and semantic-audit debt are unchanged.

These metadata assert no DOI, OpenTimestamps, archive or persistence success. Older receipts remain tied to their historical versions. Actual current-release outcomes require separate verified coordinator receipts.
