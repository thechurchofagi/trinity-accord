# CTD v0.2: skeptical novelty and publication audit

Date: 2026-10-10. Scope: a methods and secondary-analysis paper based on the public D'Angelo et al. Experiment 3 data, its released computational model, exact observer equivalences, and a proposed additional readout. This review does not authorize publication or submission and does not alter the frozen v0.1 record.

## Recommendation

The strongest defensible paper asks **what the released intervention-response data identify once model fit, observer-parameter interpretation, and latent implementation are separated**. A useful answer combines a reproducible source-model audit, a transparent check of its mandatory response constraints, and an explicit response-equivalent decision-side construction. A conditional paired-report measurement can then show what additional observable would identify one decomposition under stronger assumptions.

This is materially stronger than the original v0.1 emphasis on a strict proportional-width bridge, but it must be presented as a specialized application and empirical audit. Neither Gaussian noise convolution nor the general idea of using joint response covariance to separate noise sources is new. The nearest literature already makes those points explicitly.

The source-code/saved-fit arithmetic audit is complete. The centered-symmetry analysis and theoretical calculation code have been inspected and are compatible with their stated finite-model assumptions. The equally applied location extension and held-out comparison have now passed a corrected training-nesting and independent score audit, described below. Together these results can support a substantive, narrowly framed methods/secondary-analysis preprint, provided the final manuscript preserves the interpretation limits and prior attribution in this report. This is not a forecast of journal acceptance or a certification of all possible optimizer optima.

## 1. What changed from v0.1, and why it matters

The strict statement that two task widths have identical stimulation-induced log ratios is a mathematically definite auxiliary hypothesis, but it is not a required prediction of the source study's BCI observer, of Bayesian causal inference generally, or of UCT. Rejecting such a bridge is easy to overinterpret as rejecting a shared mechanism. A zero group-mean log-ratio difference also does not establish equality at the individual level.

The source-width reconstruction adds another reason to demote that line. The empirical lead reports that a four-parameter descriptive Gaussian, including a free baseline, almost exactly reproduces the released widths for 178 of 180 curves. A zero-baseline Bernoulli Gaussian was therefore not a faithful reconstruction of the original width-extraction family. This finding should correct the v0.1 narrative rather than be disguised as confirmation of it. Negative descriptive baselines in many fits explain why width-summary reproduction and full probability-model inference are distinct analyses.

The revised response-level question has a firmer target: the actual source probability function and its measured binary responses. It can demonstrate limitations that do not depend on choosing a new descriptive width convention.

## 2. Claim-by-claim novelty assessment

| Candidate claim | Closest established result | Appropriate status here |
|---|---|---|
| Sensory variance and Gaussian criterion jitter add in an interval-response curve | Yarrow et al. 2011, p. 1525; Yarrow et al. 2023, Appendix A | Inherited principle; do not claim a new general identifiability theorem |
| Marginal curves imply an upper bound on a common sensory variance | Yarrow et al. 2011 already gives an upper bound from composite flank variances | Specialized across-condition construction and sharp interval under declared common-component restrictions |
| Different sensory and decision implementations give exactly the same source BCI response curves at every SOA | The GLINC/AT-A-GLANCE construction provides the algebraic ancestor | A concrete embedding of the released BCI family, with its threshold trajectory retained, is a useful application |
| Joint response information can separate internal noise components | Cabrera, Lu, and Dosher 2015 uses multipass confidence covariances | Conditional paired interval-readout specialization, not the first covariance-based repair |
| A centered bivariate Gaussian rectangle is increasing in nonnegative latent correlation | Classical Gaussian integral identities, including Plackett 1954 | Elementary supporting lemma; cite the mathematical lineage |
| A location parameter relaxes a centered BCI response curve | Chancel, Ehrsson, and Ma 2022, Figure 2—figure supplement 4, already defines BCIbias | Source-lineage robustness check, not a new observer model |
| Source AIC/BIC contain a specific sign discrepancy | Exact reconstruction of original public code, fitted values, and Figure S2 | New, concrete source audit, with retained aggregate winner reported prominently |
| The centered source response family fails an absolute symmetry constraint in this dataset | Standard conditional binomial/hypergeometric inference | New data-specific secondary result, subject to count-independence and stationarity assumptions |
| Known external noise never identifies perceptual models | Contradicted as a general statement by Hahn, Wang, and Wei 2026 | Restrict to the declared additive sensing-plus-jitter family; no universal claim |
| The results discriminate UCT from other consciousness theories | No such numerical bridge is supplied by UCT or tested here | Unsupported; retain only a brief boundary statement |

Novelty therefore lies in the **specific source-family interpretation audit, verified empirical constraints, quantitative response twins, and explicitly limited additional measurement**, rather than in a new branch of mathematics or a new generic noise-separation method.

## 3. The closest primary precedents

### Yarrow et al. 2011: criteria, latency, and composite variance

**Full reference:** Yarrow, K., Jahn, N., Durant, S., & Arnold, D. H. (2011). Shifts of criteria or neural timing? The assumptions underlying timing perception studies. *Consciousness and Cognition, 20*(4), 1518–1531. https://doi.org/10.1016/j.concog.2011.07.003 .

Primary author PDF: https://www.psy.uq.edu.au/~uqdarnol/Derek_CV_files/Motor_Sensory_Recal_2011.pdf . Metadata: https://openaccess.city.ac.uk/id/eprint/340/ . Local copy: `primary_sources/Yarrow2011.pdf`.

**Exact locations inspected:** journal p. 1521 / PDF p. 4 discusses the ambiguity between latency differences and criterion positions. Journal p. 1525 / PDF p. 8, Equations 1–2 and adjacent paragraphs, writes flank variances as sums of sensory and boundary-criterion variances, explains that two measured variances do not identify three components, and gives the sensory-noise upper bound and criterion-variance difference. The study combines simultaneity and order judgments, although its response treatment is not the proposed pair of binary ownership/simultaneity interval judgments on a shared internal draw.

**Consequence for this paper:** the equation v = a + b and the bound a ≤ min v must be introduced as an application of established timing-observer reasoning. The new proof can make its assumptions exact and connect them to the released intervention family, but should not imply that previous literature only vaguely suspected a confound.

### Yarrow et al. 2023 and its 2025 correction: GLINC / AT-A-GLANCE

**Full reference:** Yarrow, K., Solomon, J. A., Arnold, D. H., & Roseboom, W. (2023). The best fitting of three contemporary observer models reveals how participants' strategy influences the window of subjective synchrony. *Journal of Experimental Psychology: Human Perception and Performance, 49*(12), 1534–1563. https://doi.org/10.1037/xhp0001154 .

Primary author PDF: https://kielanyarrow.github.io/MyPage/papers/StrategyAffectsSJWidth.pdf . Code overview: https://kielanyarrow.github.io/MyPage/Code.html . Local copy: `primary_sources/Yarrow2023.pdf`.

**Exact locations inspected:** author-manuscript PDF p. 10, lines 211–228; p. 12, lines 266–269; Appendix A, pp. 57–59. Appendix A allows sensory and criterion variables with a covariance matrix and describes composite variance parameters. With perfectly correlated equal-variance lower and upper criteria and sensory independence, the moving-center special case reproduces the present Gaussian convolution. The unequal-flank approximation in A3 has a stated breakdown and code fallback, so our exact special case should not be confused with a universal claim that its approximate formula is exact. The paper also empirically changes response strategy and demonstrates consequences for fitted synchrony widths.

**Consequence:** this is the closest conceptual and algebraic precedent. Cite it in the main statement of the response twin, not only in a general discussion paragraph. The fixed-baseline versus free-baseline reconstruction issue also makes its warning against interpreting arbitrary fitted widths directly especially relevant.

**Erratum:** “Correction to ‘The best fitting of three contemporary observer models reveals how participants' strategy influences the window of subjective synchrony’ by Yarrow et al. (2023).” *Journal of Experimental Psychology: Human Perception and Performance, 51*(12), 1708 (December 2025). https://doi.org/10.1037/xhp0001226 ; primary PubMed record https://pubmed.ncbi.nlm.nih.gov/41325147/ . The correction reports a missing factor 2 before l in four equations. In the inspected author manuscript, the corresponding lapse formulas are Eq. 1 (PDF p. 24), A5 (p. 59), A12 (p. 66), and A17 (p. 69). Their prose defines l as half the total lapse probability; the proper form is l + (1 − 2l)q. Our separate convention, lambda/2 + (1 − lambda)q, has lambda = 2l. The accessible correction abstract does not name the four equation numbers; that mapping is from direct manuscript inspection. The Appendix A composite-variance reasoning cited here does not rely on the incorrect lapse factor.

### Cabrera et al. 2015: covariance-based noise separation is established

**Full reference:** Cabrera, C. A., Lu, Z.-L., & Dosher, B. A. (2015). Separating decision and encoding noise in signal detection tasks. *Psychological Review, 122*(3), 429–460. https://doi.org/10.1037/a0039348 .

Primary institutional version: https://escholarship.org/uc/item/2dd1q6w9 ; PDF https://escholarship.org/content/qt2dd1q6w9/qt2dd1q6w9.pdf . Local copy: `primary_sources/Cabrera2015.pdf`.

**Exact locations inspected:** PDF pp. 8–10 / manuscript pp. 7–9, especially the comparison of categorical response and multipass agreement constraints with the additional confidence-category covariance constraints. Figure 4 illustrates noise configurations with matching marginal response characteristics but different joint covariances. The empirical task uses repeated external noise samples and multiple confidence categories. Repeating a physical stimulus is not the same assumption as reusing one internal sensory realization.

**Consequence:** say that the proposed paired interval readout is one specialized way to obtain a missing joint observable. Do not say that ordinary double-pass binary judgments automatically separate sensory and decision variance, or that the present work first discovers joint covariance as a solution. The present theorem's independent task criteria and shared internal draw are strong, substantive assumptions.

### Chancel et al. 2022: original body-ownership observer lineage

**Full reference:** Chancel, M., Ehrsson, H. H., & Ma, W. J. (2022). Uncertainty-based inference of a common cause for body ownership. *eLife, 11*, e77221. https://doi.org/10.7554/eLife.77221 .

Primary full text: https://pmc.ncbi.nlm.nih.gov/articles/PMC9555868/ ; publisher https://elifesciences.org/articles/77221 . Full-text XML: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9555868/fullTextXML . Local copy: `primary_sources/PMC9555868.xml`.

**Exact locations inspected:** Introduction's second aim; Results comparison of BCI and fixed-criterion (FC) models; Figure 2—figure supplements 1–4, especially supplement 4 (`fig2s4` in the XML). The study manipulates visual noise and contrasts a noise-adaptive Bayesian criterion with a fixed criterion. Its joint-task fit shares sensory parameters and lapses as a modeling assumption. The BCIbias variant already permits a nonzero mean asynchrony; its source dataset did not clearly favor that added parameter under the reported BIC comparison.

**Consequence:** our decision-side twin must carry over the condition-specific BCI threshold k, because that threshold itself changes with the effective noise scale. It is not equivalent to the source FC alternative with an invariant interval width. The source-lineage location variant should be named when reporting our robustness extension; no novelty should be assigned to adding a location parameter itself.

### Hahn et al. 2026: avoid a universal nonidentifiability conclusion

**Full reference:** Hahn, M., Wang, E., & Wei, X.-X. (2026). Identifiability of Bayesian models of perception. *Proceedings of the National Academy of Sciences, 123*(37), e2601013123. https://doi.org/10.1073/pnas.2601013123 . Published online September 11, 2026.

Primary full text: https://www.pnas.org/doi/10.1073/pnas.2601013123 ; https://pmc.ncbi.nlm.nih.gov/articles/PMC13578815/ .

**Exact locations inspected:** main text Sections 1.1–1.3, Equations 2–3 and the discussion of Theorems 3.1 and 3.3. In a smooth continuous-estimation framework, known loss permits recovery of encoding and prior in a small-noise regime; with unknown loss there can be prior/loss confounding. Response distributions from multiple small sensory-noise levels can identify most models in the specified family. The manipulation-to-noise mapping need not be known beforehand, but the manipulation must change the noise magnitude.

**Consequence:** our invariance to added Gaussian variance is a property of a particular additive sensing-plus-criterion-jitter family and its permitted decision rule. It neither contradicts their positive results nor shows that external-noise manipulations are generally useless. Their framework excludes or constrains alternatives that our counterexample explicitly allows; observables and decision families differ.

### Plackett 1954: Gaussian probability derivative

**Full reference:** Plackett, R. L. (1954). A reduction formula for normal multivariate integrals. *Biometrika, 41*(3–4), 351–360. https://doi.org/10.1093/biomet/41.3-4.351 . Primary publisher record: https://academic.oup.com/biomet/article-abstract/41/3-4/351/230622 .

The classical derivative of a bivariate normal CDF with respect to correlation underlies the four-boundary rectangle calculation. The two-sided centered interval problem is not literally ordinary one-sided tetrachoric regression. It is better to describe the result as a specialized Gaussian latent-correlation identification calculation than to invent a new general statistical principle.

## 4. Required mathematical boundaries

### Exact response twin

For a fixed participant, if the source fitted effective variance in condition f is v_f, choose a common sensory variance a with 0 ≤ a ≤ min_f v_f and set independent criterion-center variance b_f = v_f − a. Sensory error minus criterion-center error is Gaussian with variance v_f. The source probability curve is exactly reproduced when its task-and-condition threshold k_tf and lapse are retained.

This is an implementation ambiguity for the response family. It does not prove that any particular participant used criterion noise, that sensory uncertainty did not change, or that both descriptions are equally plausible given all possible neural evidence. It also does not turn a arbitrary threshold trajectory into the original Bayesian observer with sensory variance a: to preserve that interpretation one would need additional constraints relating decision thresholds to the new sensory likelihood and prior.

The twin remains valid when a calibrated location shift is included equally in the two descriptions. Therefore finding asymmetric source curves does not itself destroy the implementation ambiguity; the repaired response family must still be examined separately.

### One additional joint probability

At a calibrated common center, with positive finite interval widths, known marginal effective variances and known lapses below one, one scalar joint-yes probability identifies nonnegative shared variance if two reports use the same internal sensory draw and their criterion jitters and lapses are independent. The bivariate centered rectangle has an increasing dependence on nonnegative correlation.

The phrase “one additional probability” refers to a population observable estimated from repeated trials. It must never become “one trial suffices.” The derivative vanishes at zero shared variance, so small shared components are weakly identified; there is no automatic useful finite-sample precision. Marginal calibration, timing, reporting procedure, and the exclusion of shared decision or memory noise are parts of the model, not observations guaranteed by asking two questions.

If criterion covariance is allowed, the measured covariance contains the sum of sensory and criterion components and the separation generally fails again. Likewise, physically repeating the stimulus does not guarantee that the two reports share one internal draw. Source response asymmetry means that physical zero SOA cannot simply be assumed to be the calibrated common center.

### Added external noise

The counterexample persists when known independent Gaussian external noise contributes an additive variance to the same latent comparison and the permitted decision family preserves the same total-variance threshold trajectory. This scoped statement is exact. A universal statement about all external-noise experiments, all Bayesian observers, or all response-distribution measurements is not supported.

## 5. Empirical audit: what the emerging results establish

### Saved-fit information-criterion discrepancy — independently completed

See `SOURCE_BCI_AUDIT.md`, `source_bci_reconciliation.csv`, and `source_bci_reconciliation.json`. The source likelihood values and all 30 Figure S2 differences are reconstructed. Corrected summed Delta AIC is -127.8592, and Delta BIC is -370.2744. These correct the released -112.1408 and -354.5561 while retaining the aggregate Sigma preference. This is a specific new reproducibility result, not a reversal of the source paper's full conclusion.

### Centered-symmetry check — code and scope inspected

The released predictor necessarily has p(s) = p(-s). The analysis in `../theory/test_source_symmetry.py` tests this in 540 participant/task/stimulation/absolute-SOA pairs using conditionally independent Hypergeometric(20, K, 10) laws. It does not estimate a BCI parameter, use descriptive widths, or substitute a large-sample chi-square reference distribution. The observed aggregate deviance is 984.3042; no value among 19,999 planned null draws reaches it, giving a plus-one Monte Carlo p of 0.00005. The provided exact binomial uncertainty interval concerns Monte Carlo tail-probability estimation, not an effect-size confidence interval.

This rejects the centered independent-binomial response family conditional on its assumptions. Repeated-trial dependence, nonstationarity, or nonzero locations can violate that family. The test does not by itself attribute asymmetry to sensation, criterion position, stimulation, or a theory of body ownership. A group-average bias test and this simultaneous family test ask different questions: individual biases can matter even when group means cancel.

### Location and held-out robustness — corrected result independently checked

The completed follow-up adds exactly two task-specific locations, fixed across stimulation conditions, equally to both source candidate families. This is motivated by their shared mandatory centering restriction and by the BCIbias precedent, rather than by an open-ended model search. Five folds are formed by randomly allocating each cell's ten recorded binary outcomes into five held-out pairs, using a fixed seed.

| Response family | Sum of held-out NLL over 12,600 binary judgments | Nominal free parameters per participant |
|---|---:|---:|
| Sigma | 5465.166346 | 6 |
| Prior | 5427.816041 | 8 |
| Sigma with two stable task locations | 5238.549911 | 8 |
| Prior with two stable task locations | 5299.434505 | 10 |

The two location extensions improve their respective aggregate scores. After the extension, the Sigma-minus-Prior score difference is -60.884595, or -2.029486 per participant; its conditional descriptive participant t interval is [-3.267624, -0.791349], and 21 of 30 participant scores favor Sigma. This supplies positive relative predictive evidence for the effective-noise-varying family in the specified split procedure. The exact decision-side twin still limits its sensory implementation interpretation. These are compatible findings and should both be reported.

**A consequential numerical correction in our own workflow:** initial shifted Sigma fits violated nesting in three training folds despite passing optimizer status and projected-gradient checks. Their training NLL exceeded the unshifted submodel by 51.712, 50.513, and 99.666. A uniform numerical repair refitted all 300 shifted training fits, adding the corresponding same-training-fold unshifted fit with zero locations as an initialization. No full-data fit or held-out score selected individual reruns. The original run and the decision record are preserved. The initially reported shifted comparison (-3.494 total) is superseded and must not appear as the final scientific result.

After repair, an independent evaluation using the direct signed Gaussian-CDF expression, without importing the root fitter, reproduces all 600 saved probability/held-out-score records: maximum probability discrepancy 5.56e-16, maximum NLL discrepancy 3.56e-13, and no training-nesting violations. Full-data fits and unshifted CV records are unchanged. Receipts are `CV_NESTING_REVIEW_INITIAL.json` and `CV_NESTING_REVIEW_FINAL.json`.

**Finite computational bounds:** the independent fitter retains source log-sigma bounds but uses prior logits in [-16, 16] and lapses in [1e-8, 1 − 1e-8]. Clipping the original Prior-model start appreciably affects participant 6 before refitting. The new full-data Prior NLL is 0.034920 above the original saved total, while the Sigma total is slightly lower. Thus the independent refits should be described as explicitly bounded source-related fits; they do not prove that every original saved parameter vector was available to that optimizer or that global optimality was reached. The exact original-parameter likelihood reconstruction remains a separate result.

With only aggregated counts, these splits estimate prediction to exchangeable judgments at the same stimulus cells. They do not recreate original trial order, independently validate stationarity, or test generalization to new participants, new SOAs, or a new experiment. The displayed participant interval is conditional on this single artificial partition and fit procedure, not independent-replication evidence.

### Quantitative joint-readout illustrations

The 1,260 source-parameter marginal response probabilities in `../root_analysis/response_twin_summary.json` are reproduced by the constant-sensory-variance twin to floating-point precision. The proposed 90 joint-readout profiles and their simple-hypothesis error bounds are **model-derived illustrations**, not collected joint responses. They use the original centered parameter family, whose centering constraint fails the empirical check. They therefore must not be promoted to validated power calculations for these participants. Distinct fitted task locations also mean that one physical zero-SOA condition need not center both tasks; the centered joint theorem requires additional calibration or a modified measurement rule.

## 6. Minimum publication threshold and stopping rule

The revised paper is worth developing into a rigorous methods/secondary-analysis preprint if it contains all of the following:

1. Reproducible raw-count mapping, an explicit source likelihood, original-versus-recomputed objective checks, and separation of saved-fit arithmetic from independently optimized fits.
2. One clear absolute restriction test, its independent-binomial assumptions, a descriptive account of effect magnitude, and the source-lineage location robustness result.
3. An exact source-family response twin with the retained threshold trajectory explicit, demonstrated quantitatively using the released or independently refitted parameters.
4. A compact conditional additional-readout result, including lapse conventions, shared-draw and independence assumptions, centering, weak identification near zero, and a counterexample when criterion covariance is allowed.
5. Prominent attribution to Yarrow 2011/2023, Cabrera 2015, Chancel 2022, Plackett 1954, and the scoped comparison with Hahn 2026.
6. A conclusion proportional to the evidence: the data support a restricted response-model comparison and experimentally measured stimulation effects, while a specific sensory implementation remains unidentifiable in the larger stated family.

Do not continue adding broad reviews or unrelated consciousness theories once these points are settled. A concise, complete empirical-model audit with a constructive design implication has a clearer contribution than a long theory manifesto. A prospective paired-report experiment remains future work; its absence should limit empirical claims but need not prevent a transparent methods preprint.

## 7. Suggested title and central contribution wording

Possible title: **“What temporal-integration response curves identify: a computational audit and a conditional route to sensory–decision separation.”**

Suggested contribution wording: “We evaluate the exact response constraints and interpretation of a published alpha-stimulation observer model using its public counts, fitted parameters, and code. After reconciling its information-criterion calculation and testing a mandatory centering constraint, we construct sensory and decision-side implementations that preserve the model's complete marginal response curves. Building on established criterion-noise and joint-response methods, we derive the assumptions under which one added paired-response probability would identify a shared variance component.”

The manuscript must not describe this as the first proof that identical behavior can conceal different mechanisms, as a proof that sensory explanations are false, as a complete validation of a new human measurement procedure, or as evidence that uniquely supports UCT.
