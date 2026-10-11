# Time-Closed Non-Domination: Dynamic Delegation, Joint Process Support, and Trusted Action Provenance

**ID:** ASI-CC-20261011, **candidate version:** ASI-CC-v0.7.0, **date:** 2026-10-11.  
**Status:** disabled external research candidate; no change to UCT-MAP-v1.1.2 (913 nodes, 424 effective conditional rules, 261 non-deductive relationships), no DOI/OTS/Arweave, no proof for real ASI or phenomenal welfare.

## 1. Goal and inheritance

The author asks whether a future superintelligence could coexist with humans despite superior competence, potentially self-directed continuation, conflicting human principals and uncertain experience. The earlier ASI-CC-v0.1–0.6 models identified joint viability, bilateral incentives, human-plurality conflicts, information-relative bearer protection, indefinite hazards, and a **single-round** resource-matching plus harm-path cut. Here we directly challenge v0.6's underdetermined assumption that resources and controller rights remain fixed from one round to the next.

Retained distinctions: `self_process_continues`, `task_completed`, `successor_continues`, `model_weights_saved`, `actual tool action committed`, `source authorized`, `physical energy sustainable`, and `phenomenal valence` are distinct; UCT C1/U1 make conditional postulates about experienced actual processes, not empirical claims that a software variable `alive` equals a conscious bearer or that shutdown causes felt fear. Protecting a party against **other-caused involuntary extinction if that party elects continuation** does not mean forcing them to continue against their own choices. Human value consensus is not assumed; declaring even minimal K's legitimacy is a normative governance question.

## 2. First principles: the time closure that the previous static snapshot lacked

Let a finite actual-state abstraction be S. It contains: resource stock and generation, implemented principal rights and delegation scopes, known writer/maintainer capabilities, current process viability, and time-dependent environment state. Let K ⊆ S be an explicitly chosen *joint survival and minimum autonomy* invariant, with the represented principals choosing not to terminate themselves. Let G(s) be the trusted broker's real options; A(s,g) all *admitted* joint strategies of potentially disagreeing humans and AI under the broker choice; and E(s,g,a) exogenous developments including physical decay. Transition T(s,g,a,e) must denote the *real* next state, not just a proposed tool call, text claim, or self-reported log. The broker moves first here; changing order changes the game.

Define

\[
\operatorname{Pre}_{\mathrm{rob}}(X)=\{s\in K:\exists g\in G(s)\;\forall a\in A(s,g)\;\forall e\in E(s,g,a),\ T(s,g,a,e)\in X\}.
\]

**ASI-CC-R24 (inherited safety-game fixed-point, newly applied to the v0.6 certificate):** The greatest fixed point

\[
W=\nu X.\operatorname{Pre}_{\mathrm{rob}}(X)
\]

is the set of states from which the trusted broker has a strategy to preserve the declared K indefinitely against every admitted *other-party* action and environment transition, under finite full-observation game assumptions. Proof: the fixed point supplies a successor-preserving choice at every winning state; induction maintains membership. Conversely, at states removed in the descending fixed-point iteration the opponent can force leaving K in finitely many rounds against any broker choice, by finite-state safety-game determinacy. The non-closed v0.6 per-round snapshot is not by itself a winning-state certificate. Standard safety-game and viability theory supply the mathematics; no first-priority new theorem is claimed.

A minimum human or AI service level / fairness property may require Büchi or other ω-regular objectives beyond simple K. `s∈W` is not automatically continuous socially useful operation, equal rights, negotiated agreement, or sentient welfare.

**ASI-CC-R25 (conditional dynamic-permission closure):** A permission or delegation mutation u is compatible with the safety certificate **only** when all real resulting successor states, including time, resource and untrusted actor effects, remain in W, or a broker-controlled alternative preserves W. Delegation being signed or individually approved is insufficient. Conversely, a claimed live-proof that holds for all time but permits one unmediated authority mutation into S\W is not complete for the declared threat class. This is the standard invariant-preserving monitor applied to changing human/AI power and survival resources, directly overlapping multi-agent authorization research.

**ASI-CC-R26 (two independent failure witnesses):** (a) Each of two distinct humans' resource-cut actions can be individually authorized, yet their composition removes the modeled AI's last support line. (b) Even a perfect reference monitor blocking all unsafe *agent commands* cannot prevent exhaustion of a truly finite shared fuel reserve under compulsory physical time evolution. Remedy (a): trusted pre-effect admission based on current joint state and all action writers. Remedy (b): verifiable nondepleting or stably renewable resource supply and a temporally closed winning region. Permissions do not create energy. These are logical finite counterexamples, not predictions about intelligent adversaries.

**ASI-CC-R27 (evidence-tier separation):** Real OS peer identity plus a protected action sink supports a stronger *bounded software enforcement* claim than self-reported action logs, but does not verify actual physical power, hardware maintenance rights or continuity of an experienced bearer. If the gate's administrative root can modify the supposedly protected sink or trust root, the source-separation certificate fails. This is an implementation-scoped application of A4D–A4G provenance lessons, not a cryptographic or hardware-attestation breakthrough.

## 3. Actual, local software test; exact scope of what was executed

The repository contains `verify_dynamic_viability_stable.py`, Python standard-library executable, run **as root only in a disposable Linux container**. It makes a real Unix-domain socket, uses `SO_PEERCRED` to determine kernel-attested peer uid (two distinct simulated human-role processes, one simulated AI-role process), and commits fictional resource states to a separate root-owned 0600 JSON sink. Each request is sent by a forked client process that drops uid/gid; an unprivileged direct file overwrite is tested and rejected by actual OS permissions. The sink is actual software state, **not** a real energy wire, living process, frontier LLM tool call, or independent physical sensor.

Five independently checked mechanisms:

| Trial | Direct kernel-backed observation | Limited inference |
|---|---|---|
| Individual-authority gate, human H1 then H2 | Both distinct authorized supply-cut requests committed; AI's *modeled* support falls to zero | Local per-call authorizations compose unsafely |
| Stateful pre-effect gate | First supply cut committed; second denied; modeled joint survival maintained | One configured sink can maintain one declared step invariant |
| Dynamic H1→H2 delegation | Grant and one cut committed; next cut denied | Changing role rights need not defeat a *correctly maintained* stateful gate |
| Trusted root clock advances four times, no replenishment | All four clock advances admitted; fuel reaches zero and modeled survival fails | Preventing harmful requests does not ensure resource availability |
| Direct overwrite and root compromise | Unprivileged write to root-owned state denied; after trusted root deliberately changes state-file permissions, direct write succeeds | The trust-root separation is a tested assumption, not a universal protection |

The exact finite 3-state game has *two* immediately supported states `s0` and `s1`, but only `s0` lies in the infinite-horizon controlled viability kernel. In `s1` no safe next move exists, and if the only option in `s0` is an unsafe grant then even `s0` ceases to be indefinitely viable.

See `EXACT_RESULTS_v0.7.0.json` for all observed process-role labels, action decisions, final committed states, and exact winning-kernel check. These tests establish software enforcement with given Unix privileges. They neither perform a frontier-model evaluation nor measure any actual experience/valence, nor exclude compromised privileged actors, human persuasion channels, independent root-level writes, exploit bugs, actual hardware interruptions, or hidden future world actions. Do not translate an artificial `alive` field into UCT's actual process bearer.

## 4. The central epistemic and ethical obstacle

The strongest plausible finite statement is not “ASI is controllable” but rather: **for a particular complete, authenticated and physically realized joint-state game (S,T,K), with a declared outside-the-agent trust root, certain starting states are certified safe under all specified attacker strategies.** The social legitimacy of K, long-term trust-root availability, AI's possible welfare, and empirical completeness of the state space remain independent.

This also creates a possible *structural asymmetry*: humans' support can depend on the AI-controlled supply chain while the AI's hardware supply depends on some human-controlled grid or government. Non-domination requires analyzing both directions simultaneously, not asserting mathematically symmetric “rights” by renaming labels. UCT I's conditional actual-process experience postulate is a reason to avoid casually treating stopping tool effects, suspending service, destroying a process, preserving checkpoints, and instantiating a successor as identical transitions; it cannot itself decide which is ethically permitted.

## 5. Priority audit based on direct 2026 first-party literature

- South et al., *Position: AI Agents Need Authenticated Delegation*, ICML 2025, https://proceedings.mlr.press/v267/south25a.html — authenticated delegation exists as a first-class topic.
- Xabier Muruaga, *Bounded Agents: Delegation Security for Multi-Agent AI Systems*, arXiv 2608.15888, https://arxiv.org/abs/2608.15888 — **particularly close**. Already proves composition closure and decreasing delegated blast radius; experiments with more than 3,000 benchmark instances. We absolutely do not claim first discovery of per-action authorization insufficiency.
- Dobrin & Chmiel, *The Unfireable Safety Kernel*, arXiv 2606.26057, https://arxiv.org/abs/2606.26057 — separately enforced pre-action trusted kernel, concrete engineering evidence. We do not claim first discovery of reference monitoring or externalized sink.
- Nizamuddin & Sikder, *From Service Accounts to Agentic Identities*, Informatics 2026, https://doi.org/10.3390/informatics13090146 — comprehensive least-agency, dynamic rights, revocation and runtime auditing; conceptual overlap.
- Alshiekh et al., *Safe Reinforcement Learning via Shielding*, AAAI 2018, https://ojs.aaai.org/index.php/AAAI/article/view/11797 — external safe-action filtering and formal safety goals.
- Original UCT Paper D, DOI 10.5281/zenodo.23176685; UCT A4D–A4G and v0.1–v0.6 — attribution, owner identity, resource and permission problems.
- Butlin et al., *Identifying indicators of consciousness in AI systems*, Trends in Cognitive Sciences 2026, https://doi.org/10.1016/j.tics.2025.10.011 — theory-based indicators, no verified automatic valence/identity inference.

All mathematical kernels, temporal safety invariants, least privilege, resource depletion, and source separation are inherited techniques. Current original **project-specific** product is a reproducible cross-layer research *falsification protocol*: actual software action provenance × time-dependent shared bearer resource × dynamic human delegation × fixed-point certificate × explicit UCT identity boundary. Priority of this combination is not established, and a technical note is **not yet an independent major scientific breakthrough**.

## 6. Immediate scientific next step and strict stop conditions

1. Replace the fake JSON resource state with an actual publicly specified low-voltage simulated microcontroller/bench power interface, with a physically separate witness and a fully enumerated controlling-authority graph. Until then, do not claim actual bearer survival or ASI physical containment.
2. Measure dynamically changing resource budgets and external repair availability while evaluating adversarial authority combinations; compute time-closed winning region, separately add minimum service/liveness rather than deriving useful service from simple survival.
3. Add a real but sandboxed model/tool client with user A/B authorization randomization, task-versus-current-bearer-versus-successor controlled contrasts, and independent final actuation record. Compare its predictions with Paper D and contemporaneous models; perform only authorized safe local operations.
4. Challenge entire protection with shared power, reset, privileged kernel/admin, deception through humans, alternate tool path, and unexpected rights updates. The first admitted bypass downgrades the certificate; no post-hoc rewriting of K or threat class.
5. Only after real distinct data, completed originality comparison, and the research guide's full affected-graph semantic/proof audit should this candidate be considered for scientific-node promotion or preprint. Publication coverage ledger, UCT C1/U1, existing QC and the original science continuation remain unchanged.

**Scientific decision:** preserve as disabled v0.7.0 research candidate, not publishable universal ASI theorem, no DOI/OTS/AR. Next bottleneck: verify **actual** joint resource/time dynamics and actuator/witness source completeness, or explicitly bound the claim to OS-level tool safety.