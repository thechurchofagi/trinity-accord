"""Build a disabled CTD2 candidate and audit the preserved map structure.

Writes only this governance directory. Does not merge, activate, modify
navigation, reduce inherited OPEN debt, or claim whole-map semantic reproof.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import gzip
import hashlib
import io
import json
import subprocess
import tarfile

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
MANUSCRIPT = "manuscript/noise-identifiability-bodily-judgments-v0.2.0.md"
THEORY = "theory/RESPONSE_IDENTIFIABILITY_RESULTS.md"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def record_digest(obj):
    return digest(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode())


def n(number, label, kind, statement, premises, domain, quantifier, proof_sections,
      evidence, limits, novelty, lineage):
    return {
        "id": f"CTD2-N{number:03d}", "label": label, "kind": kind,
        "statement": statement, "domain": domain, "quantifier": quantifier,
        "all_premises": premises, "proof_locations": proof_sections,
        "evidence_paths": evidence, "counterexamples_and_limits": limits,
        "novelty_status": novelty, "source_lineage": lineage,
        "status": "PENDING_MAP_CONDITIONAL_OR_RECORDED_EVIDENCE",
        "enabled": False, "enabled_as_established_premise": False,
        "automatic_premise_truth": False, "actual_application_premises_discharged": False,
        "experience_inference": "NONE; no experiential or actual-consumer premise follows from registration."
    }


def loc(path, section):
    return {"path": path, "section": section}


NODES = [
 n(1, "Effective Gaussian interval response domain", "MODEL_CLASS_DEFINITION",
   "One fixed participant and declared task/condition family has p_tf(s)=lambda/2+(1-lambda)[Phi((k_tf-(s-mu_t))/sigma_f)-Phi((-k_tf-(s-mu_t))/sigma_f)]. Source k^2 is the positive part of 2v(v+S^2)/S^2 times [logit(pi)+0.5log(1+S^2/v)], with v=sigma^2 and S^2=84000 ms^2. This is an observation-model definition, not an anatomical interpretation.",
   ["Same participant, task labels, condition labels, SOA convention, and report code.", "sigma>0; 0<=lambda<1; finite k>=0; source posterior criterion one half unless explicitly generalized.", "Centers are zero in the released family; the limited extension has two task centers stable across conditions.", "Parameters of the population law, fitted estimates, descriptive Gaussian widths, and actual processes are separate objects."],
   "Finite task/condition families and arbitrary real SOAs in a specified Gaussian interval observer.",
   "For each fixed parameter vector and every admitted SOA; no universal claim about all biological observers.",
   [loc(MANUSCRIPT,"2.2, 4.1"),loc(THEORY,"1")],
   ["root_analysis/fit_response_models.py","literature/code_archive/modelprediction_log_BCI.m","RELOCATION_PROVENANCE.json"],
   ["A label such as sensory uncertainty does not establish a sensory source.","The fixed numerical fitting box and the unrestricted mathematical model are distinct."],
   ["INHERITED","NEW_APPLICATION"],["D'Angelo et al. 2026, DOI 10.1038/s41467-025-67657-w","Chancel et al. 2022, DOI 10.7554/eLife.77221"]),
 n(2,"Released likelihood and data provenance","SECONDARY_EVIDENCE",
   "The released Experiment 3 aggregate table has 30 selected participants, 2 tasks, 3 stimulation conditions and 7 SOAs with 10 judgments per cell. Evaluating the declared source likelihood at all 60 saved parameter vectors reproduces saved NLLs within 2e-9 and fixes the task/condition mapping.",
   ["The three public workbooks and released observer code are the pinned versions in the provenance records.","Counts are aggregated; original trial order is unavailable.","Saved-fit evaluation is separate from new optimization and from new human experimentation."],
   "The declared public Experiment 3 source files and their 1260 count cells.",
   "All 60 saved parameter vectors and all 1260 source count cells; no worldwide or population-wide assertion.",
   [loc(MANUSCRIPT,"2.1, 3.1, Appendix A.1")],
   ["empirical/inputs/Experiment_3.xlsx","empirical/inputs/Experiment_3_Computational_modelling.xlsx","literature/source_bci_reconciliation.json","literature/source_bci_reconciliation.csv"],
   ["Exact objective reproduction is not global optimization or identification of a physical mediator.","Independent-binomial analyses cannot establish unobserved serial independence."],
   ["NEW_APPLICATION"],["Source study and authors' public OSF data/modeling materials"]),
 n(3,"Source information-criterion sign correction","ARITHMETIC_CORRECTION",
   "For d_i=NLL_Sigma,i-NLL_Prior,i the correct saved-fit differences are DeltaAIC_i=-4+2d_i and DeltaBIC_i=-2log(420)+2d_i. The source calculation instead used -2d_i. Reconciliation covers all 30 reported source-data rows. Correcting it preserves the aggregate Sigma preference; summed corrected DeltaAIC is approximately -127.8592.",
   ["Use the same saved parameter vectors, count law, model difference direction, and 420 binary judgments per participant.","The free-parameter difference is two; the source's extra count of fixed S cancels between models.","The sign discrepancy is established by code, saved objectives and source-data arithmetic together."],
   "The released saved-fit information-criterion comparison.",
   "Each of the 30 source participants and their aggregate arithmetic; no claim of reconstructing the exact bootstrap execution.",
   [loc(MANUSCRIPT,"3.1, Appendix A.1")],
   ["literature/SOURCE_BCI_AUDIT.md","literature/source_bci_reconciliation.json","literature/source_bci_reconciliation.csv"],
   ["The correction is not a reversal of the aggregate source comparison.","Relative IC preference does not establish model adequacy or a sensory implementation."],
   ["CORRECTION","NEW_APPLICATION"],["Standard AIC/BIC arithmetic applied to the released source artifacts"]),
 n(4,"Centered symmetry and conditional test law","CONDITIONAL_MATHEMATICAL_RESULT",
   "Every zero-centered curve in CTD2-N001 satisfies p(s)=p(-s). For independent Binomial(10,p) signed-pair counts, conditioning on total K gives Y_plus|K~Hypergeometric(20,K,10). The pooled-pair deviance against cell saturation is a lower bound on every centered BCI model's count-table deviance.",
   ["For symmetry, set each task center to zero and keep the same interval/lapse at opposite SOAs.","For the conditional law, two counts in each pair share p and are independent Binomial(10,p); pairs are independent under the declared test law.","The saturated symmetric family leaves zero-SOA probabilities unrestricted."],
   "A declared centered interval family and conditional count experiment.",
   "Every model parameter vector; every finite observed pair total; every centered fit for the deterministic deviance bound.",
   [loc(MANUSCRIPT,"3.3, Appendix A.2"),loc("theory/SYMMETRY_TEST_REPORT.md","Null, statistic, and exact conditional law; deterministic implication")],
   ["theory/test_source_symmetry.py","theory/SYMMETRY_ANALYSIS_PLAN.json"],
   ["The conditional test is not distribution-free under arbitrary serial dependence or drift.","A symmetry failure need not refute BCI in general."],
   ["INHERITED","NEW_APPLICATION"],["Binomial conditioning and likelihood-family inclusion; released centered observer"]),
 n(5,"Conditional source-symmetry rejection","NEGATIVE_SECONDARY_EVIDENCE",
   "The fixed global 540-pair test gives T=984.30423637609. Zero of 19999 conditional simulations exceeds or equals T, yielding plus-one p=0.00005 and a 95% binomial Monte Carlo tail interval [0,0.0001844362]. This rejects the centered independent-binomial family under the stated observation law.",
   ["Canonical count mapping and retained 540 sign pairs; zero-SOA cells excluded by design.","Conditional sampling assumptions of CTD2-N004.","One retrospective plan recorded before this statistic; seed 202610100742; no adaptive extra simulation or subsidiary significance selection."],
   "The released Experiment 3 counts and one specified conditional Monte Carlo test.",
   "One global family test; task and condition summaries are descriptive only.",
   [loc(MANUSCRIPT,"3.3"),loc("theory/SYMMETRY_TEST_REPORT.md","Results; Limits")],
   ["theory/SYMMETRY_TEST_RESULTS.json","theory/symmetry_conditional_simulations.npz","theory/symmetry_pair_diagnostics.csv","theory/SYMMETRY_ANALYSIS_PLAN.json"],
   ["No causal attribution of asymmetry to stimulation, sensory timing, decision criteria or experience.","Physical zero SOA is not established as a calibrated common center for the proposed paired theorem."],
   ["NEGATIVE_RESULT","NEW_APPLICATION"],["CTD2-N004 applied to the authors' aggregate counts"]),
 n(6,"Corrected fixed-partition response comparison","SECONDARY_EVIDENCE",
   "In the final bounded four-model pipeline, the task-center Sigma model has 60.8845945270 lower held-out binary NLL than the task-center Prior model; mean participant difference is -2.0294864842 and its descriptive paired t interval is [-3.2676238033,-0.7913491652]. All shifted training fits satisfy nesting after uniform training-only repair.",
   ["Same fixed artificial five-fold partition: each cell holds out two of ten exchangeable binary outcomes and trains on eight.","The two task centers remain fixed across all three stimulation conditions.","Fold starts are generic plus the same-fold unshifted fit for shifted models; no full-data/source/test parameter initialization.","The repair was applied to all 300 shifted training fits; archived first-run failures remain available.","Family specification was retrospective; participant intervals condition on this selected pipeline and fixed partition."],
   "30 participants in the bounded four-model response comparison, parameter counts 6/8/8/10.",
   "All 120 full fits and 600 training fits in the final saved run; no new participant, SOA or temporal generalization.",
   [loc(MANUSCRIPT,"4, Appendix A.3"),loc("theory/RESPONSE_COMPARISON_AUDIT.md","Final score contrast")],
   ["empirical/results/bci_response/response_comparison_summary.json","empirical/results/bci_response/cv_fits.json","empirical/results/bci_response/cv_partition_counts.npz","empirical/results/bci_response/cv_nesting_repair_summary.json","theory/RESPONSE_COMPARISON_AUDIT.json"],
   ["Local optimizer convergence is not global optimality; boundary fits constrain regular asymptotic interpretations.","This compares parameterizations, not the exact decision-side counterpart or anatomical mechanisms.","Artificial partitions do not reconstruct trial chronology or remove prior model-selection effects."],
   ["NEW_APPLICATION","CORRECTION"],["Source BCI models; standard location extension; retained numerical nesting repair"]),
 n(7,"Additive Gaussian sensory and criterion domain","MODEL_CLASS_DEFINITION",
   "A sensory sample X=s+E with E~N(0,a) and an independent criterion center C~N(mu,b) gives response 1{|X-C|<=k}; its effective variance is v=a+b. Lower and upper criteria C-k and C+k move together and do not cross.",
   ["Nonnegative finite variances, independent sensory and criterion variables, fixed halfwidth and lapse law in each declared cell.","The criterion center is one common shift of both bounds, not two unrelated crossing thresholds."],
   "A Gaussian interval observer with explicitly separated sensory and decision-center variables.",
   "Every nonnegative decomposition of a positive effective variance under the given independence law.",
   [loc(MANUSCRIPT,"5.1"),loc(THEORY,"3")],
   ["theory/bci_identification.py","theory/check_bci_identification.py","literature/V02_NOVELTY_AND_PUBLICATION_AUDIT.md"],
   ["This ambiguity is inherited, not a new general noise-decomposition theorem.","It is an admitted observation model, not an established description of the participants."],
   ["INHERITED"],["Yarrow et al. 2011 DOI 10.1016/j.concog.2011.07.003","Yarrow et al. 2023 DOI 10.1037/xhp0001154"]),
 n(8,"Exact constant-sensory intervention counterpart","CONDITIONAL_MATHEMATICAL_RESULT",
   "For each participant with source variances v_f>0, choose a fixed a in (0,min_f v_f] and set b_f=v_f-a. Retaining every k_tf, center and lapse gives the same marginal response at every SOA and the same likelihood for every possible marginal count table. The fixed construction a=0.5 min_f v_f adds no fitted prediction parameter.",
   ["CTD2-N001 and CTD2-N007 hold for the same participant, task/condition labels, response rule and lapse convention.","All source halfwidths and centers are retained, including condition-specific threshold changes.","The construction is a permitted alternative implementation, not the original normative observer with only its sensory interpretation relabeled."],
   "Source-related Gaussian interval observers across one participant's stimulation conditions.",
   "Every finite positive source variance family, every real SOA and every possible marginal count dataset.",
   [loc(MANUSCRIPT,"5.1 Proposition 1"),loc(THEORY,"3 Proposition 3")],
   ["root_analysis/instantiate_response_twins.py","root_analysis/response_twin_summary.json","root_analysis/response_twin_probabilities.csv","theory/BCI_IDENTIFICATION_CHECKS.json"],
   ["Does not show that criterion variability actually caused the source results.","Do not say only jitter changes while all thresholds are fixed.","Pointwise equivalence concerns these marginal laws, not full physical organization or all possible joint observations."],
   ["NEW_APPLICATION","PRIORITY_UNVERIFIED"],["Inherited Yarrow Gaussian criterion-noise ambiguity, explicitly applied to the released stimulation observer"]),
 n(9,"Prior and posterior-criterion alias","CONDITIONAL_MATHEMATICAL_RESULT",
   "With posterior report threshold gamma in (0,1), the source interval depends on pi and gamma only through logit(pi)-logit(gamma). Equal shifts of both logits preserve every response probability; a fitted prior under gamma=1/2 is conditional on that report convention.",
   ["The same Gaussian Bayesian likelihood and stimulus-prior scale are used.","The report rule compares posterior common-cause probability with gamma; pi and gamma are interior probabilities.","The nonpositive interval branch is retained."],
   "The declared posterior-threshold Gaussian source observer.",
   "All jointly shifted logit pairs in their probability domains and all SOAs/noise levels.",
   [loc(MANUSCRIPT,"5.2, Appendix B.1"),loc(THEORY,"1 Proposition 1")],
   ["theory/BCI_IDENTIFICATION_CHECKS.json","theory/bci_identification.py"],
   ["Does not equate arbitrary prior changes with arbitrary effective-noise changes.","A decision convention is not evidence about anatomical implementation."],
   ["INHERITED","NEW_APPLICATION"],["Posterior-odds algebra in the source model"]),
 n(10,"Calibrated shared-sample Gaussian pair","CONDITIONAL_MODEL_CONTRACT",
   "One same internal sensory draw E~N(0,a) reaches two consumers Z_t=s+E-C_t. The criterion vector is jointly Gaussian, independent of E, with zero means after a common center calibration. Effective variances v_t>0, finite positive k_t, and marginal lapses below one are known. Lapse indicators and fair guesses are independent across reports and from the Gaussian variables.",
   ["The same internal sample, participant/implementation, event, SOA origin and marginal calibration apply to both consumers.","Criterion joint Gaussianity is required; marginal Gaussianity alone is insufficient.","Halfwidths, effective marginal variances and lapse parameters remain fixed when comparing possible variance decompositions.","For a central readout both consumer intervals are centered at the same calibrated physical SOA; for off-center statements the same calibrated offset is used.","Different task centers or sequential answer contamination do not satisfy this contract automatically."],
   "A prospective two-consumer Gaussian interval observation family, with a in [0,min(v_O,v_S)].",
   "One fixed pair of calibrated marginal laws and its admissible joint Gaussian laws; one population probability is not one trial.",
   [loc(MANUSCRIPT,"6.1, 6.2, Appendix B.2"),loc(THEORY,"4, 6")],
   ["theory/bci_identification.py","theory/BCI_IDENTIFICATION_CHECKS.json","review/THEORY_MANUSCRIPT_REVIEW.md"],
   ["The existing experiment supplies separate task blocks, not this joint observation.","The source symmetry rejection prevents treating zero physical SOA as established common calibration.","A mathematical contract is not evidence of an installed physical protocol."],
   ["PROPOSED_NEW_RESULT","PRIORITY_UNVERIFIED"],["Source-specific contract; prior joint-noise methods include Cabrera et al. 2015 DOI 10.1037/a0039348"]),
 n(11,"Centered paired inverse under independent criteria","CONDITIONAL_MATHEMATICAL_RESULT",
   "Under CTD2-N010 and CTD2-N020, a valid central population P11 uniquely identifies shared variance a. With radii r_t=k_t/sqrt(v_t) and rho=a/sqrt(v_O v_S)>=0, J'(rho)=2[phi2(r_O,r_S;rho)-phi2(r_O,-r_S;rho)]>0 for 0<rho<1. Known independent lapses transform J affinely with positive slope.",
   ["The complete CTD2-N010 contract and zero criterion covariance CTD2-N020 hold together for the same pair.","P11 lies in the admissible central response-law range; endpoints are included by continuity.","Nonnegative total correlation follows from shared sensory variance and independent criteria."],
   "The admissible nonnegative-correlation subfamily of the calibrated Gaussian pair.",
   "Each valid population P11 has one inverse on a in [0,min(v_O,v_S)]; with fixed binary marginals one added degree of freedom suffices.",
   [loc(MANUSCRIPT,"6.1 Theorem 2, Appendix B.2"),loc(THEORY,"4 Theorem 4")],
   ["theory/BCI_IDENTIFICATION_CHECKS.json","root_analysis/paired_readout_predictions.csv"],
   ["No optimal finite-sample or validated human protocol is established.","Centered intervals identify absolute correlation without the sign restriction; relaxing criterion independence requires CTD2-N013."],
   ["NEW_APPLICATION","PROPOSED_NEW_RESULT","PRIORITY_UNVERIFIED"],["Plackett 1954 DOI 10.1093/biomet/41.3-4.351; source-specific central two-sided readout"]),
 n(12,"Externally bounded criterion correlation","CONDITIONAL_MODEL_CONTRACT",
   "Retaining CTD2-N010, allow criterion covariance c subject to |c|<=kappa sqrt((v_O-a)(v_S-a)), for an externally justified kappa in [0,1]. The covariance form includes zero criterion variance. Do not conjoin this alternative with CTD2-N020 as a compulsory assumption.",
   ["All shared-sample, common-center, joint-Gaussian and lapse conditions in CTD2-N010 persist.","The value or bound kappa comes from evidence outside the same single joint response probability.","The observer's total covariance is a+c; the central rectangle loses its sign."],
   "A correlated-criterion extension of the same fixed marginal Gaussian pair.",
   "Every shared variance and jointly Gaussian criterion covariance satisfying the stated tolerance; no claim that a human kappa has been measured.",
   [loc(MANUSCRIPT,"6.2, Appendix B.3"),loc(THEORY,"6")],
   ["theory/bci_identification.py","theory/BCI_IDENTIFICATION_CHECKS.json"],
   ["Freely fitting kappa from P11 removes this identifying restriction.","Gaussian marginals alone or an unmeasured correlation bound do not satisfy the contract."],
   ["NEW_APPLICATION"],["Ordinary Gaussian covariance feasibility; explicit sensitivity contract"]),
 n(13,"Sharp correlated-criterion identification set","CONDITIONAL_MATHEMATICAL_RESULT",
   "Let r be the absolute total correlation identified by a calibrated central P11 and R=r sqrt(v_O v_S). Under CTD2-N010 and CTD2-N012, the sharp set is {a in [0,min(v_O,v_S)] : (R-a)^2<=kappa^2(v_O-a)(v_S-a)}. For v_O=v_S=v and kappa<1, max(0,(r-kappa)/(1-kappa))<=a/v<=(r+kappa)/(1+kappa); for kappa=1 the fraction lies in [0,(1+r)/2].",
   ["The same calibrated marginal laws, internal sample, joint Gaussianity and independent lapse law satisfy CTD2-N010.","CTD2-N012 supplies the externally supported covariance tolerance for this same pair.","The nonnegative a range and unobserved total covariance sign are both retained."],
   "Shared sensory variance consistent with one calibrated central Gaussian rectangle and a fixed covariance budget.",
   "Necessity for every compatible Gaussian construction and attainability of every feasible a; the set may be empty for unequal marginals.",
   [loc(MANUSCRIPT,"6.2 Theorem 3, Appendix B.3"),loc(THEORY,"6 Theorem 6")],
   ["theory/BCI_IDENTIFICATION_CHECKS.json","theory/bci_identification.py"],
   ["Sharpness is within the declared Gaussian and calibration class, not over arbitrary criterion copulas.","If kappa>=r in the equal-variance case, zero shared sensory variance is admissible.","This is covariance algebra applied to the proposed readout, not a new general covariance theorem."],
   ["NEW_APPLICATION","PROPOSED_NEW_RESULT","PRIORITY_UNVERIFIED"],["Gaussian covariance positive-semidefiniteness and the central rectangle inverse"]),
 n(14,"Weak central identification near zero shared variance","CONDITIONAL_MATHEMATICAL_RESULT",
   "For positive finite radii, J(rho)-J(0)=2r_O r_S phi(r_O)phi(r_S)rho^2+O(rho^4). Under known fixed marginals and independent criteria/lapses, observed excess d(a)=C a^2+O(a^4), C>0; categorical KL is O(a^4). Thus n a^4->0 gives vanishing total-variation separation while sqrt(n)a^2->infinity permits separation by a joint proportion.",
   ["CTD2-N010 and CTD2-N020 apply along the same local family with all effective marginal parameters fixed as a approaches zero.","Independent repetitions of the declared paired law; calibration uncertainty is not included.","a denotes a variance, not a standard deviation or neural time constant."],
   "Local asymptotic discrimination near independence in the centered calibrated Gaussian pair.",
   "The specified local sequences and fixed interior marginal probabilities; not all sample-size or composite-model regimes.",
   [loc(MANUSCRIPT,"6.3, Appendix B.2"),loc(THEORY,"5")],
   ["theory/BCI_IDENTIFICATION_CHECKS.json","theory/check_bci_identification.py"],
   ["The n^(-1/4) scale is conditional mathematical sensitivity, not a proposed human sample size.","Tail saturation and calibration error can make practical identification weaker."],
   ["NEW_APPLICATION","PROPOSED_NEW_RESULT","PRIORITY_UNVERIFIED"],["Taylor expansion of Gaussian rectangle probabilities and standard KL/Pinsker arguments"]),
 n(15,"Off-center local information","CONDITIONAL_MATHEMATICAL_RESULT",
   "For the same calibrated nonzero offset s in both consumers, with L_t=(-k_t-s)/sqrt(v_t) and U_t=(k_t-s)/sqrt(v_t), the joint derivative at rho=0 equals [phi(L_O)-phi(U_O)][phi(L_S)-phi(U_S)]>0. A second offset can therefore add first-order local sensitivity.",
   ["CTD2-N010's common calibrated coordinate, known marginals and lapse law; a nonzero physical offset is the same for both consumers.","CTD2-N020 defines the sensory-only correlation direction near zero.","Positive finite halfwidths and variances are fixed during the derivative calculation."],
   "The local Gaussian pair law at a common nonzero offset.",
   "Every shared nonzero calibrated s at rho=0; no global monotonicity assertion at arbitrary offsets.",
   [loc(MANUSCRIPT,"6.3, Appendix B.2 equation B4"),loc(THEORY,"5")],
   ["theory/BCI_IDENTIFICATION_CHECKS.json"],
   ["Task-specific unaligned centers can change the derivative signs and invalidate this statement.","A local derivative is not a global inverse or a validated experimental design."],
   ["NEW_APPLICATION","PROPOSED_NEW_RESULT","PRIORITY_UNVERIFIED"],["Classical bivariate-normal boundary derivative in the selected observation model"]),
 n(16,"Countermodels to uncalibrated pairing","EXPLICIT_COUNTEREXAMPLES",
   "Correlated criteria can preserve all marginal and joint curves while changing shared sensory variance: (a,b_O,b_S,c)=(0.2,0.8,0.8,0.3) and (0.4,0.6,0.6,0.1) have the same total variances and covariance. Independently resampled sensory draws give product marginals; correlated lapses can produce apparent shared variance. Marginally Gaussian but non-joint-Gaussian criteria also invalidate the Gaussian rectangle inverse.",
   ["Each counterexample has its own explicitly specified law; mutually incompatible witnesses are not conjoined into one actual instance.","The correlated-criterion pair retains the same thresholds, centers and lapse policy.","The shared-coin lapse witness uses marginal yes probabilities 0.5 and 20% shared fair-coin replacement, giving joint yes probability 0.30.","For the copula witness C_O=G, C_S=D G with independent normal G and fair sign D: Gaussian marginals and zero covariance do not imply independence."],
   "Separate explicit Gaussian, lapse, resampling and non-Gaussian-copula witness domains.",
   "Existence of the separately bound countermodels refutes the corresponding premise-dropping inference; no universal biological mechanism claim.",
   [loc(MANUSCRIPT,"6.3, Appendix B.3"),loc(THEORY,"7"),loc("review/THEORY_MANUSCRIPT_REVIEW.md","Required correction 3")],
   ["theory/BCI_IDENTIFICATION_CHECKS.json","review/THEORY_MANUSCRIPT_REVIEW.md"],
   ["These witnesses show why assumptions matter; they do not establish which violation occurs in the source participants.","Sequential dual reports need their own contamination and sample-sharing validation."],
   ["INHERITED","NEW_APPLICATION"],["Cabrera et al. 2015 joint-noise precedents; explicit local constructions"]),
 n(17,"No automatic mechanism or experience inference","SCOPED_INFERENCE_BOUNDARY",
   "The audited count-law parameters, widths, scores and latent covariances are neither complete actual organization nor named phenomenal endpoints. No candidate rule derives an anatomical mediator, ownership experience, agency, mineness or a UCT-specific prediction from those quantities. C1/U1 remain inherited with their original domains; no report, fit, calibration or complexity threshold is added for basal experience.",
   ["Keep finite models, population parameters, estimates, reports, actual tokens and specified experiential interpretations as distinct sorts.","Actual source/consumer/time binding and any phenomenal bridge require separate evidence.","Preserve nonempty experience for admitted actual processes under UCT's own conditional commitments without treating those commitments as measured here."],
   "Interpretation of this methods paper and its relation to the inherited UCT program.",
   "All uses of this candidate's models and empirical results; no universal positive or negative consciousness verdict.",
   [loc(MANUSCRIPT,"1, 7, 8"),loc(THEORY,"8")],
   ["review/THEORY_MANUSCRIPT_REVIEW.md","literature/V02_NOVELTY_AND_PUBLICATION_AUDIT.md"],
   ["A failure to identify a specified experience does not imply absence of basal experience.","No exclusive owner, erasure of persistent local experience, or claim that local content must stay unchanged is introduced."],
   ["INHERITED","NEW_APPLICATION"],["UCT A:C1, A:U1 and actual-token typing; SCU and prior calibration/use limitations"]),
 n(18,"Prospective calibration and implementation obligations","PROPOSED_EMPIRICAL_CONTRACT",
   "A future discriminating implementation must validate common-center calibration, marginal parameter/lapse estimates, same-internal-sample routing, report stability and an independent bound on shared decision variability. Its implementation packages need explicit separated prediction sets. The exact counterparts above match marginals and differ only in eligible joint predictions under the stated exclusions.",
   ["The contracts must hold together for the same actual implementation, consumers, event, task coordinates and intervention family.","A software/apparatus witness is not itself human endpoint validation.","Phenomenal interpretation, neuronal mediation and independent empirical replication remain separately open."],
   "Prospective device or human studies instantiating the declared joint-response model.",
   "Only explicitly specified implementation packages with tested or externally grounded premises; not all sensory and decision theories.",
   [loc(MANUSCRIPT,"6, 7"),loc(THEORY,"8")],
   ["theory/SYMMETRY_TEST_REPORT.md","review/THEORY_MANUSCRIPT_REVIEW.md"],
   ["No joint human responses or actual consumer-route intervention were collected in this revision.","Existing separate-block data cannot supply the missing joint observation retrospectively.","C1 does not independently identify the required measurement bridge."],
   ["NEW_APPLICATION","PRIORITY_UNVERIFIED"],["Established independent-calibration discipline; source-specific future contract"]),
 n(19,"Descriptive-width reconstruction and remaining mismatch","SECONDARY_EVIDENCE",
   "A free-baseline unweighted Gaussian reconstruction matches 176 of 180 released descriptive widths within 0.01 ms and 178 within 0.1 ms; two material mismatches remain. Many reconstructed curves leave the probability range. These descriptive widths are not the effective sigma of the released interval observer.",
   ["Use the recorded fixed reconstruction procedure and all source participants/tasks/conditions.","Reconstructed nuisance parameters are not released original nuisance estimates.","Do not splice a different estimator into the two unresolved cases or claim exact reconstruction of all original widths."],
   "The 180 released descriptive Gaussian widths and documented reconstruction attempts.",
   "All 180 saved endpoints; remaining discrepancies and failures retained.",
   [loc(MANUSCRIPT,"3.2, Appendix A.1")],
   ["empirical/WIDTH_RECONSTRUCTION_REPORT.md","empirical/results/gaussian_reconstruction_summary.json","empirical/results/gaussian_probability_domain_diagnostics.csv"],
   ["CTD-OPEN-ESTIMATOR-RECONSTRUCTION is not closed by partial recovery.","The v0.1 width branch remains archived unchanged; its restrictions are not made consequences of this BCI model."],
   ["NEW_APPLICATION","NEGATIVE_RESULT"],["Published descriptive endpoint estimates; standard free-baseline Gaussian fitting"]),
 n(20,"Independent-criterion subfamily","CONDITIONAL_MODEL_CONTRACT",
   "Within CTD2-N010, impose c=Cov(C_O,C_S)=0. Because the criterion vector is jointly Gaussian, its components are independent; total covariance is a and total correlation is nonnegative. This is one explicit hypothesis subfamily, not a demonstrated property of the source study.",
   ["CTD2-N010's joint Gaussianity, sensory independence, centers, marginal calibration and lapse conditions.","Criterion covariance zero in the same paired event; no shared decision disturbance omitted from the declaration."],
   "Independent-criterion branch of the prospective calibrated Gaussian pair.",
   "Only pairs satisfying the complete zero-covariance Gaussian contract.",
   [loc(MANUSCRIPT,"6.1, Appendix B.2"),loc(THEORY,"4")],
   ["theory/bci_identification.py","theory/BCI_IDENTIFICATION_CHECKS.json"],
   ["Not inferred merely from a lack of marginal correlation or separate task blocks.","The bounded-correlation branch CTD2-N012 replaces this restriction; both are not compulsory empirical premises."],
   ["INHERITED","NEW_APPLICATION"],["Joint Gaussian zero-covariance independence; source-specific hypothesis contract"])
]


def rule(number, premises, conclusion, binding, proof, witness):
    return {"id": f"CTD2-R{number:03d}", "kind": "CONDITIONAL_MATHEMATICAL_RULE",
        "all_of": premises, "conclusion": conclusion,
        "premise_semantics": "AND of the complete referenced contracts for the same declared instance; registration is not premise truth.",
        "same_instance_required": True, "binding": binding,
        "alternative_route_semantics": "Separate rule IDs are alternatives; the independent and bounded-correlated criterion branches are not conjoined.",
        "proof_locations": proof, "joint_witness_or_argument": witness,
        "enabled": False, "enabled_as_established_premise": False,
        "actual_premises_discharged": False, "machine_proof": False}


RULES = [
 rule(1,["CTD2-N001"],"CTD2-N004","Restrict the defined source family to zero task centers; all conditional count assertions retain the explicit equal-p and independence antecedents in N004.",[loc(MANUSCRIPT,"3.3, Appendix A.2")],"Normal symmetry; binomial conditioning; inclusion of every centered source curve in the saturated symmetric family."),
 rule(2,["CTD2-N001","CTD2-N007"],"CTD2-N008","Same participant, condition variances, task interval/center policy and lapse process; compare the explicitly constructed alternative a and b_f, not two unrelated people.",[loc(MANUSCRIPT,"5.1")],"Choose a<=min v_f, b_f=v_f-a; the complete marginal probability arguments remain equal."),
 rule(3,["CTD2-N001"],"CTD2-N009","Use the same source posterior law and its explicitly generalized report criterion gamma; N009 asserts the conditional alias, not empirical freedom of the participant's criterion.",[loc(MANUSCRIPT,"5.2, Appendix B.1")],"Posterior log odds minus logit(gamma) depend on pi,gamma through their logit difference."),
 rule(4,["CTD2-N010","CTD2-N020"],"CTD2-N011","Same calibrated two-consumer pair, one internal sensory event, fixed positive finite marginal laws, central readout, independent criteria and independent lapse variables.",[loc(MANUSCRIPT,"6.1, Appendix B.2")],"Strict increase of the central rectangle on the admissible nonnegative-correlation interval and a positive-slope lapse map."),
 rule(5,["CTD2-N010","CTD2-N012"],"CTD2-N013","Same calibrated joint-Gaussian pair and one externally fixed kappa. N020 is not required; correlation is permitted rather than silently combined with independence.",[loc(MANUSCRIPT,"6.2, Appendix B.3")],"The negative covariance branch is contained in the positive-branch feasibility set; every feasible a is attained by a positive-semidefinite Gaussian criterion covariance matrix."),
 rule(6,["CTD2-N010","CTD2-N020","CTD2-N011"],"CTD2-N014","Known fixed effective marginals and lapses along a->0; independent repetitions of this same family. The population inverse is not replaced by finite-data plug-in estimates.",[loc(MANUSCRIPT,"6.3, Appendix B.2")],"Gaussian rectangle expansion gives joint excess O(a^2), categorical KL O(a^4), and the conditional local separation limits."),
 rule(7,["CTD2-N010","CTD2-N020"],"CTD2-N015","Both consumers use the same nonzero offset from an independently calibrated common center; fixed positive finite thresholds/variances; derivative at zero sensory correlation only.",[loc(MANUSCRIPT,"Appendix B.2 equation B4")],"At rho=0 the four-corner density derivative factors into two normal-density differences of equal nonzero sign.")
]


CONTEXT_SPECS = [
 ("CTD2-N002","CTD2-N003","SOURCE_ARTIFACT_ARITHMETIC_SUPPORT"),
 ("CTD2-N002","CTD2-N005","SUPPLIES_AGGREGATE_COUNTS_NOT_CAUSAL_MEDIATION"),
 ("CTD2-N004","CTD2-N005","RESTRICTION_TESTED_UNDER_DECLARED_COUNT_LAW"),
 ("CTD2-N005","CTD2-N006","MOTIVATES_RESTRICTED_RETROSPECTIVE_SENSITIVITY"),
 ("CTD2-N006","CTD2-N008","PREDICTIVE_PREFERENCE_DOES_NOT_RESOLVE_EXACT_COUNTERPART"),
 ("CTD2-N008","CTD2-N011","MISSING_JOINT_OBSERVABLE_UNDER_ADDITIONAL_CONTRACT"),
 ("CTD2-N016","CTD2-N010","COUNTERMODELS_TO_OMITTED_PAIR_PREMISES"),
 ("CTD2-N017","A:C1","AXIOM_STATUS_PRESERVED_NO_NEW_BRIDGE"),
 ("CTD2-N017","A:U1","NO_BASAL_EXPERIENCE_GATE_ADDED"),
 ("CTD2-N018","A:ACTUAL_TOKEN","ACTUAL_INSTANCE_GROUNDING_REMAINS_REQUIRED"),
 ("CTD2-N018","R188:IDEAL_NOT_INSTALLED","CONTEXT_ONLY_IDEAL_PROTOCOL_IS_NOT_INSTALLATION"),
 ("CTD2-N019","CTD2-N001","DESCRIPTIVE_ESTIMATOR_DISTINCT_FROM_INTERVAL_NOISE"),
 ("CTD2-N013","CTD2-N018","CORRELATION_BUDGET_REQUIRES_EXTERNAL_CALIBRATION")
]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--research-root",type=Path,
        default=PACKAGE.parent/"uct_repo"/"research"/"uct-agent-consciousness-workspace")
    args=parser.parse_args(); research=args.research_root.resolve()
    HERE.mkdir(parents=True,exist_ok=True)
    repo=research.parents[1]
    commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=repo,text=True).strip()
    source_prefix="research/"+research.name+"/"
    def read_research(relative):
        # Read the immutable current Git snapshot even when the working tree
        # is being materialized concurrently by the packaging process.
        return subprocess.check_output(["git","show",f"{commit}:{source_prefix}{relative}"],cwd=repo)
    old_dir=research/"records"/"CTD20261010_Cross_Task_Intervention"
    old_prefix="records/CTD20261010_Cross_Task_Intervention/"
    old_path=old_dir/"MAP_EXTENSION.json"; old_bytes=read_research(old_prefix+"MAP_EXTENSION.json"); old=json.loads(old_bytes)
    old_summary=json.loads(read_research(old_prefix+"review/BASELINE_STRUCTURE_SUMMARY.json"))
    old_per=json.loads(gzip.decompress(read_research(old_prefix+"review/BASELINE_PER_ID_STRUCTURE.json.gz")))
    release_dir=research/"versions"/"UCT-MAP-v1.1.2"
    capsule=release_dir/"UCT_MAP_v1.1.2_Capsule.tar.xz"
    capsule_bytes=read_research("versions/UCT-MAP-v1.1.2/UCT_MAP_v1.1.2_Capsule.tar.xz")
    with tarfile.open(fileobj=io.BytesIO(capsule_bytes)) as tf:
        graph_bytes=tf.extractfile("UCT_EFFECTIVE_GRAPH.json").read()
    graph=json.loads(graph_bytes)
    expected=old_summary["source_graph_sha256"]
    assert digest(graph_bytes)==expected=="0973600f1be5cf21614592ca901112b26f9f0c9f6df36294a5dbb049efcf7612"
    assert (len(old["nodes"]),len(old["rules"]),len(old["context_links"]))==(13,4,7) and old["enabled"] is False
    baseline_counts={"nodes":len(graph["nodes"]),"active_conditional_rules":len(graph["rules"]),
        "contexts":len(graph["context_links"]),"suspended":len(graph["suspended_historical_rule_ids"])}
    baseline_counts["total"]=sum(baseline_counts.values())
    assert baseline_counts==old_summary["counts"]==dict(nodes=913,active_conditional_rules=424,contexts=261,suspended=10,total=1608)
    baseline_nodes={x["id"] for x in graph["nodes"]}; baseline_rules={x["id"] for x in graph["rules"]}
    prior_ids={x["id"] for key in ("nodes","rules","context_links") for x in old[key]}
    contexts=[{"id":f"CTD2-C{i:03d}","from":a,"to":b,"type":kind,"deductive":False,
        "enabled":False,"enabled_as_established_premise":False,
        "relation_semantics":"Context, evidence, motivation or scope comparison only; never a proof edge or premise-discharge event."}
        for i,(a,b,kind) in enumerate(CONTEXT_SPECS,1)]
    a3m_path="research/uct-agent-consciousness-workspace/records/A3M20261010_Bodily_Familiarity_Invariance/MAP_EXTENSION.json"
    a3m_bytes=subprocess.check_output(["git","show",f"{commit}:{a3m_path}"],cwd=repo)
    a3m=json.loads(a3m_bytes)
    assert not a3m["enabled"] and all(len(a3m[k])==0 for k in ("nodes","rules","context_links"))
    coverage=json.loads(read_research("PUBLICATION_COVERAGE.json"))
    candidate={
        "schema":"uct-pending-extension/1","id":"CTD2-20261010","result_version":"CTD-RESULT-v0.2.0",
        "candidate_version":"CTD2-MAP-CANDIDATE-v0.1.0","base_release":"UCT-MAP-v1.1.2",
        "integration_status":"PENDING_CHECKPOINT_DISABLED","status":"PENDING_MAP",
        "enabled":False,"enabled_as_established_premise":False,
        "release_effect":"NONE; no completed-map version increment, active rule change, entry-point edit or scientific premise promotion.",
        "evidence_path_root":"Parent directory of this governance folder (the CTD v0.2 package root).",
        "baseline_reference_root":"research/uct-agent-consciousness-workspace in the preserved research repository",
        "baseline":{"release":"UCT-MAP-v1.1.2","capsule_path":"versions/UCT-MAP-v1.1.2/UCT_MAP_v1.1.2_Capsule.tar.xz",
            "member":"UCT_EFFECTIVE_GRAPH.json","sha256":expected,"counts":baseline_counts},
        "unchanged_v01":{"path":"records/CTD20261010_Cross_Task_Intervention/MAP_EXTENSION.json",
            "sha256":digest(old_bytes),"nodes":13,"rules":4,"contexts":7,"enabled":False},
        "concurrent_checkpoint":{"repository_head":commit,"id":"A3M20261010","source_path":a3m_path,
            "source_sha256":digest(a3m_bytes),"nodes":0,"rules":0,"contexts":0,"applications":len(a3m.get("applications",[])),
            "enabled":False,"preservation":"No A3M record, claim, OPEN status or argument changed or semantically re-reviewed here."},
        "publication_coverage":{"inherited_entry_version":coverage["coverage_version"],
            "intended_v02_metadata_version":"UCT-PUB-v1.0.28","status":"Parent-managed metadata update; no formal publication or scientific premise effect.",
            "formal_publication_counts_unchanged":True,"new_doi_assigned":False},
        "premise_policy":{"complete_referenced_contracts_required":True,"same_instance_required":True,
            "alternative_rule_routes":"OR; AND only inside one complete route.",
            "empirical_nodes_are_deductive_inputs":False,"context_links_are_deductive":False,
            "C1_or_U1_deductive_inputs":False,"global_semantic_reproof_completed":False},
        "nodes":NODES,"rules":RULES,"context_links":contexts,
        "inherited_open_obligations":old["open_obligations"],
        "inherited_open_debt":old_summary["inherited_open_debt"],
        "new_open_obligations":[
            "CTD2-OPEN-SAME-INTERNAL-SAMPLE","CTD2-OPEN-COMMON-CENTER",
            "CTD2-OPEN-INDEPENDENT-LAPSE","CTD2-OPEN-CRITERION-CORRELATION-CALIBRATION",
            "CTD2-OPEN-ACTUAL-NEURAL-MEDIATOR","CTD2-OPEN-PHENOMENAL-BRIDGE",
            "CTD2-OPEN-PROSPECTIVE-REPLICATION","CTD2-OPEN-FULL-SEMANTIC-INTEGRATION"],
        "open_status_effect":"No inherited obligation is closed, renumbered or reduced; the two source-estimator mismatches retain the v0.1 reconstruction OPEN. New labels do not recompute historical debt counts."
    }
    target=HERE/"MAP_EXTENSION.json"
    target.write_text(json.dumps(candidate,ensure_ascii=False,indent=2)+"\n")
    # Structural verification of every item in the completed baseline.
    old_records={(x["kind"],x["id"]):x for x in old_per["items"]}
    visited=[]; unresolved=[]; external_context_references=[]
    for key,kind in [("nodes","node"),("rules","active_rule"),("context_links","context")]:
        for item in graph[key]:
            refs=[]
            if key=="rules": refs=item.get("all_of",[])+[item["conclusion"]]
            elif key=="context_links":
                source=item.get("from",item.get("source"))
                target_ref=item.get("to",item.get("target"))
                assert source is not None and target_ref is not None
                refs=[target_ref]
                declared_type=item.get("from_type",item.get("source_type"))
                is_external=item.get("external_source",False) or declared_type in {
                    "source_reference","module_reference","module","external_reference"}
                if not is_external:refs.append(source)
                else:external_context_references.append({"id":item["id"],"source":source,
                    "declared_type":declared_type,"role":"Preserved source/module context, not a dangling deductive node premise."})
            known=baseline_nodes | baseline_rules | set(graph["suspended_historical_rule_ids"])
            missing=[x for x in refs if x not in known]
            if missing:unresolved.append({"id":item["id"],"missing":missing})
            legacy_key=next((k for k in old_records if k[1]==item["id"]),None)
            assert legacy_key is not None
            prior=old_records[legacy_key]
            h=record_digest(item)
            assert prior["record_sha256"]==h,(item["id"],prior["record_sha256"],h)
            visited.append({"id":item["id"],"kind":kind,"record_sha256":h,
                "prior_per_id_record_unchanged":True,"structural_visit":True,
                "references_resolve":not missing,"status_or_application_change":False,
                "fresh_full_source_semantic_reproof":False})
    for item_id in graph["suspended_historical_rule_ids"]:
        prior=next(x for x in old_per["items"] if x["id"]==item_id)
        visited.append({"id":item_id,"kind":"suspended_rule_id",
            "inherited_record_sha256":prior.get("record_sha256"),"structural_visit":True,
            "suspended_status_preserved":True,"status_or_application_change":False,
            "fresh_full_source_semantic_reproof":False})
    assert len(visited)==1608 and len({(x["kind"],x["id"]) for x in visited})==1608
    assert not [x for x in unresolved if x["id"] in baseline_rules],unresolved
    per_id={"completed_map":"UCT-MAP-v1.1.2","source_graph_sha256":expected,
        "scope":"All1608 structural visits and unchanged record/status checks; no full historical semantic reproof.","items":visited}
    (HERE/"BASELINE_PER_ID_STRUCTURE.json.gz").write_bytes(gzip.compress(json.dumps(per_id,ensure_ascii=False).encode(),mtime=0))
    candidate_ids=[x["id"] for key in ("nodes","rules","context_links") for x in candidate[key]]
    assert len(candidate_ids)==len(set(candidate_ids))
    assert not (set(candidate_ids)&(baseline_nodes|baseline_rules|prior_ids|set(graph["suspended_historical_rule_ids"])))
    node_ids={x["id"] for x in NODES}; empirical={x["id"] for x in NODES if x["kind"] in {"SECONDARY_EVIDENCE","NEGATIVE_SECONDARY_EVIDENCE","ARITHMETIC_CORRECTION"}}
    node_reviews=[]; evidence_files={}
    for item in NODES:
        assert item["all_premises"] and item["domain"] and item["quantifier"] and item["counterexamples_and_limits"]
        for p in item["evidence_paths"]+[x["path"] for x in item["proof_locations"]]:
            full_path=PACKAGE/p;assert full_path.is_file(),p
            evidence_files[p]={"path":p,"sha256":digest(full_path.read_bytes()),"bytes":full_path.stat().st_size}
        node_reviews.append({"id":item["id"],"kind":item["kind"],"record_sha256":record_digest(item),
            "local_semantic_review":"Full statement, object/quantifier, complete premises, proof/evidence location and limits reviewed in the CTD2 response-model scope.",
            "enabled":False,"actual_application_established":False})
    for item in RULES:
        assert set(item["all_of"])<=node_ids and item["conclusion"] in node_ids
        assert not (set(item["all_of"])&empirical)
        assert not any(x in {"A:C1","A:U1"} for x in item["all_of"])
        assert item["same_instance_required"] and item["binding"]
        node_reviews.append({"id":item["id"],"kind":"conditional_rule","record_sha256":record_digest(item),
            "local_semantic_review":"Conjunction, same-instance binding, mathematical domain and conclusion checked; alternatives preserved.","enabled":False,"actual_application_established":False})
    for item in contexts:
        assert item["from"] in node_ids and item["to"] in node_ids|baseline_nodes
        assert item["deductive"] is False
        node_reviews.append({"id":item["id"],"kind":"nondeductive_context","record_sha256":record_digest(item),
            "local_semantic_review":"Typed as evidence, motivation or compatibility only; no C1 bridge or premise promotion.","enabled":False,"actual_application_established":False})
    assert all(x["enabled"] is False and x["enabled_as_established_premise"] is False for key in ("nodes","rules","context_links") for x in candidate[key])
    # No cycle among conditional theorem dependencies (necessary, not sufficient for validity).
    adjacency={x:[] for x in node_ids}
    for rule_item in RULES:
        for p in rule_item["all_of"]:adjacency[p].append(rule_item["conclusion"])
    white=set(node_ids); gray=set();black=set()
    def visit(x):
        assert x not in gray,"Conditional candidate cycle"
        if x in black:return
        gray.add(x)
        for y in adjacency[x]:visit(y)
        gray.remove(x);black.add(x);white.discard(x)
    while white:visit(next(iter(white)))
    selected_core=["A:TOKEN_CRITERIA","A:ACTUAL_TOKEN","A:C1","A:U1",
        "R168:PARTIAL_VIEW_NONENTAILMENT","R169:METRIC_SCALE_GAUGE_NONENTAILMENT",
        "R169:HELDOUT_CALIBRATION_FALSIFIER","R177:JOINT_SOURCE_FEATURE_DOMAIN",
        "R177:SOURCE_FEATURE_SEPARATION","R188:COMMON_STIMULUS",
        "R188:IDEAL_NOT_INSTALLED","R188:INFERENCE_CONTRACT"]
    assert set(selected_core)<=baseline_nodes
    receipt={"schema":"uct-map-review-receipt/1","id":"CTD2-MAP-REVIEW-20261010-v1",
        "created_at_utc":datetime.now(timezone.utc).isoformat(),"status":"PASS_SCOPED_DISABLED_CANDIDATE; AUDIT_INCOMPLETE_FOR_FULL_HISTORICAL_SEMANTIC_PROMOTION",
        "candidate_sha256":digest(target.read_bytes()),"candidate_counts":{"nodes":len(NODES),"rules":len(RULES),"contexts":len(contexts),"total":len(candidate_ids)},
        "all_candidate_items_disabled":True,"duplicate_candidate_ids":0,"collisions_with_completed_or_v01_ids":0,
        "unresolved_candidate_references":0,"empirical_deductive_premise_uses":0,"C1_U1_deductive_premise_uses":0,
        "independent_and_correlated_criterion_routes_not_conjoined":True,"conditional_dependency_cycle":False,
        "baseline_before":baseline_counts,"baseline_after":baseline_counts,"active_rule_change":0,"completed_map_version_change":False,
        "baseline_effective_graph_sha256_before":expected,"baseline_effective_graph_sha256_after":digest(graph_bytes),
        "baseline_per_id_count":len(visited),"baseline_per_id_structural_record":"BASELINE_PER_ID_STRUCTURE.json.gz",
        "baseline_structural_reference_notes":unresolved,
        "preserved_external_context_references":external_context_references,
        "prior_v01_sha256_before":digest(old_bytes),"prior_v01_sha256_after":digest(read_research(old_prefix+"MAP_EXTENSION.json")),
        "prior_v01_13_4_7_disabled_unchanged":True,"inherited_open_obligations":old["open_obligations"],
        "inherited_open_debt":old_summary["inherited_open_debt"],"inherited_open_status_changes":0,
        "local_semantic_reviewed_candidate_items":node_reviews,"selected_baseline_core_semantic_comparisons":selected_core,
        "new_full_semantic_reproof_of_all_1608":False,"fresh_all_historical_source_depth_review":False,
        "unreviewed_scope":"Full historical proof/source-depth semantics; independent empirical truth of physical/phenomenal contracts; A3M substantive arguments; worldwide novelty priority.",
        "root_navigation_edits_by_this_script":False,"map_increment_completed":False,
        "concurrent_checkpoint":candidate["concurrent_checkpoint"],
        "publication_coverage":candidate["publication_coverage"],"evidence_files":sorted(evidence_files.values(),key=lambda x:x["path"]),
        "policy_sources":[{"path":x,"sha256":digest(read_research(x))} for x in ("RESEARCH_MASTER_GUIDE.md","FORMAL_MAP_REVIEW_POLICY.json","PUBLICATION_COVERAGE.json")],
        "reading_scope":"Current master-guide core policy read; governance policy and baseline/candidate records read. Historical AGENTS/review ledgers were sampled by relevant core/current sections, not claimed complete. Completed graph fully parsed structurally from the v1.1.2 capsule, not substituted by the smaller root historical graph."
    }
    assert receipt["prior_v01_sha256_before"]==receipt["prior_v01_sha256_after"]
    (HERE/"MAP_REVIEW_RECEIPT.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n")
    summary={"scope":"All1608 structural checks plus local CTD2 semantics; not full-map semantic reproof.",
        "source_graph_sha256":expected,"counts":baseline_counts,"unresolved_active_rule_references":0,
        "new_complete_semantic_review":False,"completed_graph_changes":0,
        "inherited_open_debt":old_summary["inherited_open_debt"],"candidate_items":receipt["candidate_counts"],
        "all_candidate_items_disabled":True,"v01_disabled_candidate_unchanged":True,
        "concurrent_A3M_preserved":True}
    (HERE/"BASELINE_STRUCTURE_SUMMARY.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"candidate":str(target),"counts":receipt["candidate_counts"],
        "baseline_counts":baseline_counts,"baseline_graph_sha256":expected,
        "v01_unchanged":True,"unresolved_baseline_reference_notes":len(unresolved),
        "all_candidate_disabled":True,"map_increment_completed":False},indent=2))


if __name__=="__main__":main()
