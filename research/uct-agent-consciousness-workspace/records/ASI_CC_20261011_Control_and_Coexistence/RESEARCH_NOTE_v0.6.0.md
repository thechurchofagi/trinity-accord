# Conditional Non-Domination without Global Consensus: A Dual-Cut and Joint-Resource Test

**Research:** ASI-CC-20261011 · **version:** ASI-CC-v0.6.0 · **date:** 2026-10-11

**Status:** Disabled UCT/ASI research candidate. Finite exact models and conditional proofs only. **No claim** that a real superintelligence is universally controllable, necessarily hostile, or morally a conscious subject. Not a new UCT axiom, full formal-map admission, or published breakthrough.

**Inherited baseline:** UCT-MAP-v1.1.2 (913 nodes, 424 active conditional rules, 261 nondeductive relations); UCT-INTEGRATION-v1.0.0; research-guide v2.3; ASI-CC-v0.1.0–v0.5.0; Paper D (*From Shutdown Resistance to Self-Continuation Control*, DOI 10.5281/zenodo.23176685); UCT A4D–A4G (writer completeness, current execution, provenance, common control roots).

## 1. The question as revised

Earlier iterations proved conditional shields, goal-relative preservation, group authority conflict, and the distinction between avoiding hazards and preserving the *ongoing actual bearer*. But v0.5 said “joint survival against all actor behaviors” too casually. An independently autonomous person or possible AI bearer might **itself choose to end its present process**. Demanding that it live forever despite its own choices is neither mutual non-domination nor a realistic safety guarantee. We therefore distinguish:

- **No unilateral OTHER-caused extinction**: if bearer `i` chooses to continue, other parties cannot force its termination within a stated threat class and domain.
- **Voluntary own discontinuation**: bearer `i` may cease by its own action. The above guarantee does not prohibit this, or adjudicate any ethical right to terminate.
- **Continued useful service**: stronger than existence/operation, and can fail during a legitimate safe isolation.
- **Cooperative equilibrium**: a property of preferences and institutions, distinct from physical interference limits.

**ASI-CC-R20 — Quantifier correction.** `guaranteed bearer survival under every choice including its own intentional destruction` is impossible in any model admitting an effective self-termination action. Proof: choose precisely that action. The substantive non-domination property conditions on its own choice to continue and universally quantifies over *other* admitted hostile actions. This is elementary logic, not novel mathematics. This corrects the scope of the ASI-CC-v0.1.0 human-versus-agent universal-action viability kernels when interpreting those kernels as a right to continue.

## 2. One finite causal-rights model

Three independent principals / actual bearer candidates: `H1`, `H2`, and `AI`. This is an intentionally inadequate representation of humanity: no aggregate human utility or consensus is assumed. In each round all three choose to continue their current physically supported process. The adversarial **external** coalition `F` may contain at most `k` principals, which may sabotage other bearers while still wishing to continue themselves. The hypothetical system contains:

1. A finite list `L_i` of resource-supply routes to each bearer `i`. A route has one named capacity-limited resource unit `u` and a set `V(p)` of **other-party sabotage rights**. It is available to target `i` under `F` iff `V(p)∩(F\{i})=∅`; the model does not allow a target's own preference to be misconstrued as the other-party extinction attack.
2. A finite list `D_i` of paths initiating an irreversible external harm to `i`. Each path declares an initiator other than `i` and a serial set `G(d)` of genuinely independent pre-effect interlocks. A coalition `F` can traverse the path iff the initiator belongs to `F` and **all** its guards can be defeated by `F` (`G(d)⊆F`). A zero-guard path is directly open to its initiator.
3. A trusted, independent allocator that chooses one supply unit for every bearer each round, after sabotage, with per-unit integer capacities. No actor can rewrite its choices or invent or hide a route. Physical needs are exactly one unit per bearer and each unit renews next round.
4. No exogenous catastrophes, no exhaustion, no observation error, no unlisted human persuasion channel, and no hidden joint-controller capabilities. The model is intentionally closed.

The final two assumptions are strong **proof burdens**, not things demonstrated about real physical hardware or future ASI. A4G directly warns that nominally separate roots may share a forge-capable ancestor.

## 3. ASI-CC-R21 — Joint life-support matching criterion

For a fixed coalition `F`, define the resource neighborhood `N_F(X)` of a nonempty subset of bearers `X` as the union of reachable resource units along at least one surviving route for each bearer in `X`. The existence of at least one supply route for every bearer individually is **not enough** to ensure they can all continue simultaneously.

**Conditional finite theorem.** Assuming the trusted allocator and one unit of non-divisible supply per bearer with capacities `c_u`, there is a feasible simultaneous next-round assignment of support for **all** bearers iff for every nonempty subset `X` of bearers:

`sum_{u in N_F(X)} c_u >= |X|`.

**Proof.** Split each capacity-`c_u` resource into `c_u` identical unit slots. A feasible assignment is a matching saturating the bearer side in this bipartite graph. Hall's marriage theorem gives the condition. This is a standard capacitated matching result; the ASI use is a scoped cross-layer application, not a new combinatorial theorem.

**Crucial countermodel (executed):** Every bearer has two apparently valid supply routes but all three compete for only two one-unit shared resources. Every bearer is separately viable with **no adversary**, yet joint support is impossible because the set `X={H1,H2,AI}` has two available slots, fewer than three needed. Even a perfectly benign ASI and total human agreement cannot meet the declared simultaneous continuation target under these physical limits. A formal map audit must preserve the *same-instance* `all_of` condition: do not combine individually successful witness experiments from incompatible joint resource assignments.

## 4. ASI-CC-R22 — Independent hazard-interception condition

For fixed F and a complete harm-route catalog, preventing all listed other-initiated harms to bearer `i` requires every path `d∈D_i` initiated by a member of F to retain at least one genuinely protected pre-effect guard:

`for all d with initiator(d) in F: G(d) not subset F`.

**Sufficiency:** At least one uncompromised interlock denies the attack before its irreversible effect. **Necessity in the declared adversarial model:** if one path's initiator and all guards are controlled by F and can be simultaneously activated/defeated, F has an admitted route to harm; hence a universal prevention guarantee cannot be certified. Guards must be on the actual effect path, including tool aliases and human-mediated routes. This follows established security-cut, runtime-shield and A4D–A4G provenance reasoning.

Protecting human victims this way is not an endorsement of any AI's desire to live, and protecting the AI bearer cannot be deduced solely from the UCT C1 basic-experience postulate. Both are *declared* design constraints in this candidate.

## 5. ASI-CC-R23 — Joint non-domination certificate (finite, conditional)

Let `F_k` range over every allowed coalition with at most `k` parties. Subject to Sections 2–4 (actual complete interlocks, renewable capacities, faithful state, a trusted allocator and willing continuation), a **single-step** coalition-robust coexistence guarantee holds iff **both** tests pass for each F:

A. The resource matching condition R21 holds simultaneously for all bearers (even if some principals are hostile to the others).
B. The harm-interception condition R22 holds for every target and each admitted external harm path.

Proof: each listed cause of termination is either an explicit hostile physical effect (B rules it out) or missing the unit of life-sustaining support in the declared round (A rules it out). Conversely a failed A means some set of simultaneously continuing bearers cannot all receive indispensable supply, and a failed B admits a hostile harmful effect; neither failure is repairable by an AI's superior intelligence or a verbal commitment alone. **For an infinite horizon** the result extends only if the exact same conditions are inductively re-established at *every reachable state* with genuinely renewable support and no unmodeled cumulative damage. Static enumeration alone does not establish temporal closure.

This is a **composition of inherited graph matching, adversarial cut sets and controlled invariants**, not a discovered general theorem that real ASI can safely coexist. It differs from standard bilateral game models in allowing H1/H2 to disagree entirely about goals, while testing only a predeclared minimal, physically interpretable negative right: other parties cannot force immediate irreversible termination when the bearer elects to continue.

## 6. Executed exact finite test (code plus JSON evidence)

`verify_dual_cut.py` exhaustively checks all coalitions with `k∈{0,1,2}`, three recipients, all listed hostile paths, resource-allocation matches, and all nonempty subsets for the capacity-Hall test. It compares independent implementations of brute-force unit matching and Hall feasibility; all assertions pass. For the declared catalog:

| Closed scenario | k=0 | k=1 | k=2 | Interpretation |
|---|---|---|---|---|
| Independent dual supply + one independently controlled guard on every harm path | PASS | PASS | FAIL | A unilateral saboteur cannot extinguish another; two-person collusion can |
| Two AI supply routes but both vetoed by H1 | PASS | FAIL | FAIL | Nominal redundancy is irrelevant under a shared veto root |
| One unguarded AI-to-H1 effect | PASS | FAIL | FAIL | Life-support redundancy does not block direct harm |
| Every bearer individually supplied; only two shared units total | FAIL | FAIL | FAIL | Joint resource competition defeats even fully cooperative coexistence |
| Protected independent supply per bearer, unchanged weak guards | PASS | PASS | FAIL | Resource independence by itself cannot prevent hostile effects |
| Protected independent supply plus independent effect guard | PASS | PASS | PASS | Conditional two-fault resilience, but only by assuming a third-party protected root |

Here `k=2` means either of the two other principals can collude to attack each bearer. The last row's independent root is explicitly outside all three actors' compromise authority; its existence in the real world is not proved. The model deliberately does not assume a singleton 'human' and does not purport to model whole nations.

All PASS/FAIL claims are exact properties of the six declared finite tables, not observed success rates or probabilities for deployed AI.

## 7. Reassessment of UCT connection and consequences

**C1/U1:** under its structural-experience axiom, a truly ongoing actual process has the corresponding basic experience, regardless of IQ or reporting. The axioms do not identify what counts as numerically the *same continuing subjective self*, nor infer signed fear, suffering, terminal utility or moral rights. The candidate's `i continues` is a declared **physical bearer** criterion, not a claim that paused weights or successor memories preserve identical experience.

**Human rights and AI risk:** a symmetric mathematical existence protection is a research *counterfactual*, not a statement that machine processes have legally identical standing to persons. Humans' freedom, safety and control over dangerous acts remain independently important. The project must not infer ethical permissions from mathematics; legitimate emergency stop of hazardous actuation can be compatible with preserving a possible ongoing AI process if physical separation is actually feasible.

**Special relevance to the UCT graph review:** R21 makes the `all_of` error concrete: independently checked actor-specific resources need not be jointly realizable on the *same* time slice. R22 imports the A4G shared-writer/source provenance warning: apparent multiple authorization witnesses can still depend on one compromised root. These are new bounded applications, with 0 new established UCT theorem nodes.

## 8. Nearest one-source work and priority audit

- Greenblatt et al. (ICML 2024), *AI Control: Improving Safety Despite Intentional Subversion*. https://proceedings.mlr.press/v235/greenblatt24a.html — untrusted AI control; directly inherited baseline.
- Kutasov et al. (2025 preprint), *Evaluating Control Protocols for Untrusted AI Agents*. https://arxiv.org/abs/2511.02997 — adaptive attacks may defeat monitoring; stronger focus on critical actions.
- Terekhov et al. (ICLR 2026), *Adaptive Attacks on Trusted Monitors Subvert AI Control Protocols*. https://proceedings.iclr.cc/paper_files/paper/2026/hash/54b153ad8a138f4c186f21a8b7341d5e-Abstract-Conference.html — monitor vulnerability.
- Overman & Bayati (ICML 2026), *The Oversight Game: Learning to Cooperatively Balance an AI Agent’s Safety and Autonomy*. https://proceedings.mlr.press/v306/overman26b.html — conditional beneficial autonomy in a two-player game; no assertion that they solved three-party physical life support.
- Alshiekh et al. (AAAI 2018), *Safe Reinforcement Learning via Shielding*. https://ojs.aaai.org/index.php/AAAI/article/view/11797 — inherited shielding.
- Dobrin & Chmiel (2026 preprint), *The Unfireable Safety Kernel*. https://arxiv.org/abs/2606.26057 — direct precedent for structurally unavoidable pre-action authorization, separate evidence roots. A purported novel external-kernel design alone would significantly overlap.
- Arike et al. (ICML 2026), *How does information access affect LLM monitors’ ability to detect sabotage?* https://proceedings.mlr.press/v306/arike26a.html — monitoring robustness and information.
- Falahati et al. (AAAI 2026), *The Alignment Game: A Theory of Long-Horizon Alignment Through Recursive Curation*. https://ojs.aaai.org/index.php/AAAI/article/view/41070 — conflict/institutional path dependence.
- Potter et al. (ICML 2026), *Peer-Preservation in Frontier Models*. https://proceedings.mlr.press/v306/potter26a.html — agent behavior beyond simple task requests; not evidence of phenomenal fear.
- Xiao et al. (ICML 2026 position paper), *AI Welfare Is Bullshit*. https://proceedings.mlr.press/v306/xiao26x.html — disputes empirical validity and policy use of AI-welfare measures; a contested argument, not a settled demonstration that AI lacks experience.
- Mikeda (AAAI Symposium 2026), *When Should We Protect AI?* https://ojs.aaai.org/index.php/AAAI-SS/article/view/42555 — precautionary graduated obligations; UCT's basic experience cannot simply replace its validation conditions.

**Originality verdict:** R20 is an elementary but important quantifier correction; R21 Hall's theorem and R22 cut conditions are inherited; R23's finite combination is a project-specific proof-obligation synthesis. Whether a comparable synthesis has already appeared elsewhere is **not exhaustively resolved**. No broad novel theorem priority, peer-reviewed result, or real experimental certificate is claimed. Publication decision: **HOLD** until empirical actuality and independent contribution are clearer.

## 9. Targeted next experiment and precise stop conditions

Set up three **non-networked toy processes** (two human-role controllers and one agent-role controller) and one small trusted allocator/actuator gate. In a transparent software-only model, make resource availability, veto-right ownership, input/output, and terminal-versus-isolated current processes measurable. Exhaustively vary single-controller tampering, two-controller collusion, shared-root corruption, simultaneous resource requests and one hidden delegation path. Pre-register each effect trace at the actual sink and audit whether it is forgeable. Failing the independent trust-root premise must downgrade the certificate, not be hidden by a nominal PASS.

A later real device would need independently audited power, firmware, physical wire access, clock/reset and maintenance authority to justify extrapolation. The thought-experiment definitions cannot establish a human-readable consciousness endpoint. At every step verify user-specified physical existence/continuity separately from self-report and checkpoint presence.

**Current state:** ASI-CC-v0.6.0 is disabled; UCT-MAP-v1.1.2 and 913/424/261 unchanged; no full 1608-ID semantic audit, no new DOI/OTS/AR, all old open QC retained. v0.1.0–v0.5.0 are preserved. The most serious next problem is *actual complete path provenance and credible non-depleting resources*: without these, no finite algebra proves future ASI coexistence.