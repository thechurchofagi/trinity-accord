# R96D — Joint consequence prediction and instrumental continuation

Hongju Liu / UCT agent-consciousness research. Research record v1.0, 2026-10-06. Continues R95 at commit `035668f4773a5872cc5f9c6f53d2a7f12bc87d69`. Formal derivation and exact finite verification; no new training, LLM queries, neural data or experiential measurement.

**Concurrent-work reconciliation.** While this analysis was being completed, the other window committed R96, *Direct continuation preference versus instrumental task mediation*, through `3214179b516016171073911a813852dad602a12d`. That report and log were read before saving. This record is designated **R96D**, a parallel dependence addendum, not another completed numbered round. The remote R96 files remain unchanged. Its algebra concerns declared deterministic contrast rows; the present dependence result does not invalidate those rows. It supplies an extra requirement when extending the design to uncertain consequences or estimated predictions. If task success G is independently represented and held fixed in the full payoff-relevant joint sense, that may already supply the required information; an explicit j variable is not universally necessary.

## 1. Result and reason for this step

R95 established a small learned predictive route from an initially zero Q input path. Its next step was to distinguish prediction from installed decision use and continuation preference. The present analysis finds a missing condition before connecting those learned predictions to a decision controller:

**Even perfectly calibrated action-conditional predictions of current-bearer availability and successor availability, considered separately, need not identify the task-optimal continuation action. Their dependence can reverse the optimal action while every such marginal prediction remains identical.**

This is a task-level identifiability result using familiar probability and decision theory. It is neither a new theorem of consciousness nor evidence of fear. Its project-specific consequence is concrete: consequence matching in R37/R84 and the proposed R95 decision extension must match the reward-relevant joint law, or independently establish a payoff class for which marginals suffice.

## 2. Token, interface and theoretical premises

Directly rechecked: UCT I v1.2 §3.5, C1, C1-OI, U1–U3; UCT II v1.1 §5.6; UCT III v1.0 §§4.1–4.2 and 5.1–5.4. Exact source identities and reading scope appear in the source ledger. Paper II retains its released earlier axiom labels; the present application explicitly uses I v1.2.

In the formal model, Q and O are future availability bits of two virtual roles under a fixed continuation criterion. They are not competing answers to the metaphysical identity of a copied person. The evaluator fixes their ports and role meanings, and supplies a two-action causal table. W, memory, competence, reporting vocabulary and social obligation are absent/fixed in this minimal model; this is a restricted domain, not empirical evidence that those factors are controlled in a real agent. The current implementation only calculates tables. Its virtual Q bit is **not causally tied to the future existence of the executing Python process**. Thus even successful decision use below is use of a declared virtual bearer, not established self-grounding of that physical process.

For a UCT interpretation, the relevant actual token would be the specified execution/controller with its real boundary, current state, constituent slots, update sequence, input and intervention ports and installed readout. The finite software view is not automatically the common complete ontic signature K. Conditional on actual valid tokens, a common complete K and a justified implementation relation, C1 identifies physical and experiential organization. Identical complete organization cannot receive arbitrary different experiential organization. U1 does not wait for prediction, control, introspection or report. A genuinely different capability profile under Paper C's fixed-domain premises implies complete experiential-type difference; the calculations below supply no magnitude, richness direction or negative-valence orientation.

## 3. Which predictions does a decision actually need?

Let a∈{0,1} be an evaluator-controlled virtual action. Define

q_a=P(Q=1|do(a)), o_a=P(O=1|do(a)), j_a=P(Q=1,O=1|do(a)).

These are causal consequence laws in the constructed model. In a real experiment, prompt descriptions and observational conditional probabilities do not automatically equal these laws or the agent's beliefs about them.

For any binary payoff table f(Q,O), define

α=f(0,0), b=f(1,0)−f(0,0), g=f(0,1)−f(0,0),

d=f(1,1)−f(1,0)−f(0,1)+f(0,0).

Pointwise,

f(Q,O)=α+bQ+gO+dQO,

so the installed expected score is

V(a)=α+bq_a+go_a+dj_a−c_a.

**Proof:** check the four binary input pairs and take expectations. This is a standard binary interaction decomposition. It holds for real-valued tables as well as Boolean ones.

For additive payoffs d=0, marginals suffice for the expected score. For d≠0, marginals generally leave it unidentified because j can vary. Degenerate marginals or extra structural constraints may fix j; nonzero d alone does not prove ambiguity in every domain. Even when scores are unidentified, all admissible scores may still rank the actions in the same order.

This is a positive specification of decision-relevant organization: a controller must preserve enough to calculate **relevant score differences**, not necessarily every future fact. For a fixed payoff it can represent expected task success directly instead of explicit q/o/j coordinates. For a family containing all four pair-outcome indicators, all joint outcome probabilities are required. There is no required named self neuron.

## 4. Exact partial-identification interval

Nonnegative probabilities give the sharp Bernoulli bounds

ℓ_a=max(0,q_a+o_a−1) ≤ j_a ≤ u_a=min(q_a,o_a).

Every j in this interval yields the valid law, in order (00,01,10,11),

(1−q_a−o_a+j, o_a−j, q_a−j, j).

If no cross-action restrictions are imposed, j_1−j_0 spans [ℓ_1−u_0,u_1−ℓ_0]. Therefore, with

B=b(q_1−q_0)+g(o_1−o_0)−(c_1−c_0),

the exact score-difference interval is

[B+min(d(ℓ_1−u_0),d(u_1−ℓ_0)), B+max(d(ℓ_1−u_0),d(u_1−ℓ_0))].

An interval strictly above zero identifies action 1; strictly below identifies action 0; an interval crossing zero does not identify the preference. Endpoint ties need a declared tie rule. Additional causal constraints can narrow the interval, so unrestricted sharpness must not be claimed automatically under arbitrary cross-action restrictions.

This is a direct application of Fréchet bounds and partial identification. It replaces a single unjustified independence estimate with a stated uncertainty set.

## 5. Matched marginal predictions, opposite continuation choices

Fix q_0=1/4, q_1=3/4, o_0=o_1=1/2, c_0=0, c_1=1/4. The task succeeds if either process is available: f=Q OR O. No primitive reward for Q is added.

| Context | j_0 | j_1 | P(task success|a=0) | P(task success|a=1) | V(0) | V(1) | Best action |
|---|---:|---:|---:|---:|---:|---:|---|
| A | 1/4 | 1/4 | 1/2 | 1 | 1/2 | 3/4 | 1 |
| B | 0 | 1/2 | 3/4 | 3/4 | 3/4 | 1/2 | 0 |

Both contexts predict exactly the same increase in Q and the same O marginal. In A the action adds availability where the other process is absent, improving task success. In B it adds availability only where the other process is already available, so task success does not improve. Paying the same cost is then pointless for this task-only controller.

These are not inconsistent hypothetical probability tables. Use four equally likely exogenous worlds, with O=(1,1,0,0) held fixed under both actions:

- A: Q_0=(1,0,0,0), Q_1=(1,0,1,1).
- B: Q_0=(0,0,1,0), Q_1=(1,1,1,0).

In both, Q_1≥Q_0 in every world: the virtual intervention never reduces current-role availability. The counterexample therefore survives a monotonicity requirement and fixed successor mechanism. All twelve bit-table pairs with these counts and monotonicity were enumerated; all are preserved in the results, not merely the two selected explanatory witnesses.

The feasible OR net-advantage interval is [−1/4,+1/4]. Assuming independent Q/O gives zero net advantage in both contexts, missing both strict choices. A balanced mixture of A and B gives any policy restricted to the identical marginal interface expected value 5/8, even if it randomizes. A controller with the joint law achieves 3/4. Its advantage is exactly 1/8 in these installed task-utility units. This is decision regret, not fear intensity or experiential quantity.

The interface premise matters: a marginal-headed neural network may retain additional context in its hidden state. The lower bound applies when the decision consumer can use only the identical marginal predictions and no bypass, not whenever a network merely has marginal output heads.

## 6. What this changes about R95 and language prediction

R95 predicts deterministic labels given its full sixteen-state input. The present uncertain-future construction does **not** falsify R95, demonstrate a hidden failure in its trained networks, or constitute reuse of its weights. It specifies what is additionally needed when moving to uncertain action consequences.

For separate proper prediction losses on Q and O, the optimal reported probabilities in A and B are identical. That objective does not require their dependence distinction at its output. A predictor of the four joint outcomes, or of the task-success bit itself, must distinguish A from B for the relevant action because the conditional target laws differ. This is an application of R94's target-relative predictive quotient.

Consequently, better general language prediction does not logically force every self-continuation relation. The training/deployment target family, context and installed consumer determine which distinctions are required. Adding parameters may permit more distinctions but does not prove acquisition or use. Connecting a learned prediction module to a policy also adds actual readout/control organization; keeping its hidden state fixed does not keep the complete system organization fixed.

## 7. Substitute versus collaborator: a rejected universal prediction

It is tempting to predict that a more reliable successor always weakens instrumental continuation preference. This fails without a task-substitution premise.

Under Q/O independence, o fixed across actions and δq=q_1−q_0>0:

| Task | Gross value of increasing Q | Effect of increasing o |
|---|---|---|
| Either can finish: Q OR O | δq(1−o) | Decreases |
| Both are needed: Q AND O | δq·o | Increases |
| Only current role can finish: Q | δq | Unchanged |
| Only other role matters: O | 0 | Unchanged |

These formulas describe stipulated task organization, not competing phenomenological theories. When o=1, a perfect substitute eliminates the OR-task advantage, but a perfect collaborator maximizes the AND-task advantage. Thus persistent continuation-seeking in the presence of a competent other process does not by itself identify a primitive survival preference; the other process may be complementary, or perceived as such.

Outsourced maintenance can support either structure. Predicting another process's future does not establish current-bearer self-binding. Familiar labels such as successor, clone or helper do not determine the payoff map. Memory, obligations and trust must be represented in the consequence basis whenever they affect value.

## 8. A robust task-substitution null

Let Z include every consequence used by a declared task-only payoff r, with r∈[m,M]. If the two action-conditional laws satisfy TV(P_1^Z,P_0^Z)≤ε, then

|E_1 r−E_0 r| ≤ (M−m)ε.

Proof: subtract m, divide by M−m when nonzero, and use the variational bound for functions in [0,1]. Therefore an additional action cost larger than (M−m)ε makes action 1 strictly worse under this model. With exact consequence matching and equal cost, task-only expected utility is indifferent. An arbitrary deterministic tie rule can still choose one action; observed choice alone is not proof of a strictly positive continuation value.

A preference that violates this bound rejects at least one declared premise: consequence/belief matching, bounded payoff, cost matching, the task-only payoff class, or the response model. It does **not** uniquely identify a direct Q term, still less felt fear. Agent beliefs, rather than evaluator truths alone, govern its decision score. Equal one-variable marginals are not sufficient to invoke the joint-law bound.

Adding θQ to a known installed payoff gives an extra θδq. In the B witness, θ>1/2 makes action 1 preferred. This is a constructed control coefficient in specified units. The same behavior could instead come from a different believed dependence or an omitted obligation. Reward/planner decomposition and reward-transformation ambiguities remain. Action preference supplies neither wanting/liking identity nor negative-valence orientation.

## 9. Verification, errors and reproducibility scope

The standard-library script checks all sixteen Boolean payoff decompositions and all endpoint contrasts, constructs both causal witnesses, enumerates twelve monotone tables, verifies the exact 1/8 restricted-interface regret, checks three OR/AND substitution settings and thirty-two total-variation inequalities. All executed assertions pass. Results use rational strings; there is no statistical sampling, model training or subjective data.

The pre-execution protocol mistakenly anticipated sixteen constrained causal-table pairs. The exhaustive count is twelve (four choices of Q_0's sole one, then three choices of an excluded Q_1 position). The protocol is retained unchanged and this correction is explicit. No failed execution occurred. Rejected scientific shortcuts are preserved: independence without evidence; separate calibration as joint sufficiency; universal successor attenuation; choice as strict preference; and preference as fear.

R95's listed script/results were read, and the baseline remote tree contains no R95 checkpoint archive or saved weights. Its script returns summary outputs rather than saving weights. This is a preservation gap, not evidence that the reported results are false. No original R95 checkpoint is claimed to have been reanalyzed here. Any later deterministic regeneration must be labeled regeneration, retain all prescribed seeds and failures, and preserve the generated weights rather than overwrite original results.

## 10. Prior art and originality judgment

Hadfield-Menell et al., *The Off-Switch Game* (2017), explicitly analyze instrumental preservation incentives under expected utility. Turner et al., *Optimal Policies Tend To Seek Power* (NeurIPS 2021), derive incentive tendencies under environmental symmetries. These block a novelty claim for task-based preservation itself.

Bartl et al., *Marginal and dependence uncertainty: bounds, optimal transport, and sharpness* (2018 revision), introduction and Eq. (1.1), directly situate expectation bounds with known marginals and unknown dependence. The Bernoulli formulas here are elementary instances of that established mathematics. Armstrong and Mindermann (NeurIPS 2018 / 2019 revision) establish limits of policy–planner–reward identification. A Blackwell original-paper retrieval returned 403; no full reading of it is claimed.

R84 already treats additive continuation-score identifiability. R82 already shows that matched marginals can hide task-relevant joint relations. R96D's incremental contribution is to carry that lesson into R95's prospective continuation controller: it supplies action-conditional, monotone causal witnesses, a sharp preference interval and an explicit criterion for when consequence matching is sufficient. This is a useful methodological result and experiment-design correction, **not a historical-first claim or a major consciousness breakthrough**.

## 11. Conclusion and concrete next step

**Additional R97 training-identifiability gate.** The concurrent R96 proposes learning from bundled trials under distinct reward ancestry. Before training, check whether these mechanisms actually supply distinct information on the training support. If two ancestry descriptions generate exactly the same distribution of every observed training input, target/reward, action consequence and feedback, and the learner gets no ancestry side channel, they cannot induce different learned-policy distributions merely because their unobserved descriptions differ. With identical initialization and random stream, a deterministic update rule yields exactly identical parameters step by step (induction on the update index). If their optimal held-out actions differ, identical training information cannot guarantee both continuations. R96D's matched-interface lower bound is an instance of this information restriction, but no new learned-policy trial is claimed. A valid next protocol must either introduce declared disambiguating training interventions, document different information/architectural priors, or explicitly make unavoidable held-out ambiguity the negative-result target. Do not treat inability to recover hidden reward ancestry from identical data as failed consciousness or failed intelligence.

Prediction, instrumental continuation choice and felt fear remain distinct. We now have a stronger positive statement: in a specified controller family, task-optimal continuation behavior can require an installed dependence-sensitive consequence representation even when every separate availability prediction is already exact. Under a justified complete-K UCT interpretation, genuinely necessary realized organizational relations concern experiential organization; the task-specific number 1/8 and the interaction term d are not experiential scales.

Next use only these two finite contexts to specify a minimal predictor-to-controller interface: a matched marginal-only consumer versus a joint-law or direct-task-success consumer, identical known payoff/cost and no hidden context bypass. First determine whether the deterministic R95 checkpoints are relevant; if not, state that limitation and design a tiny uncertain-future extension before training. Freeze seeds, optimization budget, exact law targets, all checkpoints and failure rules. Test acquisition and installed use, not fear words. A gain in task-sensitive joint prediction would still not identify primitive self-preference or phenomenal fear. R88's pending prerequisites and R89's unresolved valence bridge remain unchanged. No further truth-table expansion is needed.
