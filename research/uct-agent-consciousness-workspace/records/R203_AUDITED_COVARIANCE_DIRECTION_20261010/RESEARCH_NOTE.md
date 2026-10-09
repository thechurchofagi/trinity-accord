# R203 — Audited covariance direction: a sensitivity certificate and a calibration limit

Result: ACD-RESULT-v0.2.0. Date: 2026-10-10. Unpublished conditional research module.

## 1. Question and net advance

R202 identifies validation-domain prevalence and marker class-conditionals only with independently calibrated endpoint error rates and conditional nondifferentiality. Its preregistration skeleton inadvertently proposes checking dependence “within endpoint class” as though that were dependence within the unobserved experiential class. R203 corrects this substitution and weakens the information needed for a *direction* claim: exact endpoint sensitivity/specificity are unnecessary if an independently warranted endpoint direction and an independently warranted residual-covariance bound are available. Neither warrant is furnished by a successful marker/report association.

This is a specific UCT calibration application of established total-covariance and concentration mathematics. Mathematical novelty and worldwide priority are not claimed. The application separates feasible observable rejection tests from latent assumptions that an adult audit cannot self-certify.

## 2. One-instance contract

Fix reporting validation domain V, selected familiar-continuity coordinate H in {0,1}, preprompt marker M, fallible semantic endpoint J, and one actual bearer/episode/signature and actual-use stratum U=1. All probabilities below refer to this same contract. Random audit assignment must be implemented before outcomes and concealed until after M; prompt timing does not exclude effects of anticipating a prompt. Assignment and completed response are distinct: voluntary completion after randomized invitation can be selective. Missing responses must be retained and separately modelled.

Let pi=P(H=1), q_h=P(M=1|H=h), a=P(J=1|H=1), c=P(J=1|H=0), b=a-c, Delta=q_1-q_0, m=E[M], j=E[J], r=E[MJ], and K=r-mj. Require 0<pi<1 and independently signed b>0. Actual use U is not telemetry evidence E_U. Random assignment to a physical bypass is not proof of actual use in the corresponding retained-route arm.

## 3. R203-C1 — direction without exact endpoint errors

The law of total covariance gives

K = pi(1-pi)b Delta + R,

R = (1-pi)Cov(M,J|H=0) + pi Cov(M,J|H=1).

Proof: decompose E[MJ] into within-class covariance plus products of class means; subtract the product of mixed means. The between-class term is pi(1-pi)(q_1-q_0)(a-c). This identity does not assume conditional independence.

If R=0, sign(K)=sign(Delta). Thus signed reliability is enough for direction, although exact a,c remain needed for R202 point inversion. R=0 is weaker than full conditional independence, but cancellation cannot be inferred from observed fit. If independently justified |R|<=kappa and K>kappa, then Delta>0. If K<-kappa, Delta<0. Equality supports only a weak sign. If |K|<=kappa, this certificate abstains; this is not a proof that no other information could identify direction.

Since 0<pi(1-pi)b<=1/4, K>kappa also gives Delta>=4(K-kappa)>0. This is a conservative universal lower bound, not a tight identified set. Feasible binary covariance has |Cov(M,J|H=h)|<=1/4; the trivial bound kappa=1/4 cannot yield a strict positive certificate because |K|<=1/4. Therefore a nontrivial residual budget is indispensable. More samples do not shrink an unidentified structural budget.

## 4. R203-C2 — a complete observational twin, with fixed endpoint accuracy

Both worlds have pi=1/2, a=4/5 and c=1/5. Conditional cells are ordered (M=0,J=0), (0,1), (1,0), (1,1).

| World | H=0 cells | H=1 cells | Delta | R |
| --- | --- | --- | --- | --- |
| Independent | (12,3,8,2)/25 | (2,8,3,12)/25 | +1/5 | 0 |
| Dependent | (19,1,21,9)/50 | (9,21,1,19)/50 | -1/5 | 3/50 |

Both mix to observed cells (14,11,11,14)/50, hence m=j=1/2, r=7/25 and K=3/100. All cells are nonnegative and sum to one. Both dependent within-class covariances equal 3/50. The exact checker verifies full tables, not just moment algebra. Intermediate transcription mistakes were corrected before finalization and retained in FAILURES.md.

This witness shows that even *known identical* a,c and an identical observed binary joint law do not identify Delta if residual dependence is unrestricted. Independent random key/audit variables can be appended identically to both worlds; their balance cannot distinguish these two laws. No claim is made that all possible physical interventions fail, only that the declared audit information is insufficient.

## 5. R203-C3 — finite-sample certificate

Use n independent draws of complete audited episodes from the fixed contract. A conservative implementation uses one prospectively chosen episode per independently sampled adult; repeated trials from one adult are not n independent adults. Let mhat,jhat,rhat be means of M,J,MJ. At fixed n and alpha, h=sqrt(log(6/alpha)/(2n)). Hoeffding's inequality and a union bound simultaneously contain all three true means in their clipped +/-h intervals with probability at least 1-alpha. Dependence of M and J within an episode is allowed.

Set L_K=r_L-m_U j_U and U_K=r_U-m_L j_L. If L_K>kappa and the external premises hold, certify positive validation-domain direction, with Delta>=4(L_K-kappa). If U_K<-kappa, certify negative direction. Otherwise abstain. The error control is conditional on the nonstatistical premises; it does not make those premises true. An externally estimated kappa needs its own simultaneous confidence allocation. Multiple cells/markers need an alpha budget; optional stopping needs a different sequential bound. The supplied fixed-n rule is not sequentially valid.

The CLI returns OBSERVABLE_ASSOCIATION_ONLY unless all specified premise warrants are recorded. User-supplied true flags record assumed warrants; the software does not validate them. Synthetic tests establish implementation, not human H.

## 6. Correction of the experimental skeleton

“Within endpoint class” is not “within H class.” Conditioning on J makes J constant and its covariance with M vacuously zero. Repeated reports, agreement, split samples and latent-class fit do not independently establish b>0 or bound R. This is the central calibration debt that the proposed adult audit must disclose.

A physical bypass effect cannot automatically reject every marker bridge: a marker might track H that remains on an alternate route, or the bypass may fail to change the declared carrier use. Only a preregistered *route-necessity* claim with matched alternatives is rejected by preservation under a verified bypass. Similarly, selecting only successful trials or conditioning on post-treatment fluency can create collider bias; randomize externally controlled feedback/difficulty, retain all trials and label actual-success stratification as descriptive.

The concrete adult design and its observable/latent decision table are in PRE_REGISTRATION_PROTOCOL.md. It is executable as an analysis protocol but has not recruited participants, validated H, or installed a physiological instrument.

## 7. Thought experiments and relation to UCT

A report/marker twin with the tables above defeats automatic calibration. A key flip tests motor coding after semantic recoding, not endpoint truth. A common-fluency cause can preserve the same measured association without positive H tracking. A verified physical bypass attacks one specified route bridge, not basal experience. Complete copy/switch systems retain R199's continuation-probe limit; no association identifies numerical lineage. Ancestor/formation, abacus/calculator, human-implemented-agent and gradual replacement cases preserve actual-process admission, the report-domain boundary, and possible local/whole experience coexistence.

C1 remains a consciousness-specific explanatory postulate. Neither this certificate nor its failure adds a report, control, language, self-model or familiarity threshold to basal experience. The present result does not derive RetBind, H semantics, an exclusive owner or current-assistant consciousness. V-to-T transport remains separate.

## 8. Evidence, originality and decision

The exact checker revalidates 20,412 conditional-independent denominator-eight models, verifies feasible dependent binary tables, traverses all denominator-four within-class distributions crossed with seven nondegenerate prevalences, and checks residual-budget certificates. RUN_RECEIPT.json records actual execution. General proofs are in §§3–5; enumerations check bounded instances only.

Hui and Walter (1980), DOI 10.2307/2530508, require explicit independence and population assumptions for no-gold-standard diagnostic estimation. Keddie et al. (2023), DOI 10.1186/s12874-023-01873-0, show conditional-dependence misspecification biases diagnostic estimates. Hoeffding (1963), DOI 10.1080/01621459.1963.10500830, supplies the bounded-variable tail inequality. These are precedents, not evidence validating UCT H. Full Keddie text was accessed; Hui/Walter and Hoeffding were limited to primary metadata/abstract retrieval. Global priority remains unverified.

Net contribution: a minimal signed-direction interface, an exact same-accuracy opposite-direction twin, and a corrected preregistered distinction between measurable rejection tests and latent warrant. This is a reusable methods module for the R192–R203 family, not an actual consciousness measurement or standalone empirical breakthrough. Decision: CONTINUE_RESEARCH_HOLD_STANDALONE. No publication action is taken.
