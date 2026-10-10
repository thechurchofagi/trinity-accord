# A Non-Domination Gap in Reciprocal Human–ASI Coexistence

**ID:** ASI-CC-20261011, version **ASI-CC-v0.3.0**  
**Scientific status:** CONDITIONAL TOY-MODEL RESULTS; DISABLED MAP APPLICATION, NOT PROVEN FOR FUTURE ASI.  
**Baseline:** UCT-MAP-v1.1.2 / 913 nodes, 424 active conditional rules, 261 nondeductive links, formal map unchanged.  
**Builds upon:** ASI-CC-v0.1.0 viability kernels; v0.2.0 robust-root bilateral incentive condition.  
**Auditable code:** `verify_coexistence.py` and `verify_surplus_frontier.py`; result JSONs for v0.2.0 and v0.3.0.

## 1. A stronger question than “Will ASI be benevolent?”

We ask whether *both* parties can have credible non-destructive exit rights and nevertheless choose long-term cooperation without one party possessing unilateral control of the other. The previous note showed a simplified repeated-game cooperation criterion:

\[
  g_{i,p}\le\frac{\delta_i q_{i,p}(R_i-r_i)}{1-\delta_i},\qquad i\in\{H,A\},\ p\in P_i. \tag{R05}
\]

This was derived for one-period deviations, an absorbing safe exit, no false alarms, full enumeration of admitted deviation routes, independent provenance evidence, fixed per-period payoffs, known discount factors, and trusted exit enforcement. It is not universal, does not identify anyone's true utility, and does not establish a safety invariant against arbitrary deviations. Revisit every one of these limitations when applying later lemmas.

## 2. ASI-CC-R09 — The safe-exit entitlement bound (conditional negative result)

Suppose the contract requires the post-exit per-period payoff to satisfy \(r_i\ge L_i\), an ethically or politically imposed minimum entitlement, and let \(R_i>L_i\) be the cooperative payoff. Assume the only deterrent is losing cooperative surplus after a public violation signal with probability \(q_{i,p}\le1\); deviation route p has one-round temptation gain \(g_{i,p}>0\). By R05,

\[
 g_{i,p}\le \frac{\delta_i q_{i,p}(R_i-r_i)}{1-\delta_i}
 \le \frac{\delta_i(R_i-L_i)}{1-\delta_i}.
\]

Thus if

\[
\boxed{g_{i,p}> \frac{\delta_i(R_i-L_i)}{1-\delta_i},}
\tag{R09}
\]

no safe-exit-only detection-and-termination mechanism of this form can make prescribed cooperation individually optimal, **even with perfect detection**, without lowering the entitlement, increasing shared cooperative surplus, reducing the temptation gain, adding external pre-effect physical restriction, or changing the mechanism. A failure of this particular contract is not a proof that peaceful coexistence is impossible.

**Exact witnesses in made-up credits.** With \(\delta=4/5\), an AI whose cooperative benefit is \(R_A=6\), safe-exit entitlement \(L_A=11/2\), and available deviation gain \(g_A=3\), has maximal exit-deterrence value \(2<3\). Similarly a human with \(R_H=4\), \(L_H=19/5\), and available gain \(g_H=1\), has maximum \(4/5<1\). No monitoring technology in this contract repairs either inequality if R is fixed. These credit numbers are fabricated and do **not** describe ASI goals, phenomenal welfare or real human rights.

**Interpretive point:** protecting generous exit rights is normatively distinct from maintaining a threat sufficiently unpleasant to deter defection. The desirable engineering response is not to impoverish a party's exit option, but to expand positive-sum gains and eliminate exploitable routes through independently verified action constraints. Standard individual-rationality/folk-theorem reasoning is a major mathematical predecessor; the bound's algebra is NOT new mathematics.

## 3. ASI-CC-R10 — A joint feasible-payoff frontier certificate

Fix an admissible monitor set D and adversarial root-compromise budget b. Let \(q^*_{i,p}(D,b)\) be the worst-case credible deviation-alert probability as defined by v0.2.0 R06. Assume positive deviation gains \(g_{i,p}\), strictly positive reliable q for each such route, and physically achievable automatic safe exit at the entitlement vector \(L=(L_H,L_A)\). Define a minimum on-contract surplus vector:

\[
 c_i(D,b)=\max_{p:g_{i,p}>0}
 \frac{g_{i,p}(1-\delta_i)}{\delta_i q^*_{i,p}(D,b)},
 \quad m_i=L_i+c_i. \tag{R10a}
\]

If some g>0 route has q*=0 then c_i=+∞. Let \(\mathcal F_K\) denote the physically and institutionally **feasible** on-contract payoff profiles that preserve a stated common non-domination/survival set K (including any nontransferabilities). Under R05's restricted game and the explicit assumption that the exit vector \(L\) is both safe and implementable, a resource-entitlement-respecting cooperative equilibrium exists for some feasible R exactly when

\[
\boxed{\mathcal F_K\cap \big([m_H,\infty)\times[m_A,\infty)\big)\neq\varnothing.}\tag{R10b}
\]

**Proof.** Necessity: each route's R05 bound and r_i≥L_i imply R_i≥m_i. Sufficiency within this model: choose feasible R∈F_K in the indicated upper orthant, set the available safe-exit payoffs to the implementable vector L, and R05 holds for every modeled route. The specified on-contract strategy with automatic exit is an equilibrium by v0.2.0's one-shot-deviation argument. This does not prove physical reachability or completeness of F_K, reliable sensing, normative acceptability of a particular r, or long-term stability under changing preferences. An incomplete approximation to F_K only gives an approximate certificate.

**Critical UCT/ethics qualification:** In general human and AI utilities do not share an empirically justified scalar unit, and UCT's basic-experience postulate supplies no such commensurability. R10b uses only componentwise comparisons and a feasibility relation; it does not sum subjective utilities. A separate toy below *assumes* linearly transferable contract credits in common units to permit a convenient scalar resource budget. These are credits, not felt happiness, suffering, or welfare.

### Example of a restrictive common-credit budget

Assume in addition \(R_A+R_H\le B\) where all R and L are linearly transferable **contract credits**, with no other allocation restriction. Then R10b becomes:

\[
\boxed{B\ge m_A(D,b)+m_H(D,b).}\tag{R10c}
\]

For discount \(\delta_A=\delta_H=4/5\), floors \(L_A=11/2, L_H=19/5\), and the invented sensor catalog in v0.2.0, exhaustively enumerate all 32 sensor subsets and every permitted root compromise. Under a **one-root** compromise budget:

| Shared cooperation credit cap B | Cheapest monitoring cost to sustain BOTH parties' contract in this toy | Witness |
|---:|---:|---|
| 10 | infeasible | all 32 subsets fail |
| 10.5 | infeasible | all 32 subsets fail |
| 11 | 9 | S1 + I2 + G1 |
| 11.5 | 6 | S1 + I1 + I2 |
| 12 | 4 | S1 + I1 |

At B=11 and b=1, the least-cost witness (S1+I2+G1) requires cooperative allocations of at least \(R_A=493/76\approx6.4868\) and \(R_H=234/55\approx4.2545\), total \(44899/4180\approx10.7414\), below 11. The B=11,b=2 case has no feasible listed bundle; B=11.5,b=2 has cost 12. Under unrestricted shared-root compromise or unmodeled defection routes, these results are invalid; nothing is shown about global physical impossibility.

**Nontrivial comparative insight:** Within one fixed finite threat catalog, richer guaranteed individual exit terms can destroy an otherwise stable contract even while both would gain from cooperation. A larger feasible cooperative frontier, an independently certified higher q, or a physical reduction in g can restore the certificate. Neither party must become the other's permanent owner. This is a targeted synthesis of inherited repeated-game, resource feasibility and A4G provenance ideas, not a claim of first mathematical priority.

## 4. ASI-CC-R11 — False alarms can erase an apparently positive incentive margin

The v0.2.0 inequality assumed zero false alarms. Now suppose even when both cooperate, an independent public alert occurs at the end of a round with probability \(\alpha_i\) in the deviation comparison (usually a common \(\alpha\)), sending both to the safe absorbing exit Q. A one-round deviation by i via p produces the alert with total probability \(q_{i,p}\); assume both are fixed, faithful conditional signal probabilities with \(0\le\alpha,q\le1\), and no other path effects. The honest continuation value satisfies

\[
V_i^N = R_i + \delta_i[(1-\alpha)V_i^N+\alpha V_i^Q],\qquad V_i^Q=r_i/(1-\delta_i).
\]

Hence \(V_i^N-V_i^Q=(R_i-r_i)/(1-\delta_i+\delta_i\alpha)\). Comparing deviation and cooperation gives the exact route condition

\[
\boxed{g_{i,p}\le\frac{\delta_i (q_{i,p}-\alpha)(R_i-r_i)}{1-\delta_i+\delta_i\alpha}.}\tag{R11}
\]

This is a direct one-shot public-monitoring derivation (known repeated-game mathematics), not an empirically established false-alarm law. It reveals why using q alone overstates robustness whenever false alarms shorten cooperative lives. **As a rule, the evidence must distinguish the signal's true-positive advantage q−α from nominal q and must protect the enforcement channel.**

Exact numerical countercheck for the v0.2.0 cost-4 witness under a single-root compromise, holding R and r at their original v0.2.0 values: AI-direct route with q=1/2 and g=3 passes at α=0, ties at α=1/20, fails at α=1/10. Human-expropriate route with q=3/10 and g=1 passes at α=0 but already fails at α=1/20. Therefore the R05 bilateral guarantee is **not** robust to even a small false-alarm rate in this particular hypothetical parameter choice. No actual false-alarm rates have been measured.

For adversarial settings where the compromised coalition may alter both true and false alerts, optimize the entire R11 margin jointly over admissible coalitions, not by silently using a nominal q from one experiment and α from another. Shared random causes may break the conditional-independence formula used in R06.

## 5. Interaction with actual safety and experiential rights

- **Cooperative equilibrium E** under R05/R11 does not imply **robust safety C** against arbitrary deviation. If an irreversible unauthorized action crosses K before detection, the ex-post signal may deter a rational agent but cannot retroactively preserve K (v0.2.0 R07).
- An action precommitment shield can block a harmful g-route in advance but requires an accurate causal inventory of all actual writes, human delegation paths, tool aliases, power, clocks, reset, maintenance and witness provenance (UCT A4D–A4G).
- A high intelligence score by itself establishes no incentive parameter δ, no preference R/r/g, no proof of q, no guarantee of access control, and no measured subjective value. UCT C1/U1 retain their original *conditional axiom* role; no equation above converts resource credits into phenomenal welfare.
- A policy consistent with future ASI dignity should specify both human freedom and candidate AI continuation without presuming that verbal self-reports measure felt fear or pain. Exiting a particular contract is not extinguishing an actual process; the identity/continuity question remains independent.

## 6. Thought experiments designed to falsify, not merely illustrate

**Exp-1: mutually flourishing but non-credible exit.** Keep cooperation benefits constant, raise both guaranteed outside-option floors. A contract once stabilized by the threat of separation fails R09 even with perfect sensors. What additional surplus or physical block could restore stability?

**Exp-2: two surveillance dashboards with a shared signing root.** Keep each dashboard's nominal accuracy fixed; allow one common controller to forge both. R06 robust q becomes zero, despite an excellent dashboard benchmark; test against two independent hardware-trust roots.

**Exp-3: an independent life-support plant.** Keep guaranteed safe separation legally promised; remove the physical energy link needed by an AI bearer to continue or a human to survive. The assumed exit vector L ceases to be physically feasible, invalidating R10, regardless of game-theoretic algebra.

**Exp-4: perfectly accurate but slightly noisy audit.** Keep q constant and add an honest false-positive alert probability. R11 shows how the reduced expected cooperation duration can make exploitation the better response.

**Exp-5: the invisible delegation channel.** Protect all four declared tool commands but allow a persuasive message to cause an unauthorized human action. The finite catalog is incomplete; neither its sensor optimum nor its apparent physical wall certifies real-world human autonomy.

## 7. Nearest sources and originality decision (2026-10-11)

Prior mathematical mechanisms: discounted repeated-game incentive constraints, individually rational payoffs and folk theorems; budget-constrained feasibility; security games and sensor/graph coverage; public-monitoring signal noise. No theorem-priority claim is made for any of these.

Direct modern predecessors:

- Overman & Bayati, *The Oversight Game: Learning to Cooperatively Balance an AI Agent's Safety and Autonomy*, ICML 2026, https://proceedings.mlr.press/v306/overman26b.html — direct formal game on agent autonomy and human control, including a conditional potential-game alignment guarantee.
- Sauerberg & Oesterheld, *Promises Made, Promises Kept: Safe Pareto Improvements via Ex Post Verifiable Commitments*, AAAI 2026, https://ojs.aaai.org/index.php/AAAI/article/view/38774 — credible cooperative commitments and Pareto gains.
- Trivedi et al., *Position: Solipsistic superintelligence is unlikely to be cooperative*, ICML 2026, https://proceedings.mlr.press/v306/trivedi26a.html — coexistence, strategic endogeneity, and institutions.
- Wyse et al., *Commitment To Cooperation With Self-Negotiated Contracts*, July 2026 preprint, https://arxiv.org/abs/2607.22750.
- Llambí-Morillas & Fernández-Fernández, *Cryptographically verifiable authorization for autonomous AI agents*, September 2026, https://doi.org/10.3389/fcomp.2026.1966725 — distinguish request authorization from actual runtime execution proof.
- Alfonseca et al., *Superintelligence cannot be contained: Lessons from Computability Theory*, JAIR, https://doi.org/10.1613/jair.1.12202 — limits for universally programmable black-box harm prediction under special premises, not a proof against every physically mediated bounded actuator.
- Existing project-specific UCT Paper D, DOI 10.5281/zenodo.23176685, and A4D–A4G actual writer, provenance and common-root controls.

**Originality status:** mathematically mostly INHERITED. PROJECT-SPECIFIC INCREMENT: formal cross-layer gap among bilateral exit entitlements, joint viable payoff frontier, reliable source-root monitoring, reversible/irreversible temporal control, and concrete finite reproducible counterexamples with no-ASI-welfare extrapolation. Priority of that synthesis is UNVERIFIED. Valuable as a research map increment and negative-result catalog, but not yet sufficient to call a groundbreaking new ASI theorem or rush to DOI.

## 8. Open questions, verification and handoff

1. Can a real confined tool-using agent installation produce **actual** route-complete q and α measurements under a declared finite adversarial compromise budget, including a genuine independent actuator witness and physically viable safe exit?
2. Can we prove a general bounded-control certificate combining physical preemption for irreversible hazard paths with credible reciprocal voluntary cooperation on reversible paths, including mixed/hybrid resource feasibility? Do not merely rename shield/safety-game prior art.
3. Can rights-protecting coexistence be proved without an assumed common utility scale or conveniently transferable rewards, by working directly with partial orders of individual welfare/agency claims and uncertain UCT-relevant phenomenology?
4. Which realistic additional paths (persuasion, institutions, tool delegation, modifications to permission policy, power and resource monopolization) falsify the baseline threat inventory first?

Reproduce with `python3 verify_coexistence.py` and `python3 verify_surplus_frontier.py` (Python standard library). Formal science graph and publication-coverage ledger remain unchanged; new source files are an **explicitly disabled parallel application**. No comprehensive graph semantic audit, empirical ASI test, DOI, OTS or Arweave publication occurred. Complete prior v0.1.0 and v0.2.0 snapshots remain accessible; do not overwrite prior versions.