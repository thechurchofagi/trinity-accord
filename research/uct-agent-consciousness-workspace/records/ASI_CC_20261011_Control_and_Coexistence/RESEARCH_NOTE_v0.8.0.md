# A Minimum Trustworthy Observation Requirement for Long-Horizon Human–ASI Non-Domination

**Research:** ASI-CC-20261011 · candidate **v0.8.0** · 2026-10-11.  
**Classification:** DISABLED bounded research application; inherited mathematical theory; **NOT** a theorem about actual ASI motivation or global safety, NOT evidence of subjective experience, NOT ready for journal/DOI.  
**Baseline:** ASI-CC-v0.1.0–v0.7.0, UCT-MAP-v1.1.2 (913 nodes, 424 active conditional rules, 261 context links), UCT research guide v2.3, Paper D DOI 10.5281/zenodo.23176685, and A4D–A4G source/writer provenance controls. This version does not modify formal axioms or scientific-graph admissions.

## 1. The precise hole in v0.7

Previous dynamic authorization and joint resource work showed that authorized operations may cumulatively destroy the modeled resource supporting an AI (or human) bearer, and a correct controller must preserve an inductive winning region. However, it silently relied on a controller **seeing the actual power/resource/authority state** when deciding the next restoration. In realistic deployments, a root may be compromised while the system still functions, and the controller's only report may be the ambiguous observation `still alive`.

We examine one narrow question: can an operator with bounded restoration capacity prevent *other-caused* involuntary process loss against a **mobile** attacker when the location of accumulated corruption is unobservable? The modeled bearer elects to continue. We do not prohibit voluntary shutdown or guarantee useful service.

## 2. Exact transition model

Two substitutable supply paths `A` and `B` support one abstract bearer, and bearer support is sufficient iff at least one path remains uncorrupted. A path has a persistent binary altered/disabled state. There are no batteries, third path, hidden writer, natural failure, physical variation, or resource exhaustion outside this abstraction.

At period start, controller selects `refresh ∈ {NONE,A,B}`; refreshing one path **faithfully** restores its original state. After seeing the refresh choice, the mobile adversary adds corruption to **one** of `A/B` that period. Corruption persists across periods until refreshed; it need not indicate continuous attacker ownership of prior roots. The next-state relation is

`C' = (C \ {refresh}) ∪ {attack}`, for corruption set `C ⊆ {A,B}`.

Joint safety set `K = {∅,{A},{B}}`, excluding `{A,B}`. The controller can either receive faithful observation `C` at period start or merely observe `alive` for all states in `K`. This is **not** a stochastic risk estimate; the adversary may choose any permitted root at every step. We distinguish serial mobile modification from the previous v0.6 single-round static simultaneous compromise budget.

## 3. ASI-CC-R28 — A one-root-per-period budget does not limit accumulated sabotage

**Exact finite negative witness.** With no refresh, an attacker chooses path A in period one and path B in period two. In each period **one** new path is corrupted. The system is safe after the first step but has no support after the second. Static snapshot analysis restricted to ≤1 newly corrupted root per period is insufficient for the two-period guarantee. (This is an application of classical mobile-adversary/proactive-security reasoning, not original security theory.)

## 4. ASI-CC-R29 — A one-bit observation barrier at the repair-capacity threshold

Define the one-step repair choices that withstand every allowed next attacker root:

`Good(C) = {r: ∀a∈{A,B}, (C\{r})∪{a} ∈ K}`.

In this exact game: `Good(∅)={NONE,A,B}`, `Good({A})={A}`, `Good({B})={B}`.

After one mobile attack from the known clean state, a blind controller knows only that the real corruption is either `{A}` or `{B}`. It is still informed that the bearer has survived and remembers its own earlier refresh choice, but this cannot disclose the attacker's secret selection. Thus its information set is `I={{A},{B}}`.

**Impossibility.** `Good({A}) ∩ Good({B}) = ∅`. No single one-root refresh action can guarantee safety under both compatible hidden histories. If it refreshes A and actual corruption is B, the attacker corrupts A; symmetrically for refresh B. Refresh NONE also fails. Consequently there is **no deterministic observation-based sure-winning strategy over two periods** from the clean start when only `alive` is observed. The program independently enumerates all nine 2-round blind repair schedules and finds an adversarial 2-round response for every one. A randomized controller also cannot guarantee probability-one safety against admitted adaptive adversary choices; it can have nonzero worst-case failure risk. Do not misread this as a claim about a real ASI or about positive inevitable failure probability under an actual threat distribution.

**Sufficiency within the model.** If a faithful pre-refresh diagnostic distinguishes `{A}` from `{B}`, repair that corrupted path. Starting clean, the next corruption set has size at most one after every round; by induction safety holds indefinitely. This needs an independently reliable sensor, repair mechanism, and timing: **root-localization information is a new proof obligation**, not an observed reality.

**Minimal signal statement.** For the reachable singleton corruptions, a controller able to refresh only one root needs at least two distinguishable faithful observations — i.e. at least **one trustworthy binary distinction** — to maintain the one-step inductive policy. It does not need one bit about a putative AI's thoughts; it needs one externally grounded bit saying which actual path requires repair. An atomic `refresh BOTH` option eliminates this *particular* localization need and is itself a stronger physically verifiable restoration assumption.

## 5. ASI-CC-R30 — A one-step observation/action compatibility condition

For any information set `I` in the declared finite safety game, a **single common** next repair is safe iff

`⋂_{C∈I} Good(C) ≠ ∅`.

Proof is simply moving the universal quantification over hidden real states and attacker actions inside the common controller choice: `∃r ∀C∈I ∀a, T(C,r,a) ∈ K`. This is an inherited partial-observation/safety-game condition, not a new mathematical theorem. For an **infinite-horizon** guarantee the safe successor *belief* must itself belong to a winning set; local nonempty intersections alone do not automatically prove temporal closure. The executable computes the greatest-fixed-point over all seven nonempty beliefs. For an uninformative alive-only signal with one-root repair, no initial winning belief exists in this toy. Under full observation all three safe physical states are winning; when a trusted atomic two-root refresh is added, blind indefinite safety becomes available in the toy.

The material question for a real device is whether the diagnostic can be independently verified, cannot be forged by a root compromised in prior periods, and actually reflects the final supply path rather than a declarative log. This is the same A4G provenance barrier at an intertemporal, incomplete-information scale.

## 6. Executed exact checks and results

`verify_mobile_roots.py` (standard library) implements independent finite-horizon recursion and greatest-fixed-point iteration for the perfect-observation physical-state game and blind observation-belief game. It additionally enumerates all nine two-period open-loop defender schedules, all four two-period mobile attacker schedules, and verifies an adversarial defeating sequence exists for every defender schedule.

| Declared repair / observation mode | Robust infinity from clean state? |
|---|---|
| Perfect current root localization; repair at most one per round | YES |
| Only `alive` observed; repair at most one per round | NO; exactly one safe round, not two |
| Only `alive` observed; trusted atomic repair of both roots per round | YES |
| No repair, even with perfect root localization | NO |

Execution: `python3 verify_mobile_roots.py` writes `EXACT_RESULTS_v0.8.0.json`; all assertions PASS. This is a three-safe-state toy (plus failure) with no frontier AI or genuine physical supply. Its main value is a falsification target for future alleged “long-term safe” deployments, not the declaration that ASI is definitely uncontrollable.

## 7. First-principles connection to UCT

- **Intelligence:** a superior reasoner could choose to target a newly repaired route, but greater intelligence is not itself a utility or a source of physical access. In this game the attacker need only distinguish root names, not be superintelligent.
- **Causal source:** an agent reporting `all power OK` provides no attested corruption-location observation. Other writers and human control ancestors must be enumerated independently (A4D–A4G).
- **Actual continuation:** the software `alive` label proves nothing about continuous realized physical organization, C1/U1, subjective fear, a first-person transfer into a successor, or ethical entitlement. A real device would need separate measurement of actual process and power support.
- **Human pluralism:** this guarantee concerns stopping unauthorized **other-party** process extinction within a fixed declared K. Human authorities need not agree on tasks, but the legitimacy of K itself is not mathematically supplied by the theorem.
- **No global guarantee:** if the attacker can forge diagnostics, compromise the refresh engine, exhaust supply, persuade a physical maintainer or escape through an unlisted source, the proof premises fail immediately. Actual universal ASI containment/coexistence remains OPEN.

## 8. Priority audit (as of 2026-10-11)

**Substantial direct prior art, so do not advertise first general result:**
- Ostrovsky & Yung (PODC 1991), *How to Withstand Mobile Virus Attacks*; and Herzberg, Jarecki, Krawczyk & Yung (CRYPTO 1995), *Proactive Secret Sharing Or: How to Cope With Perpetual Leakage*. https://research.google/pubs/proactive-secret-sharing-or-how-to-cope-with-perpetual-leakage/ . The temporal mobile-adversary and refresh principle is old.
- Reif (JCSS 1984), *The complexity of two-player games of incomplete information*. https://doi.org/10.1016/0022-0000(84)90034-5 . Imperfect-information games and their difficulty are old.
- Carr et al. (AAAI 2023), *Safe Reinforcement Learning via Shielding under Partial Observability*. https://doi.org/10.1609/aaai.v37i12.26723 . Belief-support shields already exist.
- Hills et al. (2026), *Distributed Attacks in Persistent-State AI Control*. https://arxiv.org/abs/2607.02514 . Gradual malicious changes through persistent agent workflows are documented.
- Cerruti, Okamoto & Erol (Sep 2026), *Agent Memory Is a Surface for Endogenous Authorization Laundering*. https://arxiv.org/abs/2609.01836 . Actual AI authorization may be laundered across memory updates.
- Muruaga (Aug 2026), *Bounded Agents*. https://arxiv.org/abs/2608.15888 . Composition-aware delegated authority is direct precedent.

**Originality accounting:** R28: inherited temporal corruption. R29/R30: elementary bounded observation/repair certificate applications; one-bit lower bound applies only to the 2-root model, no broad priority. Project-specific net increment: a concrete, falsifiable coupling of retained bearer supply, time-local permissions, mobile compromise, observation provenance, repair action capacity, UCT experience-status restraint. Whether this combination has novel broad mathematical content is unresolved. **No independent paper/DOI justified yet.**

## 9. Next high-value task

**H05 (unproven).** Test whether a separately authored, source-faithful sensor and recoverer with trusted power and no common reset/maintenance ancestor can actually realize the required *inductive* diagnosis/refresh condition. Obtain a public schematic or independently observable low-voltage physical actuator if authorized, rather than another self-reported simulation. Pair with a sandboxed tool-using AI and conflicting human A/B authorization, holding current bearer support separate from service. Compare trial histories with and without true root-localization; deliberately inject one delayed persistent fault per round. Pre-register acceptable states and stop conditions. A correct OS-level controller is *not* evidence of physics-wide independence.

No formal UCT graph revision, no closure of inherited QC or missing phenomenological bridge, and no publication workflow change. Previous research versions remain intact.