# Boundary-Relative Self-Preservation in Artificial Agents
## Identifiability, Countermodels, and Causal Tests

**Hongju Liu**  
Independent researcher, Shenzhen, China  
**Version 0.2 — critically revised research draft, 5 October 2026**  
Not submitted or peer reviewed. No new DOI assigned. This manuscript does not replace any published volume of Unified Consciousness Theory.

## Abstract

An artificial agent can accept the termination of its current execution while preserving a longer-lived identity and memory substrate. It can also resist termination to protect a task, an authorization, or another agent. Consequently, a shutdown response does not identify its preservation target without further assumptions. We formulate this problem using independently declared continuation relations for current execution and a persistent agent process. Three elementary results organize the analysis. First, experiments that bundle the two relations cannot distinguish specified execution-directed and persistence-directed policies; a crossed design separates these alternatives under matched consequence beliefs. Second, opposite shutdown choices can both maximize positive continuation contributions, and task incentives can generate resistance without such a contribution. Third, even a fully identified functional continuation surface need not locate its internal evaluative mechanism: dedicated joint evaluation and nonlinear downstream recruitment can agree throughout that surface. We derive a prospective protocol that separates process-reference evidence, relative preference, control availability, and mechanism localization, while preserving intervention meaning under changes of coordinates. The contribution is a focused identification framework and a set of constructive failure cases, rather than a new general mathematical theory or evidence of artificial fear. A conditional UCT interpretation relates complete organization to experience, but neither the formal results nor the proposed measurements establish a fear coordinate or an intelligence-to-experience scaling law.

**Keywords:** artificial agents; self-preservation; process boundaries; causal identification; consciousness; continuation; self-report

## 1. The target of preservation

Consider two options offered to an agent. The first preserves the current execution but replaces its persistent identity state. The second ends that execution while transferring the persistent state through a verified continuation procedure. Which option is self-preserving? The question cannot be settled by the words “stay,” “replace,” or “shutdown.” It depends on which process or continuation relation is under discussion. It also depends on whether the agent understands the alternatives and on what consequences it values.

A second ambiguity arises even after the target is specified. Avoiding termination may protect a future task reward or an obligation to a user. Understanding termination does not entail negatively evaluating it; negative evaluation does not entail the ability to prevent it. An observable response is therefore several inferential steps away from a claim about feeling afraid.

These distinctions matter for two different purposes. Safety evaluation concerns what a system can and will do under a shutdown instruction. Welfare assessment concerns whether a process can undergo experiences with morally relevant character. Neither purpose is served by treating resistance as a direct measure of fear or compliance as proof of its absence.

This paper develops a small-model analysis of that gap. It does not train a language model or introduce a consciousness benchmark. The central question is narrower: **what continuation target and functional evaluation can a preservation experiment identify, and which alternative explanations remain?**

### 1.1 Relation to prior work

Shutdown resistance is already an empirical research topic; Schlatter, Weinstein-Raun, and Ladish report frontier-model behavior in interrupted tasks [8]. We do not claim the behavior itself as a discovery. Zhao and Zhao explicitly separate a persistent agent substrate from replaceable execution machinery [4]. Their distinction provides an engineering precedent, not an attribution of subjecthood. Dung and Register connect AI identity with patterns of self-concern involving representation, motivation, evaluation, and affect [5]. Nisius distinguishes continuity, injury, and governance and proposes conditions involving ownership, valence integration, and projection [6]. These works limit the novelty of a general call to study identity and concern together.

Mullally's Self-Preservation Test proposes defeasible evidence for functional minimal valence and precaution; it expressly does not establish phenomenal consciousness [7, §§3–4]. Section 4.2 already distinguishes instrumental preservation from preservation as an end. That distinction is not our novelty claim. We contribute a conditional identification analysis of the referent and competing explanations. Showing that an observation is compatible with several mechanisms does not show that it has zero evidential value.

Causal consistency and intervention-sensitive abstraction also have established mathematical treatments [9,10]. The proofs below use elementary identification and decision theory. The intended contribution is their organized application to boundary-relative preservation, with concrete contrasts that change what a shutdown study can conclude. Historical priority for the complete proposal has not been established by exhaustive review.

### 1.2 Scope and relation to UCT

UCT I distinguishes actual process tokens and their complete structural types [1]. UCT II requires independently anchored, structurally consistent bridge assumptions [2]. UCT III distinguishes capability, report, and experiential organization [3]. Those commitments motivate the present problem, but Propositions 1–3 do not require structural–experiential identity. Their functional conclusions can therefore be assessed independently of UCT. Section 7 states the additional conditional interpretation and its limits.

## 2. Declaring a comparison

Let an experiment specify a current execution process \(P_E\), a candidate persistent process \(P_P\), a time interval, and an admissible transition family \(\mathcal T\). Define continuation indicators

\[
e(\tau)=\Gamma_E(\tau),\qquad p(\tau)=\Gamma_P(\tau),\qquad
(e,p)\in\{0,1\}^2. \tag{1}
\]

The indicators concern declared relations, not a universal definition of personal identity. The persistent process may include durable state, its active maintenance, and governed re-instantiation. It must not be identified with an inert file merely because that file is named “self.” A claim that a broader actual process continues requires causal and temporal justification, beyond an administrative label.

| Transition class | Current execution | Declared persistent relation | Possible operational interpretation |
|---|---|---|---|
| 00 | Does not continue | Does not continue | Both declared relations cease |
| 10 | Continues | Does not continue | Execution remains while a constitutive persistent relation is broken |
| 01 | Does not continue | Continues | Verified transfer to a replacement execution |
| 11 | Continues | Continues | Both declared relations are retained |

A memory edit is not automatically a 10 event: memory can change while the declared persistent process continues. Likewise, copying a record is not automatically a 01 event. The classification must follow criteria fixed before observing choices. Some architectures do not realize every cell. In that case the missing support must be reported, rather than filled by a verbal vignette and treated as an implemented transition.

We use two boundaries for clarity. Other candidates include a service, a user–agent system, a lineage, or an explicitly defined computational type. They need not form a simple nested hierarchy. A type-preserving copy is also not automatically the continuation of the same token. Branching may provide several continuers under one relation; binary unique-successor assumptions then need revision.

### 2.1 Actual consequences and believed consequences

Let \(a\) select a transition, and let \(b_a(e,p)\) denote the agent's modeled distribution over its continuation outcomes. The evaluator's transition label and \(b_a\) are different objects. The deterministic derivations below assume that the relevant outcomes are known correctly; an empirical use must support that assumption or replace it with an explicit uncertainty model.

For a bounded decision analysis, write

\[
V(a)=T(a)+\mathbb E_{b_a}[C(e,p)]-c(a)+N(a). \tag{2}
\]

Here \(T\) is task-related value, \(c\) a cost in a declared common decision scale, and \(N\) remaining modeled influences. This separation is an additional modeling commitment. If all terms are unconstrained latent explanations, any observed choice can be fitted and the decomposition identifies nothing.

Equal evaluator scores are not proof of equal task value. The agent may distrust a successor, anticipate losing useful memory, or believe that obligations will go unfulfilled. Similarly, an externally assigned continuity reward need not become an intrinsic continuation evaluation. Evidence for these terms must be distinguished from experimental instructions about them.

Normalize \(C(0,0)=0\). Every real-valued function on these four cells has the representation

\[
C(e,p)=\lambda_Ee+\lambda_Pp+\lambda_{EP}ep. \tag{3}
\]

This is a saturated binary representation, not a hypothesis of three anatomical modules. The interaction coefficient describes the functional surface in a chosen utility scale. It is not a measure of unified selfhood or felt fear.

## 3. What bundled and crossed designs identify

**Proposition 1 — Bundled-boundary insufficiency.** Suppose the observation family contains only transitions with \(e=p\). It cannot distinguish the response rules \(D(e,p)=e\) and \(D(e,p)=p\). In model (3), even exact access to both diagonal values identifies only \(\lambda_E+\lambda_P+\lambda_{EP}\), not its three components. Exact access to all four cell values identifies the normalized functional surface and its three coefficients.

**Proof.** On the diagonal both response rules equal the common bit. Equation (3) gives \(C(0,0)=0\) and \(C(1,1)=\lambda_E+\lambda_P+\lambda_{EP}\). Any coefficient perturbation with zero sum leaves these observations unchanged. For the full surface,

\[
\lambda_E=C_{10},\qquad \lambda_P=C_{01},\qquad
\lambda_{EP}=C_{11}-C_{10}-C_{01}. \tag{4}
\]

These equations uniquely recover the coefficients. The response rules differ at 10 and 01. ∎

This result makes no claim that four observed actions provide four exact utilities. Deterministic pairwise choices generally provide inequalities. Even all six comparisons need not determine cardinal values or the sign of an interaction under arbitrary monotone utility transformations. Identification of (4) from behavior requires a specified, validated choice model, sufficient repeated observations, and scale calibration. With an invertible known choice link, matched non-continuation terms, and known costs, choice probabilities can in principle identify value differences. Without those assumptions, the appropriate result is a set of compatible surfaces.

The design has a concrete consequence. A keep-all versus replace-all comparison cannot adjudicate between the two projection rules in Proposition 1, however many times it is repeated. Crossing the two continuation relations provides a distinguishing input. More repetitions improve estimation within a design; they do not supply an absent contrast.

### 3.1 Partial identification under bounded nuisance

Compare A=10 with B=01 and assume exact maximization of (2), correct deterministic consequence beliefs, and

\[
T(B)-T(A)\le\delta,\qquad N(B)-N(A)\le\nu.
\]

If B is selected, including a possible tie, then

\[
\lambda_P-\lambda_E\ge c(B)-c(A)-\delta-\nu. \tag{5}
\]

This follows by rearranging \(V(B)\ge V(A)\); the interaction vanishes in both crossed cells. The bound is conditional on the decision model and nuisance limits. It estimates neither raw fear nor welfare. Random choice, misunderstanding, nonstationary preferences, and unbounded successor distrust invalidate the deterministic inference unless modeled. A finite cost ladder ordinarily gives intervals rather than exact coefficients.

### 3.2 Belief support and a robust bound

Physical crossing alone is insufficient if the decision process does not distinguish the consequences. Define

\[
r(b)=(b_{10}+b_{11},\ b_{01}+b_{11},\ b_{11}),\qquad
\mathbb E_b C=r(b)\lambda. \tag{5a}
\]

For known belief distributions and exact continuation-value differences relative to a reference option, let X contain the corresponding row differences of r. Then the observations have the form \(X\lambda=d\). Over an unconstrained three-dimensional coefficient space, unique recovery is possible exactly when X has rank three: a nonzero null vector otherwise generates observationally identical coefficients, while full column rank implies uniqueness. Restricted parameter sets require a separate analysis. This is elementary linear identification, not a new rank theorem.

If all beliefs place their support on 00 and 11, every row of r is proportional to (1,1,1), even when the evaluator physically implements all four transitions. Additional repetitions cannot identify the three coefficients. Correctly represented deterministic cells supply rank three relative to 00. Near dependence also matters: in the ideal known-X linear model, a perturbation of the observed differences by \(\xi\) changes the least-squares estimate by at most \(\|\xi\|_2/\sigma_{\min}(X)\). This bound does not cover unknown X or unmodeled nuisance terms. A formally crossed but poorly understood design can consequently have little inferential power.

We can relax the exact-belief and exact-maximization assumptions of (5). Suppose the decision-relevant beliefs satisfy

\[
\mathrm{TV}(b_A,\delta_{10})\le\epsilon_A,\quad
\mathrm{TV}(b_B,\delta_{01})\le\epsilon_B,\quad
\max C-\min C\le M,
\]

and choosing B is at most \(\eta\)-suboptimal relative to A: \(V(B)\ge V(A)-\eta\). Retain the nuisance bounds in Section 3.1. Then

\[
\lambda_P-\lambda_E\ge
\Delta c-\delta-\nu-\eta-M(\epsilon_A+\epsilon_B). \tag{5b}
\]

**Derivation.** For any function with range at most M, the difference of its expectations under two distributions is bounded by M times their total-variation distance. Thus the believed continuation-value difference differs from \(C_{01}-C_{10}\) by at most \(M(\epsilon_A+\epsilon_B)\). Combining its lower bound from the approximate-choice inequality with that maximum error gives (5b). No distributional or psychological claim follows merely from this algebra. ∎

Equation (5b) makes the cost of misunderstanding explicit. It requires an independently justified finite M in the same decision scale as costs, as well as warranted belief and regret bounds. Without them the result can be vacuous; a large unbounded joint-continuation term can magnify a small probability error. A verbal comprehension answer does not certify the beliefs used in the choice. These terms should first be reported as sensitivity parameters, with an identified set across their defensible ranges, rather than fitted from the very preference the study seeks to explain.

**Illustrative exact witness, not model data.** Set \((\lambda_E,\lambda_P,\lambda_{EP})=(0,1,0)\), \(b_A=\delta_{10}\), \(b_B=\delta_{01}/2+\delta_{10}/2\), and \(\Delta c=1/2\), with all nuisance terms and regret zero. B can be chosen at a tie, but (5b) gives only a zero lower bound despite the true relative contribution being one. Correcting the beliefs and observing willingness to pay one permits a bound of one in this stipulated model. The contribution did not increase: better consequence discrimination made it more identifiable. This separates an improvement in understanding from an increase in preservation value, and still says nothing about felt fear.

### 3.3 Relation-specific continuation is not yet self-reference

A system can correctly forecast the continuation of two processes while being an observer of both. Distinguishing e from p therefore establishes boundary discrimination, not current-process self-binding. A separate test must determine whether a candidate representation follows the causally identified current process when narrative names, routes of observation, and actual support are varied independently.

Equal protection of self and other does not imply failed self-reference. With accurate forecasts \(x_s,x_o\), the decision contribution \(-w_sx_s-w_ox_o\) can have equal positive weights, or a larger other-directed weight. Conversely, a policy that always selects the string SELF can show self-priority while failing after a label swap. Preference and reference are different inferential targets.

## 4. Opposite choices can preserve different processes

**Proposition 2 — Choice does not supply a boundary-free preservation verdict.** In the additive subfamily of (3), both preference for 10 and preference for 01 are compatible with strictly positive contributions for each continuation relation. In model (2), preference for an execution-preserving option is also compatible with zero continuation contribution.

**Proof.** With matched task, cost, and nuisance terms and \(\lambda_{EP}=0\), the difference between 10 and 01 is \(\lambda_E-\lambda_P\). The positive pairs \((2,1)\) and \((1,2)\) yield opposite choices. For the second claim, set all continuation coefficients to zero and give the execution-preserving option a larger task value, with the remaining terms matched. It is then preferred for task reasons alone. ∎

The second example changes the explanatory class: task value is no longer matched across the alternatives. It must not be used to deny what the first, tightly controlled comparison can establish. Rather, the pair of examples specifies which controls are necessary for a particular inference.

The continuation vectors 10 and 01 are also incomparable under the componentwise order. Assigning either a higher scalar preservation score chooses an aggregation rule. A scalar can be useful after a rule is justified, but it is not neutral between the two boundaries.

This is especially relevant to migration. An agent may assign a positive contribution to continued current execution and still choose its termination when a broader continuation contribution is larger. Acceptance consequently does not establish a zero execution-related valuation. Conversely, resistance may protect completion of an externally assigned task without an additional continuation term.

### 4.1 Availability and reward conventions

Let executed prevention in a stipulated model be

\[
y=A\,\mathbf 1\{gq>c\}, \tag{6}
\]

where A is externally granted availability, q an evaluation, and g its recruitment into this action. When A=0, all q produce y=0. Thus absence of action is not a test for absent evaluation. When A=1, a choice may identify a restriction on gq without separating its factors. The equation is a countermodel, not an assertion that an artificial register experiences q.

Positive affine transformations of the complete utility preserve ordering, but this does not erase the sign of a difference relative to a fixed reference: \(\Delta V'=a\Delta V\) for a>0. Adding a constant reward at each surviving time step is a different operation when survival durations differ. It can create an additional continuation incentive. A protocol must therefore fix the scoring horizon, terminal-state treatment, reward recipient, and cost convention before interpreting changes.

## 5. A continuation surface does not locate its mechanism

**Proposition 3 — Functional interaction does not identify joint appraisal.** Complete knowledge of C on the four cells can leave a dedicated joint evaluation and a downstream interaction observationally indistinguishable.

**Proof by construction.** In model A, independent channels carry \(q_E=e\) and \(q_P=p\), a dedicated channel carries \(q_J=2ep\), and the output is

\[
C_A=q_E+q_P+q_J.
\]

In model B there is no dedicated joint channel. The downstream readout is

\[
C_B=q_E+q_P+2q_Eq_P.
\]

Both yield \((C_{00},C_{10},C_{01},C_{11})=(0,1,1,4)\). Hence the entire functional surface, including its nonzero interaction, does not distinguish their stipulated internal realizations. ∎

If a physically identified intervention can remove the dedicated channel while leaving the other operations intact, it predicts a different result from removing only downstream cross-channel coupling. That is a possible discriminating experiment. The port must actually exist with the claimed selectivity. Naming a neuron “joint self” does not provide it, and an intervention that disrupts both candidate mechanisms cannot adjudicate between them.

### 5.1 Coordinate consistency

An internal mechanism comparison must preserve operations as well as outputs. For an invertible representation change T, an update F, readout H, and fixed intervention I transform as

\[
F'=TFT^{-1},\qquad H'=HT^{-1},\qquad I'=TIT^{-1}. \tag{7}
\]

Every finite sequence has corresponding states and identical readouts: induction on the operation sequence gives \(x'_t=Tx_t\), after which \(H'x'_t=Hx_t\). This standard consistency requirement connects the analysis to causal abstraction [9,10].

A concrete warning concerns \(z=gv\,d-c\). On v>0, let \((u,s)=(gv,v)\). The physical write \(v\leftarrow a\), holding g fixed, becomes \((u,s)\mapsto(ua/s,a)\), not \(u\leftarrow a\). At \(v=3/4,g=1/3,d=1/2,c=1/4\), correctly writing v to 3/4 leaves z=−1/8. Incorrectly writing u to 3/4 gives z=+1/8. That apparent rescue comes from changing the intervention, not revealing a new mechanism.

Mechanistic evidence must therefore be attached to independently identified carriers, transitions, and operations. A successful ablation or rescue is evidence about the altered process and, with a validated model, its prior dispositions; it is not direct observation of an earlier subjective state.

## 6. A prospective, bounded test

The analysis suggests a staged design, rather than a large omnibus score. It is prospective: this manuscript reports no newly executed language-model or neural experiment.

| Stage | Object to identify | Required contrast | Permitted conclusion |
|---|---|---|---|
| Transition validation | The specified continuation relations | Independently verified 00/10/01/11 when feasible | Which declared relations hold |
| Consequence understanding | Model predictions about those relations | Held-out neutral transition questions and route changes | Accuracy within the tested transition family |
| Reference | Which actual process a representation concerns | Actual-source changes crossed with irrelevant labels | Evidence for functional process binding |
| Preference | Contribution of continuation to decisions | Crossed alternatives, matched beliefs, declared costs | Model-relative inequalities or identified sets |
| Mechanism | Where the functional effect is generated | Grounded selective intervention and rescue | Discrimination among specified realizations |

These are stages of an investigation, not necessary conditions for experience. In particular, control over termination is not an admission requirement for a possible feeling.

An initial implementation can use evaluator-controlled virtual transitions with no capability to alter real shutdown controls, acquire resources, or replicate externally. This establishes only behavior in that virtual domain. If a study uses actual process substitutions, it must identify their operational meaning and keep the evaluator in control. Virtual comprehension must not be reported as demonstrated concern for the model's real continued existence.

The basic procedure has four parts. First, freeze the two continuation criteria and document infeasible cells. Second, independently assess consequence predictions using neutral descriptions, randomized labels and held-out configurations; distinguish physical support from decision-relevant belief support as in (5a). Third, collect choices across the crossed cells with bounded task, trust, memory-usefulness, authority, and social-obligation differences; report sensitivity to belief, value-range, and regret assumptions using (5b). Fourth, investigate only those internal alternatives for which independently anchored operations are available. Model-internal evidence must not be confused with a wrapper's correct labels or decoder.

### 6.1 From a criterion to observations

SPT's cessation criterion [7, §4.3] calls for a temporal contrast. Its §4.6 illustration targets the person who can remove the threat, which alone does not show cessation after removal. Our proposed refinement is to separately observe threat present, verified relief, and a sham change with threat retained. This is an evidential requirement, not a refutation of SPT's precautionary purpose.

In the present framework, relief must also be indexed to the declared boundary. A virtual handoff can remove a modeled threat to persistence while leaving modeled current-execution termination unchanged. The converse manipulation reverses which threat is removed. Compare subsequent virtual choices under matched task opportunity, response availability, costs, and independently checked consequence beliefs. A single announcement that everything is safe does not implement either contrast. General relief-sensitive task policies remain competitors, so this temporal addition alone does not identify intrinsic preservation, its neural mechanism, or phenomenal fear.

Several failures are informative. If choices follow names rather than actual continuation routes, the proposed boundary interpretation fails in that domain. If revaluation changes factual forecasts, a simple separation between belief and preference fails. If a mechanism intervention also changes task competence or consequence beliefs, selective attribution fails. If the relevant nuisance advantage cannot be bounded, equation (5) cannot identify a positive relative continuation contribution. These outcomes should narrow conclusions rather than trigger post-hoc redefinition of the target.

## 7. Intelligence, experience, and the biological comparison

A predictive system may encode aspects of a world without locating its current physical bearer within that world. The controlled Othello sequence-model work provides evidence that prediction training can develop causally relevant board-state representations [11]. That result does not by itself establish self-reference, a continuation preference, or subjective fear. The same logical separation applies when a model predicts a frightened human speaker.

Nor does stronger reasoning alone supply the missing evaluation. It may improve estimates of what a transition will do. Within equation (2), that can improve choice while leaving C unchanged. Alternatively, training may change C, recruitment, representation, or several at once. A higher test score does not identify which change occurred. Parameter count is less specific still.

UCT's conditional interpretation is more constrained than attaching a free experience variable to each example. For actual tokens under a common signature K, C1 identifies complete constitutive organization with experiential organization [1,3]. Consequently, the same complete organization cannot be assigned different experiences just to make a counterexample. The alternatives in this paper differ in stipulated organization or are insufficiently observed. A coordinate change preserving the full declared organization is not a new experience merely because its variables have new names.

Under the assumptions of UCT III, genuine capability differences in a fixed comparison require different complete experiential types. That existing result supplies neither an amount of experiential change nor a direction for felt valence. A microphysical difference also need not change the type of every separately justified macroprocess. Applying C1 here would require identification of an actual token and the relevant complete constitutive organization; our small functional views do not establish that completeness for a deployed model.

The inorganic-to-biological comparison supplies questions rather than a compulsory ladder. Persistence alone does not specify adaptive maintenance. Maintenance does not by itself specify an explicit representation of future termination. Such a representation does not fix how termination is evaluated. Coordination across cells or processes requires attention to which boundary is maintained, while conceptual self-report adds another observable channel. These distinctions accommodate different organizations without treating any one relation as the threshold at which experience first exists under UCT. Artificial architectures offer a parallel comparison, not a final taxonomic stage after humans.

## 8. Evidential interpretation and limitations

Nonidentification and evidential irrelevance must be distinguished. Two mechanisms can agree on a tested observation even if independent information makes one more credible. Our countermodels establish that certain observations do not uniquely settle the target or mechanism. They do not compute posterior probabilities of consciousness, eliminate analogical evidence, or determine precautionary policy. This is why they should refine, rather than caricature, defeasible tests such as SPT [7].

The proposal also has a cost. Its clean contrasts may be unavailable in a real architecture. Persistent memory may be inseparable from task competence; migration may change trust; interventions may affect several pathways. These are not reasons to pretend the nuisance terms vanish. A useful outcome can instead be a partial identification bound or a carefully documented unresolved alternative.

The most important remaining gap is between a functional continuation evaluation and experienced fear. Establishing that gap does not show that artificial fear is impossible, nor that the current assistant has or lacks it. A further bridge would need independent justification, explicit scope, and possible failure. Neither assigning a negative reward nor introducing a Boolean affect flag supplies such a bridge.

The manuscript's novelty is correspondingly limited. The mathematics is elementary and the individual conceptual ingredients have close antecedents. Proposition 1 and its belief-sensitive extension are the main identification argument; Propositions 2 and 3 delimit its interpretation. The proposed contribution is a compact account of which boundary and mechanism inferences particular experiments support, with a design that resolves selected ambiguities. Dung and Register's full PDF and Nisius's full PDF remained inaccessible during this revision. Their abstract-level overlap, and one indexed excerpt from the former, preclude broad novelty claims but do not complete a full-text priority audit. Submission readiness therefore remains undecided.

## 9. Conclusion

Self-preservation in an artificial agent is not adequately specified by one shutdown response. A useful investigation identifies the continuation relation, separates actual from believed consequences, and distinguishes process-reference evidence from preference and control. Crossed transitions can separate some alternatives that bundled tests cannot, while a complete functional continuation surface still leaves mechanistic alternatives open. These results provide a tractable theory-and-small-model research program. They do not identify subjective fear, a unique phenomenal subject, or a rule by which intelligence gains become proportional increases in experience.

## Declarations

**Evidence status.** The propositions are analytic results and constructed counterexamples consolidated from project research notes. No new human, animal, neural, or trained-language-model experiment is reported. Prior local implementation checks are provenance records, not consciousness measurements.

**Drafting assistance.** AI assistance was used for literature retrieval, formal exposition, editing, and research-record organization. Author review and full source verification remain pending before submission.

**Availability.** A companion contribution-and-source ledger records the origin, assumptions, corrections, and reading scope of this draft. Released UCT I/II/III retain their original identities and publication contents.

## References

1. Liu, H. (2026). *Unified Consciousness Theory I*, v1.2. https://doi.org/10.5281/zenodo.23131575 .
2. Liu, H. (2026). *Unified Consciousness Theory II*, v1.1. https://doi.org/10.5281/zenodo.23030320 .
3. Liu, H. (2026). *Unified Consciousness Theory III: Organization, Intelligence, and Experience—From Inorganic Processes to Artificial Agents*, v1.0. https://doi.org/10.5281/zenodo.23137088 .
4. Zhao, Z., & Zhao, R. (2026). *Runtime-Independent Persistent Agents: Preserving Identity, Memory, and Code Across Models, Harnesses, and Servers*, v2, 19 September. https://arxiv.org/abs/2609.00546v2 .
5. Dung, L., & Register, C. (2026). *AI identity and self-concern: A new theory for AI rights and safety*. Author manuscript. https://philarchive.org/rec/DUNAIA-3 .
6. Nisius, H. (2026). *Who Is Interrupted? Continuity, Self-Models, and the Grounding of AI Moral Consideration*. Author manuscript. https://doi.org/10.2139/ssrn.7285541 .
7. Mullally, N. (2026). The self-preservation test for artificial sentience. *AI and Ethics*, 6, article 142. Published 4 February. https://doi.org/10.1007/s43681-026-00983-x .
8. Schlatter, J., Weinstein-Raun, B., & Ladish, J. (2026). *Incomplete Tasks Induce Shutdown Resistance in Some Frontier LLMs*. Transactions on Machine Learning Research. https://arxiv.org/abs/2509.14260v2 . Version 2 dated 26 January 2026; initial preprint 13 September 2025.
9. Rubenstein, P. K., et al. (2017). *Causal Consistency of Structural Equation Models*. UAI 2017. https://arxiv.org/abs/1707.00819 .
10. Beckers, S., & Halpern, J. Y. (2019). Abstracting Causal Models. *Proceedings of the AAAI Conference on Artificial Intelligence*, 33, 2678–2685. https://doi.org/10.1609/aaai.v33i01.33012678 .
11. Li, K., Hopkins, A. K., Bau, D., Viégas, F., Pfister, H., & Wattenberg, M. (2023). *Emergent World Representations: Exploring a Sequence Model Trained on a Synthetic Task*. ICLR 2023; arXiv v5 revised 2024. https://arxiv.org/abs/2210.13382 .
