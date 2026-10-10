# Independent scoped review: cross-task proportional and monotone width analysis

**Date:** 10 October 2026.  
**Reviewer role:** independent internal AI-assisted literature/compatibility reviewer. This is not external peer review.  
**Review state:** theoretical results, named predecessor compatibility, all 13 new nodes, all four new rules, all seven new context links, and the supplied manuscript have been read. Final file-level results and hashes appear in §7.  
**Disposition:** retain as a conditional methods plus empirical secondary-analysis working paper. Do not promote the completed UCT map, discharge open phenomenal/application premises, or describe a null result as a demonstrated physical shared clock.

## 1. Materials and actual scope

Read in detail:

- `theory/THEORETICAL_RESULTS.md`: proportional equivalence; sharp uniform log correction; rectangular-uncertainty corollary; strict common-order representation; nondecreasing closure and sharp correction; counterexamples; UCT boundary.
- `empirical/analysis_plan.json`, `empirical/results/published_widths_summary.json`, `empirical/results/count_model_plan.json`, the original-fit portion of `count_model_summary.json`, and `empirical/fit_count_clock.py`. The initial numerical review preceded completion of the bootstrap. The supplied manuscript was subsequently read with its final recorded LR of 73.81345 and 199-replicate tail estimate of .105; this reviewer did not rerun that bootstrap and does not certify numerical results from inspection alone.
- R197, R200 and R201 research notes and candidate node/rule declarations; SCU-PAPER-v1.0.1 and its archived `MAP_EXTENSION.json`; the SCU R201 effective-correction note and overlay.
- The named R168/R169/R174/R175/TO and root ontology node statements in the actual published MGTD attachment and completed baseline graph.
- D’Angelo main article and complete supplement; the original primary literature recorded in `PRIMARY_LITERATURE_AUDIT.md` and `NOVELTY_AUDIT.md`, especially Yarrow et al. (2023).

The mathematical arguments were independently reconstructed, rather than inferred from a PASS receipt. The reported 729-matrix and 4,392,225 candidate-comparison computation was inspected as a recorded check, not rerun by this reviewer. No complete semantic re-review of all historical proofs is claimed.

## 2. New result-by-result review

The theorem labels below refer to the theory manuscript, not to established UCT map nodes.

| New result | Simultaneous premises | Review outcome and interpretation ceiling |
|---|---|---|
| Proposition 1: proportional equivalence | One participant; fixed two task meanings; finite common condition set; all widths positive; one stimulation-invariant multiplier per task. | Correct. Log additivity, constant task log differences and vanishing 2×2 multiplicative minors are equivalent. Two tasks × three conditions impose two independent restrictions. None of this identifies a neural oscillator. |
| Theorem 1: `epsilon_prop = range(d)/4` | Unweighted uniform error on every log-width cell; both task offsets and all condition offsets freely chosen; same finite table throughout. | Correct lower bound and attaining centered construction. The budget is a **uniform allowance**, not a claim that every cell actually requires the maximum correction. This is classical Chebyshev approximation in a specified two-row model. |
| Rectangular interval corollary | Every log cell lies in a jointly justified rectangle; freely selectable coordinates inside that rectangle; no omitted covariance constraint claimed. | Correct minimum discrepancy over that rectangle. It is an outer uncertainty-set calculation. Six marginal 95% intervals are not automatically a simultaneous 95% rectangle. A positive lower certificate requires valid joint coverage. |
| Proposition 2: strict common monotone representation | Stable strictly increasing task maps; a common scalar per condition; exact population values; positively fixed orientation. | Correct iff both task rows have the same weak ordering including exact ties. Positive orientation is an extra hypothesis, not supplied by C1. A successful representation does not imply one physical cause. |
| Theorem 2: sharp common nondecreasing-order distance | Uniform log-cell correction; one common order; free nondecreasing task maps; finite condition set. | Correct: for a fixed order, half the largest preceding inversion is necessary and the running maximum construction attains it; minimize over permutations. This is the closed-model distance. Zero distance need not supply an exactly strict representation when tie patterns differ. |
| Two-task opposed-pair closed form | Exactly two rows; same uniform loss and no externally fixed condition order. | Correct. Necessity follows from correcting at least one side of each discordant pair. Ordering by the sum of the two row values gives the sufficient bound. More than two tasks would require a separate argument. |
| Hierarchy `epsilon_mon <= epsilon_prop` | Same observed table, same uniform log loss, positively monotone class contains proportional class. | Correct. It compares model classes, not two amounts of neural change or two experience distances. |
| Optional monotone calibration gap | One globally feasible nondecreasing function; independently valid simultaneous interval anchors; fixed `x<y`; endpoint support/range conventions stated. | The interval `[max(0,L(y)-U(x)), U(y)-L(x)]` follows from ordered interval extension. Missing outer constraints may yield unbounded extrema. It supplies no actual experiential anchors. R168/R175/R201 are close antecedents and must remain credited. |

The four main counterexamples are appropriate: nonlinear monotone maps can violate proportionality; reversed task ranks can violate the stable positive common-coordinate model; condition-dependent maps remove the restriction; and averaging can erase subject-specific proportional failure. They do not assign experiences to hypothetical systems.

## 3. Exact ontology, inference and predecessor compatibility

| Inherited node or module | Required restriction | Audit judgment for the reviewed theory |
|---|---|---|
| `A:D_ONTIC`, `A:VIEW`, `A:ESTIMATE` | Complete constitutive organization, an investigator’s finite view and its estimate are different sorts. Equal estimates do not establish equal views or complete types. | Preserved if `W` denotes a declared response-law functional and `W_hat` its estimate. Neither is `D_ontic`. The latent `tau` is a parameter in a measurement model, not an admitted physical token or complete signature. |
| `A:C1` | Tokenwise correspondence applies to admitted actual complete `P/I/K` organization and an independently meaningful experiential interpretation. | No derivation from C1 to positive widths, proportionality, monotonicity, width direction or tACS mediation appears in the reviewed proof. Those assumptions are stated separately. |
| `A:C1_OI`, `A:C1_W` | Complete physical-type equivalence is required for full experiential equivalence. | Shared fitted widths or a fitted scalar do not satisfy that premise. A width discrepancy is not automatically a complete-type discrepancy. |
| `A:U1` | Basal experience of admitted actual tokens is not gated by prediction, control, report, metacognition or this statistical fit. | Preserved. No width threshold or model fit is made a consciousness-existence test. |
| `A:U2` | Quotient-valued organization/experience continuity uses justified same-signature maps/metrics. | The logarithmic discrepancy is not relabeled as an experiential metric or imported into U2. |
| `R168:SHARP_METRIC_ENVELOPE` | Geometry, regularity, valid tested bounds and their physical applicability are premises; sharpness is relative to an information class. | Compatible. The new sharp correction is a distinct finite model calculation; it does not derive an actual metric, derivative or Lipschitz constant. |
| `R169:ACTUAL_ROUTE_GRAPH_CONTRACT`, `R169:LOCAL_CHANNEL_UPPER_CERTIFICATE` | Actual executable edges and simultaneous upper budgets must be independently supported. | Current tACS/width data do not discharge these. No actual carrier/consumer graph is reconstructed from a width matrix. |
| `R169:METRIC_SCALE_GAUGE_NONENTAILMENT` | Numerical fit cannot identify separate scale factors without calibration. | Consistent: task ratios are invariant to positive rescaling only, and are not general affine or arbitrary monotone invariants. |
| `R169:HELDOUT_CALIBRATION_FALSIFIER`, `R169:ROUTE_CALIBRATION_TRIAGE` | Validity failure, calibrated-budget failure, certification and unresolved application are distinct. | Preserved provided the statistical rejection is described as failure of a specified measurement-model conjunction. It is not proof of no route or no experience. |
| `TO20261008:GLOBAL_CLOCK_COMPATIBILITY` | Additive edge-reference consistency requires a fixed comparison graph and vanishing oriented cycle sums. | Distinct mathematical object. The new width factorization does not instantiate or replace that “clock” result. |
| `R174:SHARED_TEMPORAL_COORDINATE` | Actual same-episode use of the reference/comparison variable by both named consumers. | Not established by two task widths recorded in separate blocks/sessions. Within-participant pairing is not same-episode consumer identity. |
| `R175:ORIENTATION_ANCHOR_PACKAGE`, `R175:HELD_OUT_ORDER_PREDICTION` under R176 correction | Two independently admitted correspondences orient supplied full chains; this alone does not predict independently named held-out content. | Preserved. The optional calibration appendix explicitly requires anchors and does not infer them from task success or from its own desired interpretation. |
| `R197:SIGNED_RELIABILITY`, `R197:UNSIGNED_LABEL_SWAP`, `R197:EVIDENCE_TARGET_SEPARATION` | Signed semantics/reliability must be independently supported; endpoint modality or agreement cannot supply it. | Positive monotone orientation is a model premise. Neither endpoint nor common factor is claimed to self-anchor experiential semantics. |
| `R200:SIGNED_FALLIBLE_ENDPOINT`, `R200:CLASS_CONDITIONAL_TRANSPORT`, `R200:SEMANTIC_CALIBRATION_FIREWALL` | Report, intended target, marker, use, evidence for use and transport remain distinct. | Preserved. Ownership judgments and simultaneity judgments remain different response tasks; no-report or AI transport remains unavailable. |
| `R200:FORMATION_USE_NONENTAILMENT` | An interaction alone does not identify the selected experiential target or route. | The task × stimulation interaction is treated as a model restriction, not direct evidence for a particular self-related feeling. |
| `R201:ROBUST_TARGET_SIGN_CERTIFICATE`, `R201:ACTUAL_USE_EVIDENCE_FIREWALL` | Independent endpoint sign, residual budget, class-specific drift bounds and actual-use stratum required jointly. | Current width data do not estimate or certify these quantities. The new sharp distance does not replace them. |
| `R201:STRICTNESS_COUNTERMODELS` and `R201:r_strictness_witnesses`, effective SCU correction | Original `rho=1,b=.1` examples are infeasible; coherent witness worlds retain separate bindings and do not prove arbitrary-budget sharpness. | Correction read and retained. No new result depends on the withdrawn tuples. |
| `SCU20261010:VALID_PROBES`, `SCU20261010:PURE_DOMAIN`, `SCU20261010:OR_DOMAIN` | Independently controlled source ports, fixed consumer class, exact readout, chronology and preparation. | The original SCU probe-optimality theorems do not apply directly to this human tACS dataset. No logarithmic or singleton probe claim is used as an empirical premise here. |
| `SCU20261010:ACTUAL_BINDING`, `SCU20261010:TRANSPORT_CONTRACT`, `SCU20261010:H_BRIDGE`, `SCU20261010:C8` | C1 structural interpretation requires actual complete binding; a named feeling requires its separate bridge. | Remain open. A statistical common scalar does not discharge actual source equality, intake identity, prediction chronology or `H`. |
| MGTD same-instance and status discipline | AND within a rule’s complete premise route; alternatives separated; context is nondeductive; presence in a graph is not truth or actual discharge. | The new module must remain disabled and bind participant, task, condition, endpoint model and uncertainty set in every relevant rule. A counterexample world must not also be required to satisfy the premise it violates. |

No contradiction with these inherited commitments was found at the reviewed scope. That judgment is conditional on retaining the stated ceilings in the final manuscript and candidate.

## 4. Empirical conclusions that are and are not supported

The source-width summary yields a mean ownership-minus-simultaneity log-ratio contrast of approximately `-0.01456`, a 95% t interval `[-0.09334, 0.06421]` and `p=.708` for the 8 Hz / 13 Hz comparison. This is a test of a necessary mean implication for **published fitted widths**. It does not establish equality in every participant. The reported 25/30 matching rank orders and observed individual correction budgets are descriptive fit diagnostics, not noise-corrected counts of participants with one or multiple underlying mechanisms.

The ±10%, ±20% and ±30% equivalence margins are disclosed as sensitivity scenarios. They must not be called independently justified experience thresholds or prospectively registered substantive equivalence bounds. Source fitted-width uncertainty is absent; the empirical branch correctly refuses to transplant uncertainty from a differently estimated count model when individual-level alignment cannot be demonstrated.

The additional count analysis declares a binomial Gaussian-response model with free amplitudes and centers and either shared or task-specific within-person frequency gains. Its null is properly nested within the alternative’s width family under the supplied parameter bounds. The code keeps estimates from the source fitting procedure and the separately specified count model separate. They are not assumed interchangeable; different fits alone do not prove that their underlying estimands must differ. Conditional trial independence, curve shape, positivity bounds, available aggregate counts and optimizer behavior remain model assumptions. A parametric bootstrap calibrates a test under that fitted null model; it does not independently validate the model’s sensory or neural interpretation. The chi-square reference is approximate, particularly with bounded parameters and ten trials per cell.

The primary plan is retrospective. An analysis choice fixed before its own inferential computation is not a prospective preregistration of a new human experiment. The original participants, stimulation and data collection belong to D’Angelo and colleagues.

## 5. Findings that must be reflected in the final write-up

1. **RR-01 — Original individual covariation exists.** Cite D’Angelo Supplement Fig. S7. It already reports cross-task within-person intervention-effect correlations. State the new stronger restriction without claiming that the original paper only tested means.
2. **RR-02 — Width is not a unique integration or neural-clock measure.** Cite Yarrow et al. (2023), DOI `10.1037/xhp0001154`, with the exact locators in `NOVELTY_AUDIT.md`. Strategic judgment changes can affect simultaneity-function width. Call the measured quantity psychometric response width.
3. **RR-03 — Mathematical originality is an application claim.** Credit Bamber, Prince, Kalish and Stout. The new equations are transparent exact specializations, not a new general state-trace or partial-identification method.
4. **RR-04 — Positive fitted discrepancies are not automatic latent violations.** Observed `epsilon>0` includes fitting error; use uncertainty or retain descriptive status. A null mean or nonsignificant likelihood test is not proof of the strict individual hypothesis.
5. **RR-05 — Rejection targets a conjunction.** Failure can reflect proportionality, positive orientation, task-map stability, response criteria, psychometric shape or additional paths. It does not uniquely select the failed assumption or refute all BCI/shared-alpha models.
6. **RR-06 — Two levels are not two new empirical experiments.** Proportional and monotone distances are computed from the same data. Their agreement is not independent corroboration. An optional anchor appendix has no new experiential calibration data.
7. **RR-07 — Complete binding remains open.** The data do not supply selective efference-copy/proprioceptive consumer intervention, actual common port use, complete token structure or a nonreport transport calibration.
8. **RR-08 — Uniform-budget wording.** Replace any phrase implying every cell must actually change by the maximum correction. At least one cell reaches the optimum’s maximum; others may require smaller or zero change.

These are scope and presentation requirements, not grounds to suppress an informative negative secondary result. The current theory manuscript already satisfies most of them; the exact original-study and Yarrow citations require prominent retention.

**Revision readback:** the theoretical author reports—and the revised text contains—both requested wording repairs: a uniform per-cell budget rather than a required actual correction in every cell, and a population width parameter distinguished from its fitted estimate. Yarrow’s metadata and strategy limitation were added. The reviewer also verified the 2025 erratum `10.1037/xhp0001226` (missing factor 2 before `l` in four source equations); the new paper does not reproduce those equations, and the substantive width/strategy citation remains appropriately scoped.

## 6. Completed-map structural check and preserved debt

The baseline file is `source_archives/UCT_DVC_SCU_DOI_Increment_20261010/reproduction_baseline/UCT_EFFECTIVE_GRAPH.json`, SHA-256:

`0973600f1be5cf21614592ca901112b26f9f0c9f6df36294a5dbb049efcf7612`.

Observed census: 913 nodes, 424 active conditional rules, 261 nondeductive contexts and 10 suspended historical rule IDs, totaling 1,608 review records. This reviewer checked active-rule ID uniqueness and resolved every `all_of` and conclusion node reference; no missing node reference or duplicate active rule ID was found. The graph records `scientific_premise_promotion=false` and `named_phenomenal_application_status=OPEN`.

This is a structural and selected-core compatibility check. It is not a claim to have freshly reviewed 1,608 proofs or discharged all historical source-depth obligations. The current state’s inherited depth ledger (1,034 IDs, 1,828 fields and 1,347 proof IDs) is retained as a historical debt record, not recomputed or reduced by this review.

The following remain open without alteration:

- `QC-20261008-10`: the positive independently justified phenomenal bridge;
- `IA-QC11`: relevant actual lineage/binding application;
- `QC-20261008-12`: actual-use versus use-evidence/application obligation;
- `QC-20261008-13`: actual bearer/interval/complete-signature/target admission;
- `SCU-OPEN-R191-NORMALIZATION` and `SCU-AUDIT-DEPTH`;
- the separate EIP normalization qualifications and all disabled pending checkpoints.

No DOI, release promotion, canonical-graph mutation, animal/human experiment or user-facing claim of consciousness validation is authorized by this report’s PASS at its stated scope.

## 7. Actual candidate and manuscript review

Reviewed candidate: `uct_repo/research/uct-agent-consciousness-workspace/records/CTD20261010_Cross_Task_Intervention/MAP_EXTENSION.json`. Reviewed manuscript: the same record's `manuscript/testing-a-shared-temporal-scale-v0.1.0.md`. Exact SHA-256 values and the machine-readable structural checks are saved in `CANDIDATE_REVIEW_RECEIPT.json`; they identify the version actually read and must not be carried to an edited file without another readback.

### 7.1 Every new node

| ID | Actual conjunction or scope checked | Verdict |
|---|---|---|
| `CTD:DOMAIN` | One participant, two positive endpoints, common finite conditions, fixed estimator/meaning, parameters separate from fits. | Correct finite mathematical domain; no actual biological membership asserted. |
| `CTD:MULTIPLICATIVE_CLASS` | Positive factorization and a condition-invariant task factor define a candidate class. | Correct; a neural common cause alone does not imply the class. |
| `CTD:MONOTONE_CLASS` | One scalar, stable strictly increasing maps, positive orientation; closure separately permits plateaus. | Correct; tie exception is retained. |
| `CTD:UNCERTAINTY_BOX` | Same-cell simultaneous nonempty finite log rectangle; no silently retained coupling; probability coverage separately required. | Correct conditional uncertainty domain. “Independent” here concerns freely selectable coordinates in a Cartesian product, not a claim that stochastic estimates are independent. |
| `CTD:PROPORTIONAL_DISTANCE` | Domain and multiplicative definition with one uniform log metric. | Exact formula independently reconstructed; scope is mathematical approximation. |
| `CTD:BOX_DISTANCE` | Domain, simultaneous rectangle and proportional distance bound to the same six or finite set of cells. | Correct lower discrepancy over the stated rectangle, not a supplied empirical confidence result. |
| `CTD:ORDINAL_DISTANCE` | Stable positive orientation, finite conditions, strict versus closure distinction; the proportional-class comparison uses R3's added premise. | Correct. Both the operative rule and the node's prose `all_premises` now explicitly include the proportional-distance premise for the inequality. |
| `CTD:COUNTEREXAMPLES` | Four separately scoped witness constructions, including the explicit two-person population example. | Correct with the revised R4 binding; no witness is required to satisfy the assumption that it refutes. |
| `CTD:DATA_PROVENANCE` | Original bytes, column mapping and publisher cross-check. | Properly typed observed data context. Counts do not become independent people or actual source/consumer identification. |
| `CTD:RELEASED_ESTIMATE_RESULTS` | Paired fitted-estimate mean, descriptive individual distances, missing source-estimator uncertainty. | Properly typed secondary observation. The printed precision is a computation record, not a claim of equivalent measurement precision. |
| `CTD:COUNT_MODEL_RESULTS` | Declared likelihood, free nuisance shapes, restricted widths, fixed fitted nulls, conditional independence and 199 simulated repetitions. | Correctly scoped separate analysis. It does not inherit original BCI semantics or quantify released-width errors. Numerical verification belongs to the computation audit. |
| `CTD:INFERENCE_CEILING` | Model, intervention assumptions and measurement assumptions remain conjoined; C1/U1 remain axioms. | Preserves actual type ≠ finite view ≠ estimate ≠ report ≠ selected experiential endpoint. No basal-experience gate. |
| `CTD:PROSPECTIVE_BRIDGE` | Independently bound actual consumer/time, independent endpoint calibration, direct-path and learning bounds, held-out distinct predictions. | Appropriate proposed contract; all empirical discharge remains open. |

The data and result nodes' quantifiers were made explicit in the final readback: the source node quantifies all mapped Experiment 3 cells and 30 participant rows; the result nodes quantify the declared paired or joint 30-person analyses while separately labeling individual descriptive statistics. No mixed-person deduction uses that metadata.

### 7.2 Every new rule and context

| ID | Premise route or context | Verdict |
|---|---|---|
| `CTD:R1` | `DOMAIN AND MULTIPLICATIVE_CLASS → PROPORTIONAL_DISTANCE`. | Full mathematical definition route; the model is defined, not asserted to be biologically true. |
| `CTD:R2` | `DOMAIN AND UNCERTAINTY_BOX AND PROPORTIONAL_DISTANCE → BOX_DISTANCE`. | Correct simultaneous same-cell binding; no covariance or coverage conclusion smuggled in. |
| `CTD:R3` | `DOMAIN AND MONOTONE_CLASS AND PROPORTIONAL_DISTANCE → ORDINAL_DISTANCE`. | Correct after adding the proportional-distance premise needed for the comparison inequality. |
| `CTD:R4` | Domain and both model definitions → four countermodels. | Correct after revision: separate witness worlds, within-witness identity, explicit two-person cancellation quantification, and no stable-map assumption imposed on the drift witness. |
| `CTD:CTX1` | Provenance supplies released estimates. | Nondeductive, appropriate. |
| `CTD:CTX2` | Provenance supplies aggregate counts. | Nondeductive, appropriate. |
| `CTD:CTX3` | Proportional formula has a descriptive data application. | Nondeductive; empirical output not used as a theorem premise. |
| `CTD:CTX4` | Ordinal formula has a descriptive data application. | Nondeductive; point estimates not converted into latent rejection. |
| `CTD:CTX5` | Inference ceiling refers to existing `A:C1` as an axiom-status context. | Target exists in the actual baseline; direction and `deductive:false` do not assert a proof of C1. |
| `CTD:CTX6` | Inference ceiling refers to existing `A:U1` as a no-gate context. | Target exists; no null/model-fit threshold is made an existence criterion. |
| `CTD:CTX7` | Inference ceiling leaves prospective actual calibration open. | Correct nondeductive research context. |

Structural check: 13 node IDs, four rule IDs and seven context IDs are unique; no candidate node collides with a baseline node; every rule premise, conclusion and context endpoint resolves. Every new node has `automatic_premise_truth=false` and `enabled_as_established_premise=false`. Every rule remains disabled and has `actual_premises_discharged=false`. All contexts are nondeductive. None of the three empirical-record/result nodes is used as an `all_of` premise by any new rule. Both module-level enabled fields are false, and no baseline file was edited by this reviewer.

### 7.3 Issues found and revision readback

- **CR-01, resolved:** R3 originally omitted the proportional-distance dependency while its conclusion included an inequality against that distance. The actual revised rule now contains `CTD:PROPORTIONAL_DISTANCE`.
- **CR-02, resolved:** R4 originally inherited a generic one-participant, stable-map binding. The actual revised rule explicitly separates its four witness domains and allows the drift example and two-person cancellation example their stated premises.
- **CR-03, resolved:** two literal `;qquad` tokens in Proposition 1 were corrected to proper LaTeX spacing commands.
- **CR-04, resolved:** §7 now calls the future extension a “prospective design contract” rather than asserting that its hardware feasibility has been established.
- **CR-05, resolved packaging check:** the candidate's relative proof references to `empirical/results/count_model_summary.json`, `empirical/results/source_data_crosscheck.json`, `empirical/fit_count_clock.py` and `review/ROOT_NUMERICAL_VERIFICATION.json` all exist in the reviewed final record. Their checksums are in the receipt. The recorded count summary matches the manuscript's final LR 73.81345, chi-square reference p=.10837 and 199-replicate bootstrap p=.105.

The final reviewed candidate SHA-256 is `27f5ee9afbab13f8652b6eded67745c2b0a5ab2272c79ece92f18c9f6b1bdedc`; the final reviewed manuscript SHA-256 is `b91cee9210ce07f7ea513679d718ce9dc39078046aabf68f20a86fe797491ffd`. These refer to the source Markdown and JSON read in this audit, not a subsequently rendered PDF or package archive.

**Final manuscript readback:** the uncertainty corollary now explicitly states that it minimizes the proportional distance over all log-width tables inside the supplied rectangle. Section 5.3 says the separately fitted estimates are not assumed interchangeable with the source estimates, without inferring that different fitting procedures necessarily imply different underlying estimands. Two `\Needspace` commands address pagination only and do not change a scientific claim; the rendered PDF layout was not checked by this reviewer. The candidate bytes are unchanged. The prior reviewed manuscript SHA-256 `3e08b1761677882267322702ca4efe24ecfb8e0f4a42380a45cf9aa9e25adfdc` is retained as review history in the receipt. No numerical analysis or literature review was rerun for these final wording edits.

The manuscript fairly credits D’Angelo's existing cross-task intervention correlations and nonlinear BCI comparison, state-trace and isotonic precedents, and Yarrow's width/strategy limitation. It explicitly declines to identify a shared physical clock, infer a source-consumer route from tACS, or arbitrate broad UCT/IIT/GNWT/HOT labels. The count model and released estimator are separately declared. Its main result is a well-scoped nonrejection, without converting that into exact equivalence or independent replication.

**Final scoped disposition:** **PASS for a disabled conditional-methods and retrospective secondary-analysis candidate**, with relative-file packaging checked separately in the receipt. This is not external peer review, a source-author endorsement, completed-graph promotion, a new human experiment, proof of a neural clock, or empirical validation of a phenomenal bridge. The existing open scientific and source-depth debts remain open.
