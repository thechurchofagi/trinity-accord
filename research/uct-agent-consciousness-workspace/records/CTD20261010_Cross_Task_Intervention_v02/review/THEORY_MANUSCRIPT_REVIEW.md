# Theory and inference review of CTD v0.2

**Manuscript reviewed:** `ctd_v02/manuscript/noise-identifiability-bodily-judgments-v0.2.0.md`, complete main text and appendices, 10 October 2026. This is an internal technical review, not external peer review. No source, empirical, or manuscript file was edited by this reviewer.

**Final review status, 08:06:49 UTC:** the source-specific equivalence, centered paired inverse, second-order sensitivity, and sharp covariance set are mathematically sound under their complete Gaussian and calibration premises. The principal empirical quantities reproduce independently. The four required wording and premise corrections identified below have all been made by the parent author and independently confirmed by readback. No unresolved algebraic or numerical error was identified in the reviewed claims. The correction history is retained below so that the review does not conceal how the claims were tightened.

Readback manuscript SHA-256: `478b57f7a5345b109225ea379b30b4be3772629ebb5d81333c6556fcf21e45f2`. Later editorial edits may change this checksum.

## Required corrections, now resolved

### 1. Appendix A.3 describes an optimizer safeguard that is not implemented

The manuscript says that the zero-shift embedding is evaluated as an eligible candidate and therefore cannot be discarded. In `fit_one`, each start is passed to `minimize`, and only the optimized result is retained in `results`. The unoptimized starting objective is not separately retained as an eligible final candidate.

Replace that sentence with: **“The zero-center embedding is included as an optimizer initialization. Every resulting shifted full-data and training-fold objective was checked against its unshifted nesting reference, with no remaining violations.”** The repair did in fact pass all 60 full-data and 300 training-fold nesting checks. Thus the correction concerns the implementation claim, not a need to rerun the fits. Also prefer “unshifted fit” to “unshifted optimum,” since global optimization was not established.

### 2. Section 4.1 misstates the standard-deviation units

The phrase “log standard deviations in [−10,10] in 100-ms units” is incorrect. `probabilities_and_derivatives` computes `sd=exp(logsd)` and combines it directly with SOAs expressed in milliseconds. Only center parameters are optimized in 100-ms units and multiplied by 100.

Use **“log standard deviations, with σ expressed in milliseconds, in [−10,10]; … centers in [−800,800] ms, optimized in 100-ms units.”** This matters for reproducing the numerical domain and for distinguishing this observer from earlier rescaled width models.

### 3. Section 6.2 must explicitly retain joint Gaussianity

After relaxing criterion independence, merely requiring Gaussian marginal distributions and a covariance bound does not justify a bivariate-Gaussian rectangle law. The necessity direction of Theorem 3 and identification of absolute correlation both require joint Gaussianity of the criterion vector and independence of that vector from the sensory variable.

Insert at the start of Section 6.2: **“Retain the calibrated-center and lapse assumptions, and let (C_O,C_S) be jointly Gaussian and independent of E, but potentially correlated.”** All other theorem premises remain in force.

For why this is essential, take $C_O=G$ and $C_S=DG$, where $G$ is standard normal and $D$ is an independent equiprobable sign. Both criteria are marginally Gaussian and have zero covariance. Nevertheless their absolute values coincide, so equal centered intervals have joint probability $q$, rather than the independence value $q^2$. Gaussian marginals and zero covariance alone would therefore invalidate the proposed inverse. The existing sufficiency construction in the proof is already correct because it explicitly chooses a Gaussian criterion vector.

### 4. Section 7 overstates discrimination of implementation packages

The sentence that sensory and decision packages “make different predictions for both marginals and joint responses” is incompatible with the central exact-counterpart result: those marginals coincide. Broad composite packages can also overlap unless their restrictions make their prediction sets distinct.

Suggested replacement: **“The combined marginal and joint laws can then be compared. For the exact marginal counterparts constructed here, their prospective joint probabilities differ under the stated independent-criterion assumptions. Broader implementation packages require explicit restrictions to make their prediction sets distinct.”** This preserves the constructive next step without claiming automatic separation of all sensory and decision accounts.

## Important inference and novelty boundaries already handled correctly

- **Common center:** the paired theorem is prospective. The source counts reject zero-centered symmetry under their stated count law; separate task blocks contain no same-internal-sample joint response. The main text correctly requires additional calibration and says that nonaligned task centers need a different analysis. Retain this qualification in abstract, figure captions, and discussion. Two different fitted centers do not produce one physical SOA centered for both tasks.
- **Threshold policy:** the alternative preserves every source halfwidth, including its condition changes. The manuscript correctly avoids claiming that only jitter changes while all decision thresholds remain fixed. Its fixed construction rule adds no fitted prediction parameter but is an explicit alternative implementation assumption.
- **Variance attribution:** relative superiority of the noise-varying family does not compare it with its exact decision-side counterpart. The wording about effective response parameters, rather than anatomical mediation or UCT consequences, is appropriate.
- **Novelty:** Gaussian variance addition and its sensory/criterion ambiguity are credited to Yarrow; joint-noise methods to Cabrera and colleagues; location bias to the prior BCI lineage; the probability derivative to Plackett. The sharp interval is an application of covariance feasibility, not a new general covariance principle. This is the defensible contribution level.
- **Weak identification:** the $n^{-1/4}$ local scale applies to the variance parameter $a$, with marginal calibration treated as known. The proof correctly gives $D_{KL}=O(a^4)$ and does not translate a population inverse into a human sample-size recommendation.
- **Symmetry test:** the hypergeometric conditional law, deterministic deviance lower bound, one global test, and Monte Carlo tail interval are correct. They test the centered independent-binomial family, not centering alone under arbitrary serial dependence. The manuscript states that distinction.
- **Minimum additional readout:** one population joint probability is the remaining degree of freedom of a binary pair with fixed marginals. It is not one trial, an optimal finite-sample design, or a validated way to elicit two human reports from one internal sample.

## Recommended clarification

The response-family extension was chosen after inspecting this dataset. Training-fold parameter fitting is isolated from held-out counts, but artificial fivefold scoring does not correct for all prior dataset-level model selection. Section 4 should say explicitly: **“The family specification was developed retrospectively using this dataset; the fixed-partition comparison evaluates the declared pipeline and is not an external or selection-adjusted validation.”** The current general retrospective statement and conditional interpretation help, but adding this near the predictive results prevents “held-out” from carrying a stronger meaning than the workflow supports.

The abstract's “centered-extension noise family” is ambiguous because the paper contrasts zero-centered and location-shifted curves. “Noise-varying model with task-specific centers” is clearer.

## Independent numerical verification

The reviewer audited the final repaired output without refitting. An independent signed-SOA response implementation checked all 720 full-data/training records, all held-out scores, 28 finite-difference cases, all 60 full-data nesting relations, and all 300 training nesting relations. Maximum probability discrepancy is $5.55\times10^{-16}$; maximum NLL discrepancy is $3.55\times10^{-13}$; maximum scaled finite-difference derivative error is $3.34\times10^{-7}$. The final shifted noise-minus-prior held-out contrast is −60.8845945270, with participant mean −2.0294864842 and descriptive paired interval [−3.2676238033, −0.7913491652].

The original three nesting violations were independently verified in the archived first run. The final repair leaves full fits, unshifted training fits, and partitions unchanged and uses only each training fold's unshifted fit as an added shifted start. The implementation evidence and remaining scope limits are in `ctd_v02/theory/RESPONSE_COMPARISON_AUDIT.md` and its JSON record.

The theoretical checks reproduce all source-derived joint profiles and the correlated-criterion set over 60,060 finite grid points. Proofs, rather than these checks, establish the stated model claims. The corrected Hellinger calculation uses squared root-probability differences and `log1p`, avoiding a spurious numerical equality for nearly saturated profiles. The paper appropriately excludes its illustrative count bounds from actual sample-size advice.

**Disposition:** all four required corrections have been confirmed in the manuscript. The abstract's ambiguous “centered-extension” wording has also been replaced. The near-CV clarification about retrospective family specification remains a recommendation in addition to the draft's existing retrospective and conditional qualifications. Publication readiness still requires the human author's review, a clear destination and positioning, and external peer review; this audit does not certify first-in-literature priority or empirical validation of the paired protocol.
