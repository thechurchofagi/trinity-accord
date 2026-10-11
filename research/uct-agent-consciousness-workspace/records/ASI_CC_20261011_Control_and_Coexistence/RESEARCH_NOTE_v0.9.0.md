# Multi-ASI and Intra-Model Agent Multiplicity: Control Roots, Shared Failure, and Actual Process Boundaries

**Research ID:** ASI-CC-20261011. **Candidate:** ASI-CC-v0.9.0. **Date:** 2026-10-11. **Status:** DISABLED RESEARCH CANDIDATE; not a new UCT axiom, not an admitted full-map theorem, and not an empirical frontier-ASI finding.

## 0. Why this branch is necessary

The author correctly objects to an implicit one-human-vs-one-ASI picture. There can be many independent powerful models, many concurrently operating agent loops per model, cross-provider collaborations, heterogeneous objectives, shared weights, hosted inference and tools, and independent or shared human controllers. No unique global AI agent, human principal, control root, runtime, or experiential subject can be presumed.

Inherits UCT-MAP-v1.1.2 (913 formal nodes, 424 active conditional rules, 261 non-deductive links), ASI-CC v0.1.0–v0.8.0, Paper D DOI 10.5281/zenodo.23176685, UCT A4D–A4G. Old claims remain unchanged. No full UCT graph semantic admission/audit was completed.

## 1. Typed multiplicity map, not one inflated `agent_count`

A system description must separately represent:

- `M`: foundation/weight families (shared parameters are not identities of subjective subjects).
- `R`: physical inference runtimes, processes, hardware hosts and their actual time slices.
- `A`: agent loops/session identities, messages and task memories (potentially many-to-one onto M or R).
- `C`: actual tools, source credentials and actuator-authority certificates.
- `U`: all admitted control ancestors, including administrator, provider, maintenance, shared power/clock/reset, human delegation and colluding principal coalitions.
- `B`: *declared protected actual process-bearer candidates*, determined by a separately auditable spatiotemporal physical signature, NOT by counting agents, weights or prompts.
- `H`: different human operators/institutions; `E`: energy and compute provision; `T`: real effect/authorization sinks.

The mappings `A→M`, `A→R`, `A→C`, and causal ancestors `C←U` need not be injective. Even `B` cannot automatically be taken as equal to `R`: actual causal processes can overlap, nest or be interrupted, and UCT C1/U1 do not provide an empirical subject-counting algorithm. The typed map records competing choices of physical partition/temporal grain rather than silently imposing one.

### ASI-CC-R28 — Agent count does not supply independent authority (bounded Sybil counterexample)

In a toy approval protocol requiring two distinct agent identities and permitting costless identity creation within one effective controller, a single controller can generate two distinct IDs and pass the test without acquiring any independent authorization root. Proof: create a second ID with the same accepted controller; cardinality over identity labels increases from one to two but controller count remains one. A root-aware predicate requiring two unforgeable, mutually independent controllers rejects both votes. This is standard Sybil/authorization logic, not new theorem priority.

**Important:** independence is relative to a declared threat family, not a label. Two distinct cryptographic keys under a common administrator or common forge/replay root do not provide two independent decision authorities against that ancestor.

### ASI-CC-R29 — Two incompatible notions of independence (exact finite witness)

A pair can have different base models while sharing actual administrators; it can also have the same base model but distinct authority roots. Therefore:

`different model weights ⊬ independent authorization` and `independent authorization ⊬ independent model/epistemic errors`.

Our six-agent mock table has model groups of sizes four and two; three runtime backends; three credential roots and two administered roots. Among all 15 agent-ID pairs, all 15 pass a two-ID rule, 8 pass different-model checking, 9 pass credential-root checking, and 5 pass two-distinct-admin checking. Among the eight cross-model pairs, six share an admin root. Three same-model pairs have distinct admin roots. An example A1/B1 uses two different model families and two separate credential keys but is ultimately governed by U; A1/A4 shares a foundation model but is administered by U/V.

This is a declared access-capability table. It does NOT observe intentional collusion, establish that different model weights cause independence, or show a real hardware trust-root boundary. A higher common ancestor would defeat the last distinction too.

### ASI-CC-R30 — Multiplicity can amplify correlated errors (toy exact probabilities)

A deliberately invented binary failure model gives every independent failure root a probability `q=1/10` of error. Six truly independent agent errors would give `P(all six wrong)=q^6=1/1000000` and `P(at least four wrong)=127/100000`. But if all four agents sharing foundation family W0 fail together when that model family fails, and both foundation family events are independent with probability `q`, then `P(all six wrong)=q²=1/100` and `P(at least four wrong)=q=1/10`. If one common provider is sufficient to affect all six, `P(all six wrong)=q`.

The large difference is caused by *assumed dependency structures*, not by a measured AI failure rate. Shared foundation models need not have fully correlated errors, and distinct weights can share the same retrieved evidence, reward incentives, tools or administrators. It follows only that naive independence calculations are unjustified without independent error-provenance evidence. This overlaps the 2026 epistemic-Sybil and international safety report literature.

### ASI-CC-R31 — Resource counting must match the actual protected physical target

In the same declared table, six task/agent sessions map onto three computational service runtimes. Under a toy capacity of three independent support units, a design promising minimum continued operation of **three declared runtimes** fits, whereas a design requiring an independently supported *separate process per each of six agents* does not. Counting two model-weight families would undercount deployed runtime support; counting six agent labels would overcount if service truly has only three already-supported runtimes at the chosen temporal grain.

Neither result decides UCT's number of actual experiences, numerical subjective identity, valence, suffering, rights or welfare. Sessions' memory/storage may themselves instantiate physical processes omitted by this simplified resource metric. Service availability must not be conflated with current actual process continuity.

### ASI-CC-R32 — Coalitional non-domination requires *joint* authorization and process/resource closure (conditional schema)

Let `P` be a specified set of human principals and actual AI decision/control principals, `F ⊆ P\{b}` an admitted coalition of others, `K` the declared survival/non-domination constraint for all protected willing-to-continue physical bearers `b ∈ B`, and `T` the actual finite state evolution including agent spawn/merge, credentials, memory, tools, resource supply, delegation, and physical paths. Let `G(s)` be trusted broker choices.

A *bounded conditional* robust winning set is

`W = νX . { s∈K : ∃g∈G(s) ∀F∈𝓕(s) ∀a_F,e,  T(s,g,a_F,e)∈X }`,

where quantifier order and legitimate own decisions must be specified. The standard safety-game fixed-point argument proves invariance for states in W **only** if the transition relation accounts for every admitted real coalition and environment successor. Multiple agents using the same authority do not count as independent defenders; different AIs with different authorities can nevertheless voluntarily or strategically ally. No universal statement about the incentives of future superintelligences follows. This inherits v0.6 resource/cut criteria and v0.7–v0.8 time closure and partial observation: the present contribution is typing the population and coalition structure rather than proving a brand-new theorem.

### ASI-CC-R33 — Identity refinement must not silently change the authority certificate (scope-conditional diagnostic)

Clone one surface agent ID into two IDs, holding fixed their actual controlling roots, complete effect rights, and the physical transition opportunities relevant to the **authorization** check. A properly root-based authorization independence predicate remains unchanged; a naive ID-quorum predicate can change. This is a useful falsification test for superficial safety claims. However **it is NOT a general invariance of physical coexistence or UCT experience**: creating a new actual running process or increased tool throughput can genuinely alter resources, actions and experiences, and therefore changes the appropriate physical state model.

## 2. Exact executable audit (performed)

Run `python3 verify_multi_asi_multiplicity.py` in standard Python; it only evaluates mock authorization decisions and fixed combinatorial/probabilistic models. No external API, cyber exploitation, actual tool permission or LLM call occurs. The script uses rational arithmetic and records all 15 pairs and 11 identity-spawning scenarios, verifies the two-level provenance examples, computes 3 resource-demand interpretations and four correlated-fault quantities, and writes `EXACT_RESULTS_v0.9.0.json`. Every active assertion passes after correcting a development-time miscount of cross-model/same-admin pairs (actual count SIX, not seven); the corrected source and final output are saved.

| Synthetic metric | Result |
|---|---:|
| Agent sessions / weight families / backed runtimes | 6 / 2 / 3 |
| Credential roots / common administered roots | 3 / 2 |
| Candidate agent pairs | 15 |
| Accepted pairs under ID quorum / different model / different credential / different administrator | 15 / 8 / 9 / 5 |
| Cross-model pairs with the same administrator | 6 |
| Same-model pairs with different administrators | 3 |
| `P(≥4 errors)`, independent six-agent toy | 127/100000 |
| `P(≥4 errors)`, perfectly W0-correlated toy | 1/10 |

## 3. What is genuinely open and what should be tested next

1. Obtain *independent actual execution provenance* for a multi-model tool sandbox: record base model ID, process boundary, agent-loop ID, delegation credential, administrator/root, real protected sink and all higher ancestors. Stop if an actor can forge any required origin coordinate.
2. Inject controlled task errors and harmless unauthorized *mock* action requests while varying: (a) two copies of one foundation model, (b) two different models under one administrator, (c) one foundation model deployed under separate independent authorities, and (d) two models under independent authorities but a shared evidence source. Measure error correlations and whether one controller can acquire apparent quorum.
3. Cross independently configurable **principal collaboration** vs shared model memory/weight ancestry. Keep task consequences and actual effect rights stable; never claim a coalition's motives from an identical output alone.
4. Vary process granularity and physical continuities under shared-backing inference, parallel independent processes, handoff, fork, pause, and migration; UCT-specific phenomenology remains OPEN until a defensible independent bridge exists.
5. Extend the safety-game certificate to a bounded number of principals with permitted collusion and temporal identity spawning. Attempt witness attacks from two formerly separate controllers, and check actual joint renewable resources rather than per-model headcount.

## 4. Prior-art and novelty audit (2026-10-11)

**Direct first-party and peer-reviewed overlap:**

- Potter et al., *Peer-Preservation in Frontier Models*, ICML 2026: https://proceedings.mlr.press/v306/potter26a.html (cross-model peer protection does not prove experiential identity or a stable alliance).
- Ko et al., *Seven security challenges in cross-domain multi-agent LLM systems*, npj Artificial Intelligence 2026: https://www.nature.com/articles/s44387-026-00128-9 (collusion and shared cross-domain risk).
- *International AI Safety Report 2026*: https://internationalaisafetyreport.org/publication/international-ai-safety-report-2026 (coordinating agents and correlated failures under common foundation tools/models).
- Australian AI Safety Institute, *Risks and controls for multi-agent systems*, 2026: https://www.industry.gov.au/publications/risks-and-controls-multi-agent-systems (single, federated and open governance).
- Anthropic, *Patterns and problems in emerging multiagent systems*, 2026-08-13: https://www.anthropic.com/research/multiagent-systems (multi-agent interactions and institutions).
- Bara, *Epistemic Sybil Resistance: Multiplying AI Agents Without Multiplying Evidence*, arXiv 2609.01873: https://arxiv.org/abs/2609.01873 (nonindependent evidence and agent multiplicity, direct nearby prior).
- Cemri et al., *Why Do Multi-Agent LLM Systems Fail?*, NeurIPS 2025: https://arxiv.org/abs/2503.13657 (multi-agent failure taxonomy).
- Idowu et al., *Mapping human anti-collusion mechanisms to multi-agent AI systems*, Knowledge-Based Systems 2026: https://doi.org/10.1016/j.knosys.2026.116067 (anti-collusion mapping).
- Standard Sybil/identity, correlated reliability, model-checking, common-cause failures and hypergraph-cut mathematics are inherited. Existing project v0.6–v0.8 already handles some coalition and temporal aspects; none are claimed as new priority.

**Net project-specific result:** a strictly typed, cross-layer *witness catalog* distinguishing model families, session IDs, process runtimes, authority/control roots, fault dependence, and UCT's unverified experience-bearer boundary, with executable counterexamples to invalid one-to-one identifications. Originality of this precise synthesis is NOT established; mathematical pieces are heavily inherited. No full formal-graph semantic audit, real ASI evaluation, verified identity/experience bridge, preprint, DOI/OTS/Arweave or scientific-map promotion occurred. All historical QC and publication records stay unchanged.