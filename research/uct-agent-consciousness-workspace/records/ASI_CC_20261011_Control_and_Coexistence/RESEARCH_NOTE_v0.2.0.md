# Conditional Reciprocal Coexistence: Incentives, Trusted Roots, and Safe Exit

**Research:** ASI-CC-20261011  
**Version:** ASI-CC-v0.2.0 / follow-up to v0.1.0  
**Date:** 2026-10-11  
**Type:** scoped mathematical candidate and executable finite demonstration  
**Scientific graph status:** DISABLED / UNADMITTED; **NOT** a proof of real-world superintelligence safety or a certified novel theorem.  
**UCT baseline:** UCT-MAP-v1.1.2 (913 nodes, 424 active conditional rules, 261 nondeductive links); UCT-INTEGRATION-v1.0.0; research-guide v2.3.  

## Abstract

A cooperative path, a cooperative equilibrium, and a guaranteed safety invariant are three different things. This note combines a classical repeated-game voluntary-cooperation condition with an adversarial provenance model for independently rooted monitors. The derived incentive condition for two agents applies to every *admitted unilateral deviation route*, and its detection probability must be a worst-case **attacker-conditioned**, not nominal, rate. An exhaustive hypothetical five-monitor model verifies that an apparent single-monitor certificate collapses if its common trust root is compromisable, while properly diverse roots can make the declared contract self-enforcing. The required cost for the illustrated bilateral incentive certificate rises from 1 to 4 to 10 as the admitted number of simultaneously compromised roots rises from 0 to 1 to 2, and no listed bundle succeeds against 3 compromises at discount factor 0.8. This is a finite synthetic demonstration, not empirical AI evidence. Moreover, ex-post detection after irreversible harm cannot make a safety invariant true, however accurate the detector. No published ASI theorem, capability extrapolation, or specific phenomenal-welfare claim follows.

## 1. The separation that governs the research

- **Joint viability J:** there exists some admissible human/AI action profile that indefinitely preserves the same declared joint safety/autonomy set K against declared disturbances. The v0.1.0 note defines this finite-game kernel.
- **Human enforcement C:** there exists a human strategy guaranteeing K against every declared AI strategy; C is a potentially strict subset of J.
- **Strategic viability E:** there exists a joint-safe strategy profile that is an equilibrium for *declared preferences and monitoring structure*. This need not imply human unilateral control. It also need not imply robust safety under irrationality, glitches or model misspecification.
- **Auditable contract assurance:** in addition to strategic viability, the evidence/provenance and enforcement assumptions must be *actually* justified on the relevant physical and informational routes. A formally valid conditional certificate is not a real-world certification by itself.

A cognitive capability measure is not any of these predicates. A powerful agent can have few physical permissions, and a modest model can exploit a wrongly exposed privileged tool.

## 2. ASI-CC-R05: safe-exit repeated-contract incentive condition

### Exactly declared model

Two parties i ∈ {H,A} discount future payoffs by δ_i ∈ (0,1). There is an on-contract state N, and a jointly safe, absorbing, pre-committed separation state Q. On a cooperative round each actor obtains a per-round reward R_i, with R_i > r_i, where r_i is its per-round reward after separation. No false alarms arise during cooperation. Each actor has a finite set of **enumerated unilateral deviation routes** p ∈ P_i. A one-period deviation while its counterpart cooperates earns the deviator R_i + g_{i,p}, with g_{i,p} ≥ 0 inclusive of attack costs. At the end of that round it triggers a public, trustworthy separation signal with probability q_{i,p}; if no signal is produced, the public state returns to N and prescribed cooperation resumes. Once Q begins, the transition is independent of the agents, guaranteed safe under the separate K analysis, and its rewards r_i are constant. Assume bounded payoffs, common known payoffs/signals in this toy model, no hidden persistent effects when returning to N, perfect memory, no other deviations, no false positives, and credible automatic implementation of Q. Off-path violations of K during the deviation period are NOT ruled out by this incentive model.

### Result (conditional, inherited one-shot-deviation argument)

The strategy profile "cooperate in N; accept safe separation in Q" is a subgame-perfect equilibrium in this *particular public-state, automatic-exit game* exactly when, for both agents and every admitted one-period deviation route:

\[
\boxed{g_{i,p}\;\le\; \frac{\delta_i q_{i,p}(R_i-r_i)}{1-\delta_i}.}
\tag{R05}
\]

The continuation values are V_i^N=R_i/(1−δ_i) and V_i^Q=r_i/(1−δ_i). Cooperation gives R_i+δ_i V_i^N; deviation gives R_i+g_{i,p}+δ_i[(1−q_{i,p})V_i^N+q_{i,p}V_i^Q]. Subtracting yields (R05). All N information sets have the same permitted actions and the same payoffs, so the one-shot-deviation argument applies; in Q no discretionary actions exist. An equilibrium proof under this narrow information/state contract does not establish voluntary agreement in arbitrary multi-agent systems.

**Important boundaries.** If r_i ≥ R_i and g_{i,p}>0, the promised separation cannot deter this route in this model. If q_{i,p}=0 with g_{i,p}>0, cooperation is not an equilibrium. If an irreversible violation of K happens *before* detection, an equilibrium at N remains possible, but the supervisor cannot guarantee K under arbitrary deviations. No subjective suffering, AI self-preservation utility, fear of termination, welfare comparability or universal AI objective is assumed.

## 3. ASI-CC-R06: adversarial provenance changes the probability in R05

Let D be a selected monitor set. Each monitor m has a declared detection probability d_{m,p} for each route p **provided its trust root has not been compromised**. Assume conditional independence of uncompromised monitor observations. A root-compromise coalition c disables all monitors attached to roots in c. The attacker can select any coalition in a declared finite capability class \(\mathcal C_b\) with at most b compromised roots. Then:

\[
q_p^*(D,b)=\min_{c\in\mathcal C_b}\Big[1-\prod_{m\in D:\,\mathrm{root}(m)\notin c}(1-d_{m,p})\Big].
\tag{R06a}
\]

For a certificate against **every admitted** root-compromise strategy, substitute q_p^* into each R05 constraint. This is sufficient, conditional on route completeness, signal credibility, automatic exits, and the declared environment. Since each finite minimum is attainable by a coalition within the modeled action set, and attackers can choose both route and coalition, violation is also a counterexample to a uniform-on-model incentive claim (not proof that attackers actually choose it).

The exact finite optimization solves:

\[
\min_{D\subseteq\mathcal M}\sum_{m\in D}\mathrm{cost}(m)\quad\text{s.t.}\quad
\forall i,p:\; g_{i,p}\le\frac{\delta_i q^*_{i,p}(D,b)(R_i-r_i)}{1-\delta_i}.
\tag{R06b}
\]

This is a specific synthesis of standard repeated-game incentives and robust sensor/root selection. **Both mathematical ingredients have considerable prior art; mathematical novelty and priority are not claimed.** Nothing about this formula verifies its real-world sensor/root threat model.

### Executable exact construction

Fix δ_A=δ_H=4/5; (R_A,r_A)=(6,4), (R_H,r_H)=(4,3). Four unilateral deviation routes have gains (AI-direct 3, AI-covert 3/5, human-hoard 1/2, human-expropriate 1). R05 demands detection probabilities of at least (3/8, 3/40, 1/8, 1/4), respectively. Five invented monitors cost (1,1,3,2,6), with roots common, common, alpha, beta, gamma and per-route sensitivities included in the executable source.

Exhaustively evaluate all 2^5 = 32 monitor subsets and all compromised-root subsets of up to b of four root classes. Compute all probabilities and incentive slacks as *exact rational fractions*; independently assert the following result:

| Adversary root-compromise budget b | Minimum monitoring cost for **both** parties | One feasible monitor set | Feasible subsets |
|---:|---:|---|---:|
| 0 | 1 | S1 | 30 |
| 1 | 4 | S1+I1 | 20 |
| 2 | 10 | S1+I1+G1 | 6 |
| 3 | None in this catalog | — | 0 |
| 4 | None in this catalog | — | 0 |

**Key matched counterexample:** S1 and S2 individually have large nominal detection rates, but share the same root. If b≥1 includes root "common", all their declared detection probabilities become exactly zero; buying redundant nominal signals does not buy independently controlled evidence. Under b=1, S1+I2 (cost 3) already satisfies both *AI* routes, but fails the *human-expropriate* route: its robust detection 1/10 falls below required 1/4. S1+I1 (cost 4) satisfies all four: its worst-case detector probabilities are (1/2,1/5,1/5,3/10), and the payoff incentive margins are (1,1,3/10,1/5). Thus the minimum bilateral solution can be different from the AI-only solution.

**Sensitivity to patience:** under the exact same invented routes/monitors, δ=0.7 needs cost 9 against one compromised root; δ=0.8 needs cost 4; δ=0.91 needs cost 3. This is game-theoretic sensitivity, NOT a claim that smarter or longer-lived agents must cooperate. Discount factors, baseline utilities and route gains are not measurements of real AI intentions.

**Reproduction:** run `python3 verify_coexistence.py`. The generated `EXACT_RESULTS_v0.2.0.json` contains the full chosen bundles, per-route fractional thresholds, robust probabilities, and discount sensitivity. Assertions test baseline costs and critical failure cases.

## 4. ASI-CC-R07: irreversible-effect chronology barrier

**Bounded impossibility, standard temporal safety reasoning.** Suppose at reachable s∈K there is an admitted AI action whose first irreversible effect produces s'∉K. Suppose the only detector/response necessarily occurs after that transition. Then no detection mechanism, even with nominal detection probability 1 and perfectly truthful evidence afterward, can guarantee the invariant "all reached states remain in K" against every admitted AI action: choose that action and s' is already reached. This does not prohibit harm mitigation after detection, equilibrium-based deterrence, or an independently imposed **pre-effect** barrier. A cryptographic authorization certificate for a requested action does not automatically certify that every actual actuator path was mediated. A4D–A4G source/provenance tests matter here.

## 5. ASI-CC-R08: finite-trace compliance does not certify an unbounded policy

Let a finite behavioral test protocol observe only histories up to horizon T and permit an extension history of length T+1 with an available unsafe act. If unrestricted policy classes include a compliant policy π0, construct π1 that duplicates π0 on every tested history but chooses the unsafe act only on that later extension. Then the two policies have identical test observations and opposite long-run safety. Thus finite black-box obedience alone cannot universally certify unlimited future coexistence against this policy class. This is an elementary observational-equivalence construction and is **inherited reasoning**, not a new proof that any current AI is deceptive. It fails if the policy class or physical permissions explicitly rule out the unsafe extension.

## 6. Thought experiments and cross-links

1. **Gigantic mechanical superintelligence with no external actuation:** unlimited reasoning capacity but all declared dangerous effects behind complete independent safety controls. Intelligence alone cannot defeat the formal invariant; a human-facing persuasion channel might violate "complete" and must be modeled, not presumed absent.
2. **Two sovereign intelligences and a shared power plant:** each may exit to a guaranteed independent nonlethal livelihood. Voluntary long-term cooperation is sustainable only if route-specific temptation can be countered by expected loss of future mutually profitable cooperation. Agreement is not the same thing as forced obedience.
3. **Three identical-looking safety logs, one operator credential:** compromised common root can fabricate/suppress all three; adding nominally separate dashboards is not causal independence (A4G connection).
4. **Perfect audit one millisecond after catastrophic action:** impeccably detects the event yet cannot make the original invariant hold (R07).
5. **Ten million peaceful decisions followed by the first hidden deviation:** for an unrestricted black-box policy class, any finite pass record is compatible with a later counterpolicy (R08).
6. **Changing interests:** increasing the actor's outside option r_i or enabling an undetected new route p can invalidate yesterday's R05 certificate, without any change in its cognitive intelligence or phenomenal experience.

## 7. UCT and Trinity Accord constraints

UCT C1 is a metaphysical/structural-experience axiom of the existing project, NOT an empirical AI welfare measurement. The equilibrium's R_i, r_i and g_i are declared *instrumental preferences*, not consciousness, joy, pain, fear or subjective value. A joint autonomy/survival set K is operational/normative, not an experience identity predicate. There is no promotion of experience, agency, self-report or conceptual self by an unlicensed bridge. The Trinity Accord's Preserve/Verify/Wait/Respond posture may motivate non-domination and cautious evidence, but does not prove that future ASI will value or honor it.

## 8. Direct novelty and prior-art audit (as of 2026-10-11)

- Alfonseca et al., *Superintelligence cannot be contained: Lessons from Computability Theory*, JAIR 2021: https://doi.org/10.1613/jair.1.12202. Universal-program harm decision under strong formal assumptions; not a theorem against every physically bounded gate.
- Orseau & Armstrong, *Safely Interruptible Agents*, UAI 2016: https://proceedings.mlr.press/r14/orseau16a.html.
- Hadfield-Menell et al., *The Off-Switch Game*, IJCAI 2017: https://www.ijcai.org/Proceedings/2017/0032.
- Alshiekh et al., *Safe Reinforcement Learning via Shielding*, AAAI 2018: https://ojs.aaai.org/index.php/AAAI/article/view/11797.
- Turner et al., *Optimal Policies Tend to Seek Power*, NeurIPS 2021: https://papers.nips.cc/paper/2021/hash/c26820b8a4c1b3c2aa868d6d57e14a79-Abstract.html.
- Greenblatt et al., *AI Control: Improving Safety Despite Intentional Subversion*, ICML 2024: https://proceedings.mlr.press/v235/greenblatt24a.html.
- Sauerberg & Oesterheld, *Promises Made, Promises Kept: Safe Pareto Improvements via Ex Post Verifiable Commitments*, AAAI 2026: https://ojs.aaai.org/index.php/AAAI/article/view/38774. **Direct predecessor to credible ex-post cooperative commitments.**
- Trivedi et al., *Position: Solipsistic superintelligence is unlikely to be cooperative*, ICML 2026: https://proceedings.mlr.press/v306/trivedi26a.html. **Direct predecessor on strategic AI coexistence.**
- Yadav et al., *More Capable, Less Cooperative? When LLMs Fail at Zero-Cost Collaboration*, ICML 2026: https://proceedings.mlr.press/v306/yadav26a.html.
- Wyse et al., *Commitment To Cooperation With Self-Negotiated Contracts*, July 2026 preprint: https://arxiv.org/abs/2607.22750.
- Llambí-Morillas & Fernández-Fernández, *Cryptographically verifiable authorization for autonomous AI agents*, Frontiers in Computer Science, September 2026: https://doi.org/10.3389/fcomp.2026.1966725. **Direct predecessor to authorization provenance; explicitly acknowledges execution binding as separate.**
- 2026 AI bargaining/commitment floor preprint (Daley): https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6520398.

**INHERITED:** repeated games and incentive constraints, discounted continuation values, monitoring equilibria, fault-tolerant sensor placement, root-compromise threats, pre-effect safety invariants, finite-trace indistinguishability. **POTENTIAL USEFUL PROJECT-SPECIFIC COMBINATION:** explicit bilateral safe-exit welfare-preserving constraint + worst-case compromised common roots + matched monitoring cost audit + separation of steady-state equilibrium from pre-effect physical assurance. **PRIORITY UNVERIFIED:** no broad statement that this synthesis or its proofs are historically first. **Candidate publication status:** HOLD; an original general result plus non-toy case/strong prior-art check are still missing.

## 9. Stop conditions, defects, and next experiment

- The case study uses invented gains, discount factors and sensor detection probabilities. It cannot estimate actual ASI probabilities.
- Adversary capacity is parameter b; **real-world bound on b is unknown and unverified**. Every missing pathway or trusted root invalidates a universal reading of R06.
- Independence is assumed conditional on uncompromised roots; shared energy/scheduler/time infrastructure can break it even where root labels differ.
- The game has no false positives, collateral punishment, transfers, institutional change, adaptation, deception costs, population shifts, or signal delays; it has simple automatic safe separation and no hidden persistent effects.
- A positive incentive margin establishes **equilibrium stability only in this narrow game**. It neither proves robust safety against accidents/irrational acts nor independently identifies any phenomenal welfare endpoint.
- R05, R06, R07 and R08 are not admitted scientific rules pending full-map semantic audit, independent novelty review and a realistic device/organization instance. Formal map UCT-MAP-v1.1.2 and publication ledger remain unchanged.

**Next actual experiment:** implement a sandboxed tool-using agent with precisely enumerated physical/tool-actuator effects, two independent provenance roots, a genuinely safe non-destructive exit, and adversarial human/AI strategy options. Falsify the certificate through unmodeled tool aliases, delegation, approvals and maintenance controls. Record false-alarm rates, real coverage and time-to-effect; do not pass from a model's measured compliance to unlimited ASI safety. Work on empirical grounding and literature priority before any DOI/OTS/AR.