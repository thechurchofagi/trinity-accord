# R76 — A matched comparator for need-directed sensing

Research note v1.0 · 2026-10-05 · UCT agent-consciousness project

**Status:** a source-motivated formal mechanism comparison, with exact small-model checks. Not a replication of the cited agent, a real-model experiment, or a measurement of fear. This note supplements the current unpublished research; it does not revise published UCT I, II, or III.

## 1. The question this round resolves

An agent can prioritize a threatened resource because it estimates that resource more reliably, because it assigns a larger decision weight to its condition, or through both routes. Can these routes be separated without relying on statements such as “I fear termination”?

For a specified symmetric observation channel and a pragmatic-only planner, we construct an exact preference comparator. At frozen predictive beliefs, it matches every candidate policy's relative score and selection probability. The match fails at the next common-observation Bayesian update. This supplies a concrete intervention contrast; it does not identify which mechanism feels like anything.

This is narrower than the unresolved organization–feeling bridge. Its positive contribution is to locate a causal difference hidden by matched immediate choices. It is not a new general theorem about consciousness or a demonstration that self-preservation implies fear.

## 2. The actual source and the open comparator

Grimbly's author companion, dated 5 August 2026, describes *Interoceptive Attention as Dynamic Homeostatic Prioritization in a Foraging Agent* [S1]. Four six-level channels share a fixed reliability budget: the uniform setting is 0.65, while the selected channel receives 0.90 and the others approximately 0.567. The symmetric likelihood places the remaining probability equally off-diagonal. Selection depends on inferred need. Reliability changes both observation sampling and the agent's likelihood. The companion describes pragmatic planning with state information gain disabled and explicitly identifies a matched preference-reweighting comparison as unfinished work.

The full companion was read. Repository retrieval failed; a supplement's GitHub wrapper was accessible but its PDF contents were not read. Consequently, the equation below is an explicitly specified abstraction motivated by S1, **not a verified transcription of its entire implementation**. Undocumented policy terms or update details could change its applicability. S1 already acknowledges the missing comparison: neither that omission nor the general suggestion to compare it is our discovery.

## 3. Local equivalence proposition

Let there be m ≥ 2 hidden states and m observations. Use a column-stochastic symmetric likelihood

\[
A_\kappa(o,s)=\begin{cases}\kappa,&o=s,\\(1-\kappa)/(m-1),&o\ne s.\end{cases}
\]

Writing U = 11ᵀ/m and λκ = (mκ−1)/(m−1), we have Aκ = λκ I + (1−λκ)U. Let C be a strictly positive normalized preference distribution, and qπ a normalized predicted state distribution for candidate policy π. Define the one-step pragmatic cost

\[
G_{\kappa,C}(\pi)=-(A_\kappa q_\pi)^\top\log C.
\]

Assume:

1. The compared planners use exactly the same qπ for every candidate policy. This clamps current inference and policy-conditioned state prediction.
2. They have the same candidate policies, policy priors, additive costs, and policy softmax inverse temperature γ.
3. κ and the corresponding comparator are fixed across candidate policies at this decision. They may have been selected from current need before comparison.
4. There is no additional κ-dependent policy term, including information gain, parameter learning value, or policy-dependent past-evidence term.
5. The baseline κ₀ is greater than 1/m. For the usual informative-channel interpretation, take the target κ in [1/m,1].

Set

\[
r=\lambda_\kappa/\lambda_{\kappa_0},\qquad
C'_i=\frac{C_i^r}{\sum_j C_j^r}.
\]

**Proposition.** For every normalized qπ, Gκ₀,C′(π) = Gκ,C(π) − d, where d is independent of π. Thus all pairwise cost differences, minimizers, and same-γ softmax policy probabilities agree.

**Proof.** Let v = log C, v̄ = m⁻¹Σvᵢ, and Z = ΣCᵢʳ. Since log C′ = rv − log Z·1,

\[
A_{\kappa_0}^{\top}\log C'
=\lambda_\kappa v+[r(1-\lambda_{\kappa_0})\bar v-\log Z]\mathbf1
=A_\kappa^{\top}\log C+d\mathbf1,
\]

where d = (r−1)v̄ − log Z. Multiplying by qπᵀ uses qπᵀ1=1; negating gives the claim. A common additive score shift cancels on softmax normalization. □

For m=6 and κ₀=0.65, λκ₀=29/50. The comparator powers are 44/29 for κ=0.90 and 24/29 for κ=17/30. These are exact fractions, not fitted coefficients. If separate channel costs add and each channel meets the assumptions, summing their policy-independent constants preserves the result. This extension requires no independence of state factors for the marginal expectation itself, but does require the stipulated additive score.

The comparator sharpens or flattens preferences only at the planner interface. “Attention equals preference” would be an incorrect generalization.

## 4. A discriminating update with identical input

Use a uniform state prior and replay the same observation o to both internal inference routines. For the simple Bayesian update

\[
q^+(s)\propto A_\kappa(o,s)q(s),
\]

the posterior is κ at s=o and (1−κ)/(m−1) elsewhere. Preferences do not enter this particular update. Therefore the high-reliability route gives [0.90,0.02,0.02,0.02,0.02,0.02], while the preference-only comparator gives [0.65,0.07,0.07,0.07,0.07,0.07], up to permutation of coordinates. Their total-variation distance is 0.25.

More generally, in this uniform-prior case the posterior total-variation difference is |κ−κ₀|, independent of m. This measures a difference in represented belief, **not a difference in experiential intensity or complexity**.

A small implementation check should therefore have two stages:

| Stage | Held fixed | Manipulated | Predicted result under the stated model |
|---|---|---|---|
| Matched planning | qπ, policy set, costs, γ | κ,C versus κ₀,C′ | Equal policy probability vectors |
| Common-observation update | Prior, observation, transition model | Internal likelihood versus planner-only preferences | Different posterior vectors |

The second stage deliberately replays a common observation. Letting each external sensor independently draw its next observation would mix sampling effects with internal inference effects. A later implementation audit must separate external sensor reliability from the likelihood used internally. Preference feedback into state inference must also be disabled or explicitly modeled; otherwise this update prediction does not follow.

## 5. Counterexamples and boundaries checked

**Uninformative baseline.** At κ₀=1/m, Aκ₀=U. Every outcome-preference vector gives the same expected utility for every state distribution. No preference-only change through that channel can reproduce a nonconstant target state score. The power formula's zero denominator reflects this substantive information loss.

**Epistemic policy value.** With uniform preferences, the pragmatic term ties policies. Compare a policy predicting one certain state with a policy predicting a uniform state. Adding mutual-information value makes their policy probability contrast depend on κ. At γ=1 the checked probability of the latter policy is approximately 0.786798 at κ=.90 versus 0.641300 at κ=.65. The proposed power comparator does not repair this difference. This counterexample excludes full-EFE equivalence, not every imaginable alternative controller.

**Closed-loop inference.** Once the matched planners obtain different posteriors, qπ need not remain equal. Immediate policy equivalence does not imply trajectory, survival, learning, or whole-agent equivalence.

**Horizons and schedules.** Equal fixed-horizon sums preserve the constant cancellation only when κ schedules and comparator normalization constants are policy-independent and predictive beliefs remain matched. Variable termination times can make the accumulated constant policy-dependent. R67's termination-accounting caution therefore still applies.

**Other likelihoods.** Learned or asymmetric channels need not admit this power transform. A more general comparator requires solving A₀ᵀlog C′ = Aκᵀlog C + d1; singular A₀ can obstruct solvability. This note does not claim to solve the general case.

**Self versus other.** The same matrix calculation works for an external object's resource or another agent's state. Algebraic sensitivity to “need” does not establish ownership. Actual self-maintenance additionally requires a verified causal route from the regulated variable to the specified process token's continued functioning; external support can implement part of that route. Own-termination representation and felt fear remain separate claims. These are applicability requirements, not new results of the computation.

## 6. Relation to UCT and the user's scaling question

Published UCT III §2 was checked for the actual-token, common-signature, and complete-organization constraints. Its C1 commitments are inherited assumptions here, not independently demonstrated facts. R67 was reread for the limits of polarity flags, reward accounting, and affect labels. This round did not re-audit the entirety of UCT I and II.

For a conditional C1 comparison, first identify the actual running process tokens p and p′ and a common structural signature K. K would need to represent the relevant observation-to-belief transition, preference-to-policy dependency, and any claimed maintenance/termination relations; listing these coordinates alone does not prove K is complete. An experimentally verified difference in the update relation is a difference on that specified relation. It does not automatically establish a difference in every coarser process type, a new unified subject, or a numerical increase in experience. The locally matched policy distributions are likewise insufficient to equate complete organization.

Consequently, this model provides a tractable example of how one organizational change can affect confidence and potentially future competence without adding parameters or making a whole agent bigger. Conversely, adding unused parameters supplies no corresponding update difference. It does not supply a scale converting parameter count, benchmark gain, or posterior total variation into experience.

The inorganic-to-biological-to-artificial comparison should therefore ask which actual processes implement resource-dependent sensing, memory, selection, and maintenance at a stated boundary. A stone aggregation, a cell, and a controller cannot be placed on a single experiential scale just by counting components. Nor does this likelihood model establish that cells instantiate its specific architecture. The result concerns a realized causal organization where its assumptions hold, irrespective of the material label.

An utterance readout such as “I am afraid” is not present in the proof and is unnecessary for the contrast. Adding an identical text readout to the matched decision stage would not recover the hidden inference distinction. It also would not settle whether either token feels fear. The missing positive bridge must connect independently justified experiential structure to a specified organization; simply naming κ “affective attention” cannot perform that work.

## 7. Originality audit and rejected route

Joffily and Coricelli (2013) propose a free-energy-change account of valence and discuss hierarchically contextualized examples, including anticipated danger [S2]. The initial idea that better prediction of bad news by itself refutes their proposal was therefore rejected as an oversimplification, not reported as a new counterexample to their full theory.

Friston et al. (2017), especially equations 2.5–2.6, already relate log outcome preferences to utility and separate pragmatic and epistemic terms [S3]. Additive-constant utility invariance and Bayesian updating are standard. A 2026 formal-equivalence paper was located but not fully read [S4], leaving an additional priority check unfinished.

The defensible contribution here is the explicit power-law matched comparator and paired-update contrast for the specified symmetric channel, applied to a concrete open comparison in S1. It is new work within this research record, but worldwide novelty is not established. It should currently be presented as a methodological derivation or appendix candidate, not a major consciousness breakthrough or a standalone publication-ready result.

## 8. Verification, conclusion, and next action

`r76_precision_preference_checks.py` uses exact fractions for 40 score identities (five reliability values times eight belief distributions), and floating-point checks after preference normalization. Maximum policy-probability discrepancy is 1.11×10⁻¹⁶. It also checks the 1/4 posterior distance and the uninformative-baseline and epistemic counterexamples. These are formal checks of our equations, not observations from a trained language model, organism, or the cited agent.

**Conclusion:** we can now distinguish two candidate organizational routes underlying the same immediate self-preservation-like choice using a precise, small intervention. We have not obtained a bridge from either route to felt fear, or a law that intelligence/parameter growth proportionally increases experience.

**Next:** retrieve and inspect the source's actual scoring and inference functions, including dependency versions and any extra policy terms. If the abstraction matches, implement the exact comparator and common-observation check in a minimal evaluator-controlled harness; do not train a large agent or run a new shutdown experiment. If it does not match, record the mismatch and solve the actual score-matching condition before interpreting differences. A separate own-versus-other maintenance intervention is warranted only after the mechanism is verified. Do not repeat the same fraction grid as new empirical evidence.

## References and reading scope

- **S1.** Grimbly, S. (2026-08-05). *Where Should an Agent Direct Its Interoceptive Attention?* Author companion to the SAB 2026 paper. https://stjohngrimbly.com/interoceptive-attention/ — full companion; no full paper/supplement or source-code replication.
- **S2.** Joffily, M., & Coricelli, G. (2013-06-13). *Emotional Valence and the Free-Energy Principle*. PLoS Computational Biology 9, e1003094. https://doi.org/10.1371/journal.pcbi.1003094 — author-hosted PDF, definitions and selected discussion/hierarchy passages; simulations not replicated. PDF: https://r.unitn.it/filesresearch/images/cimec-ldmg/download/publications/jofflincoricelli_2013.pdf
- **S3.** Friston, K., FitzGerald, T., Rigoli, F., Schwartenbeck, P., & Pezzulo, G. (2017). *Active Inference: A Process Theory*. Neural Computation 29, 1–49. https://doi.org/10.1162/NECO_a_00912 — targeted definitions and equations 2.5–2.6 plus neighboring inference text, not all 56 PDF pages. https://activeinference.github.io/papers/process_theory.pdf
- **S4.** *Decision, Inference, and Information: Formal Equivalences Under Active Inference* (2026). Entropy 28(1), 1. https://doi.org/10.3390/e28010001 — indexed metadata/abstract only; full page rate-limited. No claim of completed priority audit against this paper.

