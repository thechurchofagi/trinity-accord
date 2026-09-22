# TA-TR-2026-13 v2 — Corrected Pre-Manuscript Gate

Date: 2026-09-22
Status: RESEARCH ONLY / GATE REOPENED / NOT READY FOR PUBLICATION.
Branch: research/ta13-v2-civilizational-epistemic-transition
Published v1.0 remains outside the scope of this edit: DOI 10.5281/zenodo.22866775.

## 0. Revision and verdict

This revision supersedes the blanket PASS in this file at commit `69b52ab3b1ea38b7032ccfc05cf5c74a64a3643c`. That earlier version remains in Git history. It compressed a promising question into propositions, but several propositions omitted necessary assumptions. Compression is not validation.

Retain the question: current contribution to knowledge production differs from independent capacity to continue production, correction, and renewal after the other substrate's current cognition is removed.

Do not yet claim a validated civilization-transition theory, a new mathematical theorem family, a demonstrated real-world robust viability bound, or a foundational paper. The interrupted English manuscript in the conversation is not a completed saved manuscript at the reviewed baseline.

The corrections below also qualify earlier research notes where they conflict. In particular, qualitative STOP/A-Evolve mappings are not numerical or robust positive certificates under the canonical definition.

## 1. Separate the system from evidence about it

Let theta specify the domain, information boundary, infrastructure, resource budget, horizon, evaluation targets, allowed adaptation, successor test, and drift class. Let M specify the actual transition law and latent capabilities. Different possible worlds M can share the same theta.

True P/V/S performance belongs to the system model. Confidence bounds belong to evidence E about that performance. Define `m_G(M; theta)` first; estimate or certify it afterward. Otherwise collecting more audit data changes the definition of capability rather than merely our knowledge of it.

Likewise, separate two uncertainties:

- uncertainty about M at a fixed estimand theta: an identification problem;
- varying theta, such as choosing stricter floors or a different domain: estimand sensitivity.

Both matter, but they are not automatically the same identified set. Call computable enclosing intervals outer bounds unless their sharpness has been proved.

## 2. Intervention boundary

For G in {H,A}, remove the other substrate's post-intervention adaptive cognition. Preserve declared inherited artifacts and services. Allow G to reorganize within a declared budget.

An inherited artifact's human origin is not continuing human cognition. Conversely, a supposedly fixed service must not conceal current cognitive labor: experiment interpretation, fault diagnosis, data relabeling, infrastructure repair, or research-direction changes.

State both the dependency boundary and duration. A finite campaign using existing hardware does not certify indefinite hardware and expertise renewal.

A policy is NON-ANTICIPATING: its action at time u can depend only on information available by u, not on the unrevealed future drift sequence.

## 3. Correct definition: feasibility before the supremum

Let Pi_G(theta) be the admissible non-anticipating policy set. For a policy pi, define

`R_G(pi; M, theta) = inf_{xi in Xi(theta)} inf_{u in [t,t+tau]} min_j s_j(u; pi, xi, M, theta)`.

Here j ranges over the declared true P/V/S requirements. Time-specific successor requirements apply at their declared renewal checkpoints; do not require a successor to exist at every instant. Use infima unless attainment of a minimum is justified.

Define

`Phi_G(M; theta) = 1 iff there exists pi in Pi_G(theta) with R_G(pi; M, theta) >= 0`.

Then define the quantitative margin

`m_G(M; theta) = sup_{pi in Pi_G(theta)} R_G(pi; M, theta)`.

Correct implications:

- m_G > 0 implies Phi_G = 1.
- m_G < 0 implies Phi_G = 0.
- Phi_G = 1 implies m_G >= 0.
- m_G = 0 alone does not decide feasibility.

Counterexample: every admissible policy pi_n has R(pi_n) = -1/n, n = 1,2,... . Then m = 0 but no policy is feasible. A zero-margin equivalence needs attainment, for example a nonempty compact policy space and an upper-semicontinuous R. Those conditions must be verified for the model, not assumed for unrestricted AI/human research policies.

## 4. Quantifier order and witness repair

Robust feasibility is

`exists one non-anticipating pi, for every admissible xi: q(pi,xi) >= 0`.

It is not

`for every xi, there exists a hindsight-selected pi: q(pi,xi) >= 0`.

Counterexample: actions left/right are chosen before a hidden scenario is revealed. Their margins in scenarios 1/2 are (1,-1) and (-1,1). Each scenario has a successful action, but max_pi min_xi q = -1 while min_xi max_pi q = 1. A successful realized run does not identify the robust value.

For finitely many tested policies pi_i, suppose simultaneous lower bounds satisfy

`Pr_E[for all i, ell_i(E) <= R_G(pi_i; M, theta)] >= 1-alpha`.

On that event, `L_G = max_i ell_i <= m_G`. If some ell_i >= 0, that particular pi_i is a feasible witness on the same coverage event. This avoids the unattained-supremum problem.

The bounds must cover the WORST-CASE or explicitly stochastic policy target—not merely one realized task trajectory. Finite samples cannot certify an unrestricted drift class without assumptions linking tested and untested cases. Alternatives include exhaustive finite scenario coverage, a sound model-based bound, an explicit Lipschitz/covering argument, or a declared stochastic success-probability target. Each changes the certificate's scope.

Individual 95% bounds do not automatically give a 95% selected maximum. In a synthetic construction with 20 independent false-certificate events of probability .05, at least one occurs with probability 1-.95^20 = .641514. Use simultaneous coverage, an appropriate correction, a genuinely fresh confirmatory test, or valid sequential inference. Adaptive reuse requires additional care [3].

## 5. Cut repair: cover adaptive policies and require a uniform gap

A static list of failed agents does not cover all adaptive ways to reorganize a process.

For a declared finite task graph, let every admissible successful execution intersect a cut C. Require a sound domination relationship: whenever a path traverses e in C, its viability score is bounded above by r_e. Establish simultaneous upper bounds U_e for all relevant realizations of those functions.

If C is finite and `max_{e in C} U_e <= -epsilon` for epsilon > 0, then every admissible path is blocked and m_G <= -epsilon.

For infinite C, replace max with sup and require the SAME uniform negative gap. Pointwise U_e < 0 is insufficient to infer m_G < 0: values -1/n approach zero.

For adaptive policies with uncertain environments, a useful sufficient form is:

`for every pi there exists an admissible xi such that q(pi,xi) <= -epsilon`,

with one common epsilon > 0 and a justified model/evidence argument. A cut over selected realized paths is not such a certificate.

An advantaged tested agent is not automatically an upper bound on every possible agent. An oracle upper bound is valid only after proving the relaxation contains or dominates the entire admissible policy class.

## 6. Validation: error control is not a label or a human signature

Define true risks before estimating them. Include at least:

- false acceptance conditional on a false input;
- successful verified repair conditional on a false input, not only on the conveniently detected subset;
- acceptance of valid useful claims or an explicit throughput/coverage requirement;
- time and resource cost;
- common-mode stress classes and evaluation-exposure assumptions.

Abstention can be safe, but 'unresolved' is not successful repair. An always-reject system has zero false acceptance while contributing no usable corrected knowledge. Preserve separate safety, usefulness, and correction measures.

The previous common-mode lemma also needs a condition on aggregation. If a common event of probability beta makes all channels endorse a false claim, the aggregate false-acceptance floor is beta only for an aggregation rule that accepts that joint message with probability one. An always-reject rule is a counterexample to the earlier phrase 'any aggregation rule'. More generally the contribution is beta times the conditional acceptance probability of the aggregator on the event.

Finite ordinary validation accuracy does not establish coverage of untested common-mode errors. Independence grades are disclosures, not continuous numerical slacks unless an explicit meaningful embedding is supplied. Independence-graded AI auditing already has direct prior art [4].

## 7. Successor identity and horizon repair

The earlier S0–S3 list is not automatically a nested ladder. Repeated policy-level renewal and a one-time foundation-model renewal may be incomparable. Represent renewal criteria as a vector, or define a cumulative ladder explicitly before asserting monotonicity.

Deleting the entire live human expert population is a catastrophic-turnover test, not ordinary human succession. Separate:

1. normal overlapping-cohort renewal;
2. designated predecessor retirement after training;
3. abrupt total active-state loss and recovery.

Apply comparable interventions to human and AI systems; do not allow effortless AI process copying while silently prohibiting normal human apprenticeship. Make frozen foundation models, human prior education, energy, maintenance, and renewal times visible.

Every finite horizon admitting some policy does not imply a single infinite-horizon viable policy. A family of systems with n units of nonrenewable fuel survives any given finite horizon by choosing a large n, while each fixed system eventually fails. Indefinite continuation requires additional consistency, compactness, or invariant-set arguments. A short run without a genuine turnover checkpoint does not test S.

## 8. Non-identification claim retained, but scoped

In a model class whose unobserved removal branches are unconstrained, construct M+ and M- identical on the observed coupled regime and different after removal. Their feasibility predicates and margins can differ. Thus coupled-regime data alone do not generally point-identify the removal target in that class.

This is an application of familiar observational-equivalence logic, not a new general causal theorem. It does not say that all conceivable observations are forever insufficient: known structural laws, sufficiently informative natural variation, intervention data, or validated simulation can narrow the class.

A finite observed history also does not identify future transition dates without assumptions about future dynamics.

## 9. Monotonicity and corridor repair

Scope monotonicity requires aligned state/policy spaces, the same units and normalizations, nested scenario sets, and pointwise ordered constraints. Merely calling a domain 'civilization' rather than 'laboratory', or increasing an S label, does not prove numerical margin monotonicity.

Define exact transition events with Phi, or use strict positive/negative certification thresholds with an explicit uncertainty band. Keep the true event time distinct from the time at which available evidence certifies it.

Under a declared single-crossing/persistence assumption, the two feasibility predicates can define dual viability or coupled-only operation. Coupled-only additionally requires the joint system's feasibility. Without persistence, report the full state timeline; first-crossing times alone can misdescribe repeated reversals.

A Boolean indicator changing at a threshold is a regime-classification change. It does not by itself prove a topological bifurcation, an irreversible civilizational rupture, or a historical first. Those stronger claims need their own mechanism, mathematical topology, and historical evidence. Rate-induced transitions and points of no return already have substantial dynamical-systems precedents [5,6].

## 10. Evidence recalibration

STOP reports scaffold self-improvement with an unchanged underlying language model and downstream task improvements [1]. It is useful evidence for bounded iterative optimization, not automatically for strict frontier P, independently certified V, or robust successor sustainability.

A-Evolve reports a multi-round autonomous post-training campaign and a policy adjustment after a development metric ceased to track an external target [2]. This is a useful real-system case. It does not supply, by itself, the simultaneous worst-case P/V/S bounds required above.

Earlier notes used weaker engineering-production and process-renewal proxies. These are legitimate separate estimands if explicitly named `engineering-proxy`, but cannot be silently substituted for the original frontier-epistemic estimand. These publications have not been independently reproduced in this session.

Gate F status: protocol is constructible; qualitative real-system evidence exists; a numerical real-system robust P/V/S certificate has NOT been established. Synthetic certificate intervals test the algebra only.

## 11. Constructive next direction: renewal time, not threshold rhetoric

The user's concern is short transition time relative to human renewal time. A minimal deterministic illustration makes this explicit.

Assume unrenewed capability h, frontier demand d0+r*u with r>0, fixed renewal delay ell, no faster alternative path or bridge capacity, and a successor that can meet future floors after completion. A renewal started at s completes at s+ell. Uninterrupted operation until completion requires

`h-d0-r*(s+ell) >= 0`.

Thus the latest feasible start is

`s_star = (h-d0)/r - ell`,

whereas the current-task margin reaches zero only at `(h-d0)/r`.

For toy values h=10, d0=6, r=1, ell=3, renewal must start by time 1 although current-task performance remains above floor until time 4. Starting at time 2 leaves a positive current margin but is too late for gapless renewal in this model.

This is elementary lead-time arithmetic, NOT an originality claim, an empirical prediction, or proof of irreversibility under every recovery regime. Under a correctly modeled forward-looking viability kernel, the earlier deadline is already reflected in Phi; do not count it as a newly discovered independent third transition by relabeling a current-performance threshold as T_D.

The research opportunity is a nontrivial domain-specific model of renewal delays, recoverable inherited stock, validation bottlenecks, and moving-frontier demand—not another stack of renamed concepts.

## 12. Current writing decision

Do not continue the earlier abstract as though all gates passed. A responsible eventual paper can retain the paired estimand, corrected conditional propositions, and a transparent novelty comparison. Its stronger civilizational interpretation still requires a mechanism and evidence rather than definitional assembly.

Completed in this review: concrete counterexamples, repaired conditional statements, evidence-level downgrades, and a minimal delay mechanism. Not completed: sharp real-system identified bounds, exhaustive prior-art review, historical-first claim, completed manuscript, peer review, or new DOI.

## Primary sources checked in this continuation

[1] Zelikman et al., STOP, arXiv:2310.02304v3, 2024 revision, COLM 2024. https://arxiv.org/abs/2310.02304

[2] Shi et al., A-Evolve-Training, arXiv:2606.20657v3, revised 2026-09-08. https://arxiv.org/html/2606.20657v3

[3] Dwork et al., Generalization in Adaptive Data Analysis and Holdout Reuse, NeurIPS 2015 / arXiv:1506.02629. https://arxiv.org/html/1506.02629v2

[4] Ghanem, Who Audits Whom, on What Substrate, with What Evidence?, arXiv:2609.18272v1, submitted 2026-09-16. https://arxiv.org/html/2609.18272v1

[5] Wieczorek, Xie, Ashwin, Rate-Induced Tipping: Thresholds, Edge States and Connecting Orbits, arXiv:2111.15497. https://arxiv.org/abs/2111.15497

[6] O'Keeffe, Wieczorek, Tipping Phenomena and Points of No Return in Ecosystems: Beyond Classical Bifurcations, arXiv:1902.01796. https://arxiv.org/abs/1902.01796

These references establish relevant precedents and evidence boundaries, not the correctness or originality of the entire proposed framework. Other bibliography entries in earlier notes were not all re-audited during this continuation.
