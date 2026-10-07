# Forming bodily and action attribution: a finite mechanism and its phenomenal limit

Research note R155, version 0.1, 7 October 2026. Unpublished working extension of the UCT map; parent 5123c4c20d09fc7102225376ac30c943ed48090d.

## 1. Target and contribution

The target is the formation of bodily/action-related organization **within experience**, not the onset of basal experience or the selection of an extra owner. A UCT I v1.2 §§8.11–8.14 distinguishes physically witnessed body-centered organization, functional self-models and conceptual I. R146 supplied the self-model contract; R147 showed that accurate action prediction does not fix actual assembly attachment. This note adds an explicit acquisition mechanism, installed consumers, mistaken-attribution histories, a finite-memory boundary and a precise outstanding phenomenal-interpretation obligation.

The construction below is elementary Bayesian updating, not a new Bayesian theorem. Its project contribution is a single inspectable contract connecting formation, error, intervention, memory and the UCT interpretation boundary. It does not reproduce a human experiment, establish a biological implementation, or resolve felt mineness by naming a register “ownership.”

## 2. Four targets that must remain distinct

| Target | Symbol and domain | Meaning and boundary |
|---|---|---|
| Actual attachment | alpha(P,t) | Actual sensory/action/assembly relations of a specified bearer P, independently grounded. Can be nested or overlapping; not inferred merely from its confidence. |
| Sensory source attribution | q_O in (0,1) | Installed estimate of a specified common-source hypothesis H; no claim that common source is sufficient for bodily ownership. |
| Action efficacy attribution | q_A in (0,1) | Installed estimate of a specified command-response hypothesis K under a fixed intervention protocol; not the whole philosophical or phenomenal sense of agency. |
| Selected felt mineness | F_O(P,t), F_A(P,t) | Selected experiential targets, if independently defined. Neither is defined here as q, a threshold output, report, or actual attachment. |

Conceptual I, autobiographical identity and numerical persistence are separate targets. H concerns the candidate sensory source, not the identity of P. A high q_O can therefore be accurate about a shared external source while false as an assembly-membership judgment. A false H inference and a false membership interpretation are two different errors.

The represented signature contains typed candidate-source and command/response ports, trial counters, success counters, fixed update relations and two consumer ports. A physical realization requires these causal roles to be installed and independently witnessed. An abstract table alone does not identify its complete constitutive organization.

## 3. Fixed finite acquisition contract M

Fix integer T >= 2, a bearer/candidate/port assignment and an externally fixed trial schedule, with at most T source trials and T action trials. The schedule and feature extraction do not select trials according to unreported outcomes. There is one source candidate, one response port, one temporal grain and no target switching. Each comparison retains these choices. No infinite-time limit or evolutionary trajectory is assumed.

H,K belong to {0,1} and are constant over this window. They name hypotheses in this toy generative family. Set their priors independently to 1/2. Conditional on H,K, all trial noises are independent; the source observations depend only on H and action responses only on K. These are substantive assumptions, not UCT axioms.

On each source trial observe X in {0,1}, a predeclared cue-concordance feature, with

    Pr(X=1 | H=1)=3/4; Pr(X=1 | H=0)=1/4.

The intended source interpretation of H requires independent grounding of the cue construction and the two source conditions. These numbers are illustrative, not fitted neural parameters. They do not assert that synchrony is necessary for human ownership.

On each action trial a fair randomized intervention sets U in {0,1}. Under K=1, Y=U xor N with Pr(N=1)=1/4. Under K=0, Y is an independent fair bit. Noise and intervention are independent. Record Z=1[Y=U]. Thus

    Pr(Z=1 | K=1)=3/4; Pr(Z=1 | K=0)=1/2.

K=1 denotes this specific noisy positive command-response law; K=0 this specific null law. Other effective mappings, delays, intentions and action classes lie outside M. In particular, an inverted response can be controllable although it is outside both hypotheses. The randomized interventions establish the protocol, not a claim that any observed correlation is causal. If observational actions share an unmeasured cause with Y, the intended inference about action efficacy is unavailable.

The installed state is m=(n_O,r,n_A,s): source trial count, number of X=1 observations, action trial count and number of Z=1 observations. Initially all are zero. On the appropriate trial increment its count and success count. Skip an absent channel; do not encode missing data as a failure. Stop acquiring at its declared T. The state has at most [(T+1)(T+2)/2]^2 possible configurations, including combinations reachable under different schedules. This is a sufficient bound, not a minimal physical implementation or a bound on the containing process.

The fixed readouts are

    odds_O = 3^(2r-n_O); q_O = odds_O/(1+odds_O),
    odds_A = 3^s/2^n_A; q_A = 3^s/(3^s+2^n_A).

Finite T makes an exact rational lookup possible with finite encodings. There is no precision-free real-number oracle. Missing action trials leave q_A=1/2; that is no acquired action evidence, not absence of felt agency.

For an explicit installed use, fix threshold theta=2/3. Consumer C_O=1[q_O>=theta] enables the candidate-source fusion branch. Consumer C_A=1[q_A>=theta] enables the own-command predictor branch. Interventions on the corresponding state/readout, holding the remaining consumer inputs fixed, change the specified branch when crossing the threshold. These consumers witness causal use in the represented device. They do not establish human semantics or felt experience; physical installation remains an additional realization obligation. Keeping the evidence protocol external prevents these consumers from silently changing its sampling law.

## 4. Propositions and complete local arguments

### P1. Finite formation and posterior correctness within M

For every legal finite history, the two readouts equal the respective Bayesian posteriors under M. There is no threshold discontinuity in the posterior as a function of positive likelihoods; threshold consumers can be discontinuous.

Proof. One X=1 multiplies prior odds by (3/4)/(1/4)=3; X=0 multiplies by (1/4)/(3/4)=1/3. After n_O trials the product is 3^r 3^(-(n_O-r)). A Z=1 multiplies action odds by (3/4)/(1/2)=3/2, Z=0 by (1/4)/(1/2)=1/2. The product is 3^s/2^n_A. Conditional independence and the factorized prior make each channel's other observations cancel in its marginal posterior. Normalizing odds proves the formulas, including the empty-history value 1/2. The counter update realizes these products without reconstructing the entire history. For fixed finite history, positive prior/likelihood products have a positive denominator; their ratio is continuous. A comparison q>=theta is an independently installed discrete operation. QED.

Boundary. Posterior correctness is relative to M, not a certificate of truth, calibrated human selfhood or constitutive completeness. Coupled H,K priors or shared noise generally require a joint updater. For example, if H=K almost surely, evidence in either channel informs both and independent marginal updating is incorrect. T bounds trials and memory; it is not an experience threshold.

### P2. Four separable installed attribution outcomes

At n_O=n_A=2, the same M and fixed consumers admit all four pairs (C_O,C_A) in {0,1}^2, each with positive probability under every fixed H,K.

| Source history X | Action match history Z | q_O | q_A | (C_O,C_A) |
|---|---|---:|---:|---|
| 11 | 11 | 9/10 | 9/13 | (1,1) |
| 11 | 00 | 9/10 | 1/5 | (1,0) |
| 00 | 11 | 1/10 | 9/13 | (0,1) |
| 00 | 00 | 1/10 | 1/5 | (0,0) |

Proof. Substitute the four count pairs into P1, compare to 2/3, and use full support and conditional independence. The source branch changes with X while the action branch, action law, intervention schedule and Z are fixed; conversely for Z. QED.

This establishes separability of installed functional attributions in M, not phenomenal double dissociation in every organism. The threshold is specified before selecting histories. Other thresholds or coupled consumers can remove this particular four-row witness. No inference to a change in actual attachment follows from any row.

### P3. Acquisition permits error and does not certify actual attachment

No finite history in M rules out any of the four latent pairs (H,K). In particular, the high/high consumer row is possible with H=K=0, with probability (1/4)^2(1/2)^2=1/64 for the specified X and Z histories conditional on H=K=0. Under the 1/4 prior probability of that latent pair the joint event has probability 1/256.

Proof. Every source and match likelihood in either hypothesis is strictly positive. Products over finite histories and positive prior weights remain positive. Bayes normalization cannot turn an alternative's weight into zero. The stated event probability follows by conditional independence. The acquisition equations contain no alpha; so alpha cannot be recovered without a separate constraint linking alpha to this evidence-generating mechanism. R147 supplies an independently grounded illustration: matched sensor/action rewiring can preserve the complete sensor-response law while changing assembly-relative attachment. It is not necessary to treat alpha as an arbitrary free variable in an actual physical system. QED.

Even a correctly inferred common source need not be the containing body's source. Accuracy, functional usefulness and actual membership are distinct. The posterior's failure is not evidence for absence of any experience.

### P4. Installed history changes attribution; unlimited exact updating exceeds finite state

At the same counts n_O=n_A=2, copy the complete state (2,2,2,2) in place of (2,0,2,2), holding current ports, actual attachment and current input fixed. q_O changes from 1/10 to 9/10 and C_O changes from 0 to 1; q_A stays 9/13. Before any new trial the source consumer differs. This is a causal difference of installed memory, not just a changed report. The copied state need not remain a truthful posterior of the recipient's own history.

Proof. Readout substitution suffices; no update or rewiring occurs. This differs from R147's explicitly report-isolated autobiographical register. There is no contradiction because its isolation premise is absent here.

For a deterministic finite-state updater with readout depending only on that state and no external unbounded clock or memory, exact q_O for **all unbounded all-success histories** is impossible. After n successes, q_O(n)=3^n/(1+3^n), strictly increasing in n. Infinitely many different outputs are required, but finitely many states have only finitely many fixed outputs. QED.

This is a standard finite-state counting obstruction, not a new result about consciousness. Finite T avoids it. An unbounded implementation must admit growing storage, approximation, saturation, forgetting or another declared change. None implies copying a subject, autobiographical continuity or transfer of experience.

## 5. What UCT does and does not contribute

C1 supplies the experiential interpretation of actual complete organization. C1-OI relates its complete organization type to its complete experiential type. Neither axiom alone names a selected coordinate “felt ownership.” A mathematically different q does not by itself certify that two physical tokens have different complete constitutive types: the realization and preservation of the typed state/use relations must be supplied. Even a certified full-type difference does not identify which experiential coordinate differs.

Let Omega be a fixed class of actual bearer/window configurations admitting the same complete signature and target convention. Let J:Omega->Jspace encode the declared finite organization descriptor, and let F:Omega->Fspace be an independently specified selected mineness target. A fixed decoder psi with F=psi∘J exists exactly when F is constant on every J-fiber. Necessity: equal J gives equal psi(J). Sufficiency: assign each realized J value the common F value of its nonempty fiber. This is the existing C:P2_COORD factorization criterion applied to this target, not a newly discovered theorem. No injectivity, order or monotonicity of psi follows.

Candidate B_MIN must therefore independently provide: (a) valid actual bearers and physical realization; (b) the selected experiential target, within experience rather than behind it; (c) a fixed non-oracular cross-condition interpretation; (d) the required fiber constancy or a restricted domain where it holds; (e) an independently justified measurement bridge for empirical use. These are OPEN obligations. Defining F=psi(J) by fiat would make factorization true without establishing that F is mineness. Reports, proprioceptive drift and intervention effects are separate measurement candidates, not automatically F.

Thus this note derives functional formation and bounded failures. It does not claim that these mechanisms are necessary or sufficient for felt mineness, or for basal experience. No proof edge from P1–P4 alone to F is permitted. A valid physiological bridge might require affect, interoception, temporal integration or other relations omitted here; this is a research question, not an imported conclusion.

## 6. Two explanations and discriminating comparisons

Prediction-only proposal PRED: a selected bodily-attribution output is a fixed function of the declared action-prediction evidence Z, with all other target/background commitments held fixed. Two-channel proposal ATTR: that installed output depends on X through q_O while action-efficacy attribution depends on Z through q_A, within M. These are restricted operational proposals, not complete reductions of predictive processing or another broad consciousness theory.

Compare rows 1 and 3 of P2: same Z, action law, action posterior and schedule; different X and source consumer. PRED cannot reproduce both **specified consumer outcomes** with a fixed function of Z; ATTR can. This comparison establishes a distinction within the designed device. To discriminate explanations of felt ownership, independently mapped source cues and mineness measurements, matched background and a fixed bridge are needed. It is invalid to insert the desired experiential labels into the model and call the match validation.

Kalckert and Ehrsson (2012) manipulated timing, movement mode and hand position, obtaining experimentally dissociable ownership and agency measures. Their result motivates separate targets; it does not establish this binary mechanism. Samad, Chung and Shams (2015) modeled ownership using Bayesian multisensory causal inference and tested predictions, including ownership without tactile stimulation. Bayesian ownership inference is therefore prior art; this note's binary source channel is a deliberately simpler construction, not a replication of their spatial/temporal model.

The present work does not assess all predictive-processing accounts or claim superiority over that literature. No new human data, fitted parameters, broad novelty search or clinical conclusion is offered.

## 7. Four required thought-experiment families

| Family | Concrete modification | Consequence and excluded inference |
|---|---|---|
| Ancestors and formation | Add bounded counters, the crossmodal input route and then consumer connections to successive organizations. Separately vary reliability within a fixed positive-likelihood family. | Acquisition and causal use become possible under explicit structures. P1's finite posterior is continuous in positive likelihood parameters; threshold readout need not be. This is an engineering construction, not a reconstruction of evolution or a proof of continuous basal-experience onset. |
| Abacus and calculator | External analyst calculates q versus a device storing counters and causally routing the resulting branch. | Same written answer does not establish the same installed self-related organization. An abacus can participate in a larger installed process if actual couplings realize the roles; substrate names alone do not decide this. Neither case is declared experience-free. |
| Humans implementing an agent | Humans pass encoded cues, maintain counters and execute the two fixed consumers, including intervention alternatives. | Actual message/use relations must be specified beyond matching one transcript. The whole process and participating humans may supply nested/overlapping tokens. A simulated posterior supplies no unique exclusive owner and does not identify the complete organization. |
| Copying, rewiring and memory | Apply R147's matched sensor/action swap; separately copy the installed m of P4 rather than an isolated report record. | Prediction can survive altered attachment; installed memory can alter attribution without changing attachment. Copying neither proves numerical persistence nor moves experience between bodies. |

These modifications determine which assumptions apply. They are not mere illustrations of an already assumed experiential answer.

## 8. Joint audit and open failures

1. **No basal gate:** all thresholds concern consumers in M, never U1. Removing counters removes this mechanism, not all possible experience or self-related feeling.
2. **No semantic substitution:** common sensory cause, assembly membership, commanded efficacy, felt agency, conceptual I and numerical identity remain distinct. P2 is not a theorem about their universal independence.
3. **No hidden proof premise:** M states prior, likelihoods, independent noises, legal interventions, fixed feature extraction/schedule, horizon, consumer and common target. Physiological validity is not among its derived results.
4. **Missing observations:** passive movement supplies no intervention evidence in this protocol. A neutral q_A is not phenomenal absence; a different passive agency model requires a new contract.
5. **Joint-model failure:** shared causes or dependent prior hypotheses break marginal posterior correctness; a joint learner or explicit approximation is required. Fixed likelihoods can become wrong after rewiring or drift.
6. **Finite-view limit:** alpha, complete ontic organization and selected F are not identified by two probabilities. New mineness semantics remain open even when full organizational typing is known.
7. **History/provenance:** an installed copied estimate affects use but is no longer automatically the recipient's posterior. A copy of descriptive text with no consumer path is R147's different case.
8. **Physical resolution:** the exact finite rational table is implementable abstractly; no neural encoding, intrinsic boundary criterion or unique privileged scale has been established.
9. **What would weaken this route:** absent source-consumer causal influence in a proposed realization; a fixed-domain F contrast on a common J-fiber; inability to specify F independently of q; failure of the chosen generative family. The first targets installation, the second the proposed sufficiency bridge, the third semantic definition, and the fourth the likelihood model. They do not have the same implications for UCT.

The next substantive obligation is a **selected-mineness bridge comparison on a fixed domain**, using an independently specified target and competing sufficient descriptors. Expanding the register count cannot itself discharge it. This note makes the bridge obligation sharper; it does not mark F153-11 or F153-17 closed.

## References and exact provenance

- UCT I v1.2, DOI 10.5281/zenodo.23131575, §§8.11–8.14; pinned project snapshot `records/R128_Unified_Formal_Map_Audit_20261006/sources/A_UCT_I_v1_2.md`.
- R146, `records/R146_Experience_Intelligence_and_Self_20261007/Experience_Intelligence_and_Self_v0_1.md`; R147, `records/R147_Self_Reference_Rewiring_20261007/SELF_REFERENCE_REWIRING.md`.
- Kalckert, A., & Ehrsson, H. H. (2012). Moving a Rubber Hand that Feels Like Your Own: A Dissociation of Ownership and Agency. *Frontiers in Human Neuroscience*, 6, 40. https://doi.org/10.3389/fnhum.2012.00040
- Samad, M., Chung, A. J., & Shams, L. (2015). Perception of Body Ownership Is Driven by Bayesian Sensory Inference. *PLOS ONE*, 10(2), e0117178. https://doi.org/10.1371/journal.pone.0117178

Primary web pages checked 7 October 2026. Targeted sections/abstracts were read; no participant-level reanalysis or exhaustive external-theory audit. P1–P4 are manually argued finite mathematical claims; executable checks supplement them and are not proof-assistant certification.
