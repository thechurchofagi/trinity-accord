# Literature, novelty, and causal-interpretation review of CTD v0.2

**Reviewer role:** internal AI-assisted literature and methodological review, not independent external peer review.

**Manuscript:** `ctd_v02/manuscript/noise-identifiability-bodily-judgments-v0.2.0.md`, title *Identifiability of Noise Sources in Bodily Judgments*.

**Initial readback anchor after the first two wording fixes:** SHA-256 `6d0c845516d8e75453980e1d2f76c9aa367fab2edb53913de5bbebb0e9f25aa0`. The full manuscript and appendices were read. Date: 2026-10-10.

## 1. Overall assessment

This version has a defensible methods and secondary-analysis contribution. Its strongest result is a connected, reproducible audit of one published observer family: exact saved-fit reconstruction, a verified information-criterion discrepancy with the aggregate winner preserved, a conditional check of a mandatory response restriction, a limited predictive repair, and an exact implementation ambiguity that survives relative predictive success. The conditional joint-readout result gives a constructive consequence rather than ending at a generic warning about identifiability.

This is sufficient substance for a carefully scoped preprint or methodological research note after the textual corrections below. It is not a new general noise-decomposition theory, a validated human measurement protocol, a new neural intervention, or a discrimination of UCT from other consciousness theories. The current title and article-type description are broadly appropriate. Journal acceptance and the human author's approval remain separate matters.

The repaired held-out result should be stated positively and fairly: within the fixed artificial count-partition procedure, the location-extended noise-varying family predicts better than its prior-varying counterpart. The exact decision-side counterpart then shows why that positive response-model result still does not identify a sensory implementation. The manuscript largely preserves this distinction and does not turn the arithmetic issue into an unsupported claim that the original experiment was invalid.

No additional broad literature search, flexible model expansion, or discretionary optimization is needed to support this narrow paper once the specific items below are corrected. A future empirical paired-report study is a different project.

## 2. Required wording corrections

| ID | Location and issue | Required correction | Status at anchored readback |
|---|---|---|---|
| L1 | Section 4.1 originally described log standard deviations as using 100-ms units. The fitter logs sigma measured in ms; only location parameters use 100-ms internal units. | State natural logarithms of standard deviations measured in milliseconds in [-10, 10]. | Fixed in anchored readback |
| L2 | Appendix A.3 originally claimed that the unoptimized zero-location nested point was retained as an eligible candidate, guaranteeing the optimizer could not discard it. The fitter only retains optimized results from each start. “Unshifted optimum” also implied more than established. | State that the same-training-data unshifted fitted solution is used as a zero-location start and every retained shifted fit is checked against its nested objective. No further numerical run is needed because the final nesting checks pass. | Fixed in anchored readback |
| L3 | Section 7 says the sensory-change and decision-change packages make different predictions for both marginals and joint responses. The exact counterparts deliberately have equal marginals. | State that the exact counterparts have different prospective joint probabilities under independent criteria, and broader packages need restrictions to distinguish their prediction sets. | Fixed in final readback |
| L4 | Reference 9 uses a broad series description in place of the three actual publication titles. | Supply the verified titles and versions below, or retain only the UCT work actually needed for the cited statement. Keep their theoretical-preprint status. | Fixed in final readback |
| L5 | Appendix A.3 says “All four independent likelihood implementations.” The principal code is one parameterized fitter with four response families; other independent checks are reported separately. | “All four response families use analytic derivatives checked against finite differences.” | Fixed in final readback |

The abstract's “centered-extension noise family” was also flagged as unclear: “noise-varying family with task-specific centers” states the model directly. This is a clarity edit rather than a new scientific condition.

## 3. Primary-source attribution and closest prior art

The manuscript now places the most relevant precedents in the main argument. Their contribution is not hidden in a general literature paragraph.

| Primary source | Exact close precedent and inspected location | Assessment of the present attribution |
|---|---|---|
| Yarrow et al. 2011, DOI 10.1016/j.concog.2011.07.003 | Journal p. 1525 / author PDF p. 8 explicitly gives sensory-plus-criterion flank variances, the nonunique decomposition, and the sensory upper bound; p. 1521 explains latency/criterion location ambiguity. | Appropriate to cite directly for the moving-center construction; the manuscript does so. |
| Yarrow et al. 2023, DOI 10.1037/xhp0001154 | Author manuscript Appendix A, pp. 57–59, provides Gaussian sensory/criterion covariance and composite parameters. Equal perfectly correlated criteria give the exact moving-center special case. | Appropriate recognition of a direct algebraic ancestor rather than a vague conceptual precursor. |
| Yarrow 2025 correction, DOI 10.1037/xhp0001226 | PubMed PMID 41325147 reports four missing factors of 2 before the half-lapse parameter l. The inspected manuscript's corresponding formulas are Eq. 1, A5, A12, A17. | Reference 3 includes the correction and explicitly defines the new lambda convention independently. The cited variance argument does not depend on the erroneous lapse factor. |
| Cabrera, Lu, and Dosher 2015, DOI 10.1037/a0039348 | Institutional PDF pp. 8–10 / manuscript pp. 7–9 explains which response/agreement constraints fail to separate noise and how confidence-category joint covariances add information. | The present theorem is correctly described as a specialized paired interval result with different assumptions, not the first joint-response repair. |
| Chancel, Ehrsson, and Ma 2022, DOI 10.7554/eLife.77221 | Figure 2—figure supplement 4 (`fig2s4`) already introduces BCIbias with a nonzero location; main model comparison distinguishes noise-adaptive criteria from a fixed-criterion alternative. | Section 4 fairly attributes the location extension. Section 5 correctly retains the source's condition-specific threshold policy in its twin. |
| Hahn, Wang, and Wei 2026, DOI 10.1073/pnas.2601013123 | Sections 1.1–1.3 establish positive and negative identification results in a smooth continuous-estimation family, including multiple small noise levels. | Section 5.2 correctly restricts the external-noise counterexample to the specified additive interval family and does not contradict the broader positive literature. |
| Plackett 1954, DOI 10.1093/biomet/41.3-4.351 | Classical Gaussian probability derivative supporting the rectangle calculation. | Appropriate mathematical attribution; the two-sided centered readout is not mislabeled as ordinary one-sided tetrachoric regression. |

Full retrieval URLs, page-level notes, and the detailed inherited-versus-new matrix are in `ctd_v02/literature/V02_NOVELTY_AND_PUBLICATION_AUDIT.md`. No assertion that all potentially similar prior work has been exhaustively excluded is warranted or required.

## 4. References 9–11: titles and publication status

These entries were checked against recovered title pages, published-file receipts, the earlier SCU audit, and the archived CTD file. This was a focused bibliographic check, not a repeat of the complete UCT research-tree audit.

### Reference 9

All three DOI records are associated with actual recovered versions. The exact bibliographic items are:

- Liu, H. (2026). *Unified Consciousness Theory I: Structural–Experiential Identity and the Continuity from Physical Process to Conceptual Self*. Version 1.2. Zenodo theoretical preprint. DOI 10.5281/zenodo.23131575.
- Liu, H. (2026). *Unified Consciousness Theory II: Consciousness Theories as Effective Organization Theories*. Version 1.1. Zenodo theoretical preprint. DOI 10.5281/zenodo.23030320.
- Liu, H. (2026). *Unified Consciousness Theory III: Organization, Intelligence, and Experience—From Inorganic Processes to Artificial Agents*. Version 1.0. Zenodo theoretical preprint. DOI 10.5281/zenodo.23137088.

Their title pages explicitly identify them as theoretical preprints rather than peer-reviewed articles. The current paper uses their commitments as conditional background and does not treat their DOI deposits as validation of C1 or of a measurement bridge. That use is appropriate.

### Reference 10

The title *Matched Behavior and Source Use*, version 1.0.1, DOI 10.5281/zenodo.23272690, matches the SCU publication record. The manuscript's updated description as a Zenodo methodological preprint, not externally peer reviewed, is accurate. Its finite independent-source-control assumptions are not silently transferred to the human experiment.

### Reference 11

The exact title *Testing a Shared Temporal Scale Across Bodily Judgments*, CTD-PAPER-v0.1.0, matches the archived manuscript. Git commit `6cbbde9e1cec7374bb104d603044900c0baad149` exists. The entry explicitly says this version is unpublished; it does not invent a DOI, journal, or external validation. Retaining that status is essential.

## 5. Numerical and model-interpretation checks

The following findings were independently checked during this review role; they are not simply copied from the root author's headline summary.

1. **Source likelihood and IC reconciliation.** The three raw workbooks, scalar source predictor, and both NLL helpers reproduce saved objectives; the wrong-sign IC expressions reproduce all 30 publisher Figure S2 rows. Corrected sums are Delta AIC = -127.8591597 and Delta BIC = -370.2744424. The aggregate winner is preserved. The full source audit records the fixed-parameter count issue and other execution-history discrepancies separately.
2. **Centered symmetry.** The independent-binomial conditional hypergeometric analysis and its nuisance elimination were inspected. The test is valid for the stated observation law, without fitting a BCI parameter. It cannot attribute the departure to one psychological cause, and it is not a distribution-free protection against serial dependence.
3. **Initial CV failure detected.** Three shifted Sigma training fits violated the nesting invariant by large objective margins although optimizer flags passed. That was a concrete numerical failure, not a scientific preference for rerunning an unfavorable comparison.
4. **Uniform repair and independent final scores.** All 300 shifted fits were repaired under the same training-only rule. A separate direct signed-CDF evaluation reproduced the final 600 saved probability and held-out-score records to maximum errors 5.55e-16 and 3.55e-13, respectively. Every training-plus-test count matches its original cell. Remaining training-nesting violations are zero. Full-data fits and unshifted CV records are unchanged.
5. **Final comparison.** Shifted Sigma minus shifted Prior held-out NLL is -60.8845945; mean participant difference -2.0294865; descriptive conditional t interval [-3.2676238, -0.7913492]; 21 of 30 participants favor shifted Sigma. The manuscript uses this corrected result rather than the superseded -3.494 initial difference.
6. **Finite bounds.** The new prior-logit and lapse bounds do not include every released source parameter unchanged. The exact original-parameter reconstruction and bounded refits are properly separated. Boundary convergence is not claimed to certify global optimization.

The supporting receipts are `ctd_v02/literature/source_bci_reconciliation.json`, `CV_NESTING_REVIEW_INITIAL.json`, and `CV_NESTING_REVIEW_FINAL.json`. Rechecking these concrete invariants is sufficient for the present review; it would be inappropriate to describe this as certification of every possible optimization risk.

## 6. Causal and experiential interpretation

The following important boundaries are present and should survive final editing:

- Stimulation effects on measured reports, relative response-model prediction, absolute response-law adequacy, and physical implementation attribution are separate questions.
- The response twin retains the threshold trajectory and does not claim that jitter alone varies while every decision parameter is fixed. It is not relabeled as the original normative Bayesian observer with an unchanged sensory-likelihood interpretation.
- The joint theorem needs a common calibrated center, known marginals and lapses, one shared internal sensory realization, and independent criteria/lapse processes. Same physical stimulation and two questions do not establish those premises.
- Central paired observations discard covariance sign; the correlated-criteria theorem correctly takes the union of feasible branches and gives a sharp set. Unknown criterion-correlation tolerance cannot be estimated freely from the same sole joint statistic while retaining its identifying role.
- A population joint probability requires repeated observations. The n to the minus one quarter scale concerns the variance parameter under known calibration, not a standard deviation or a universal required sample size.
- Source-derived joint profiles come from the original centered observer family. Figure 2 already states that this family fails the centering check, the joint observations were not collected, and the illustration is not validated power analysis. Differing fitted task centers are not silently assumed to align at one physical zero SOA.
- UCT is kept outside the title and abstract's affirmative scientific claims. A fitted variance, finite view, or reported endpoint is not equated with complete actual physical organization or a phenomenal structure. No empirical support unique to C1 or an AI-consciousness conclusion is asserted.

The Section 7 marginal-versus-joint wording correction is needed to keep this otherwise consistent account intact.

## 7. Publication-value judgment

The new mathematical content is primarily a careful specialization of established ideas, supplemented by an explicit covariance sensitivity set and weak-identification analysis. The strongest original component is the source-specific empirical and computational evidence chain. The reconstruction audit, necessary-condition test, corrected predictive comparison, and exact alternative implementation together answer a concrete question that the original restricted Sigma/Prior comparison did not answer.

This is a credible contribution at the level of a rigorous methods/secondary-analysis preprint. It should not be advertised as a decisive consciousness-theory breakthrough or a demonstrated sensory–decision separation in humans. The current manuscript is substantially more publishable than a paper centered on an arbitrarily strong proportional-width bridge because its target is the released observer and its actual data, its favorable and unfavorable results are both retained, and its proposed measurement has an explicit falsifiable contract.

**Review limitations:** this review covers text, source attribution, causal interpretation, selected proofs, and specified numerical invariants. It does not include final PDF pagination or figure rendering, an exhaustive semantic revalidation of the UCT graph, independent human ethics assessment, new experimental data, or a guarantee of external peer-review acceptance.

## Final readback

**PASS for the review scope above.** The final manuscript readback has SHA-256 `33736a01e3b84e0d8f70b9c853b64df39051e45d1cac9572e145495c367fd8cd`. All five listed corrections are present. Section 7 now distinguishes exact equal-marginal counterparts from broader packages; the formal titles and preprint statuses in references 9–11 are accurate; and the numerical-method wording matches the checked code and retained fit records.

No further scientific calculation is requested by this review. Final figure/PDF rendering and human author review remain outside this role's completed scope. If later edits change substantive claims, this hash-specific receipt should not be represented as review of those unseen changes.
