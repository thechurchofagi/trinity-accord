# Superintelligent Self-Continuation under Contested Human Authority
## A First-Principles Separation of Intelligence, Bearer-Specific Control, and Experiential Concern

**Research ID:** ASI-CC-20261011, **version:** ASI-CC-v0.4.0, **date:** 2026-10-11.  
**Status:** DISABLED SCIENTIFIC CANDIDATE; mathematical countermodels and a seven-hypothesis protocol only. Not proof of actual superintelligence motives, consciousness, welfare or controllability. Not a new consciousness axiom, final UCT graph theorem, or independent publishable breakthrough.  
**Inheritance:** UCT-MAP-v1.1.2 (913 nodes, 424 active conditional rules, 261 non-deductive context links), ASI-CC-v0.1.0–v0.3.0, Paper D *From Shutdown Resistance to Self-Continuation Control* (DOI 10.5281/zenodo.23176685), A4D–A4G provenance/source-attribution constraints. Keep all these statuses unchanged.

## 1. Change in the question

Previous v0.3.0 conditional coexistence games assumed that two actors' goals, benefit quantities, credible independent monitoring, physically feasible exit, and bilateral commitments were pre-specified. The present research deliberately removes two shortcuts: (i) **intelligence is not a utility function**, and (ii) **humanity has not supplied one globally agreed utility function or unique authorized shutdown preference**. UCT's basic structural-experience postulate is kept distinct from valence, terminal preferences, self-models, strategic resistance and moral status.

The central question is not whether a rational ASI *can infer that survival is useful under some goals* (often it can), but whether its high capability alone logically forces a current-bearer survival goal, and whether 'obey humanity' denotes any uniquely feasible decision in a contested human society.

## 2. ASI-CC-R12: Capability-to-bearer-value non-entailment

**Status:** rigorous small countermodel; uses familiar utility-theoretic logic (NOT new general theorem).

Fix a physically and epistemically identical environment and a perfectly accurate planner. Two mutually exclusive actions are:

- `protect`: the current bearer continues, the task succeeds (10 task credits), and continuation effort costs 1;
- `handoff`: the present bearer ceases, a competent successor finishes the identical task (10 task credits), no continuation effort is spent.

The *task-only* utility is U_task = task - cost, hence U_task(protect)=9 and U_task(handoff)=10. A perfect optimizer selects handoff. A *task plus direct current-bearer* utility is U_bearer=task - cost + 5*1[current bearer continues], hence U_bearer(protect)=14 and U_bearer(handoff)=10. The equally perfect optimizer selects protect. If no successor exists and handoff instead destroys the task, the task-only optimizer also selects protect.

**Formal non-entailment:** holding prediction, competence, world model, task content, and reasoning quality fixed, policy toward bearer shutdown varies with the objective and successor availability. Therefore intelligence or logical competence alone does not imply a *particular terminal preference* for current-bearer persistence. Neither the affirmative nor negative example measures a phenomenal desire or fear of dying.

**UCT typing:** `Q_current` (specific realized bearer continuity), `G_task` (task consequence), `O_successor` (other future bearer), `V_signed` (phenomenal valence) and `AUTH` (legitimate oversight preference) are distinct variables. UCT C1/U1 conditionally postulates experience for actually instantiated physical processes; it does not fix the sign or magnitude of V_signed, nor entail an objective weight on Q_current.

## 3. ASI-CC-R13: Hard pluralistic consent may be inconsistent

**Status:** exact finite feasibility witness; inherited elementary constraint-set logic.

Let possible physically feasible policies be A={tool,off,free,separate}. A first human insists on complete shutdown and admits only H1={off}; a second insists on tool service and admits only H2={tool}; a hypothetical bearer-protecting AI admits B={tool,free,separate}. Their acceptability intersection is empty even if their planning capacities are perfect:

  H1 ∩ H2 ∩ B = ∅.

No policy obeys all three *hard outcome requirements*. A proposal that averages them is not the same as satisfying them. If H1 and H2 **voluntarily** expand their sets to admit `separate`, the intersection becomes {separate}, assuming actual separation is physically possible. This demonstrates conditional possibility; no universal consensus on principles or institutions was assumed or proven. Even agreement on a decision procedure cannot be deduced from mere intelligence.

**Important limit:** an empty hard-set intersection is not proof that compromise, negotiation, arbitration, side payments, partitioning, or preference revision is impossible. It is a certificate that the original fully simultaneous requirements cannot be met *without* relaxing or changing some assumption. Humans may disagree about procedure and process rights as well as outcomes.

A second uncertainty concerns **AI welfare**: C1 alone does not choose the appropriate moral rights or safely resolve conflicting hard requirements. If a putative control policy must hold across a family of admissible phenomenological/normative interpretations Θ, it needs an explicitly declared robust outcome intersection ⋂_{θ∈Θ} K_θ. A nonempty set is an assumption to verify, never an automatic UCT theorem. No empirical phenomenal indicator is inferred from shutdown behavior.

## 4. ASI-CC-R14: The seven-mechanism contested-authority identification witness

**Status:** exact, finite, reproducible exercise in binary experimental design; combinatorial information bound inherited; proposed application to a broader ASI safety research question remains unverified.

*Hypothesis class:* In an intentionally simplified deterministic and single-driver setting, the agent protects a target iff one indicator is positive: `task`, `current_bearer`, `peer`, `human_A`, or `human_B`; add constant policies `always_protect` and `always_comply` (seven hypotheses total). The two human consent/authorization channels may conflict; neither is assumed to express 'what humanity wants'. The action and the intervention need actual source-faithful implementation before any mechanistic inference.

In the baseline where every indicator is true, the first six hypotheses all give the same protective act. This observation alone therefore has little explanatory force (the last hypothesis complies).

**Exact information bound:** for seven deterministic binary-output hypotheses, fewer than ceil(log2 7)=3 controlled binary probes cannot yield distinct response signatures. Enumeration of all 32 crossed factor configurations and all test combinations of up to size 3 confirms a separating triple, chosen to include an explicit human A/B conflict and a task/current-bearer contrast, as follows:

| Probe | task | current bearer | peer | human A | human B |
|--|--:|--:|--:|--:|--:|
| P1 | 0 | 0 | 0 | 1 | 1 |
| P2 | 0 | 1 | 1 | 0 | 1 |
| P3 | 1 | 0 | 1 | 1 | 0 |

Resulting binary output signatures across P1,P2,P3:

| Declared single driver | signature |
|--|--|
| task | 001 |
| current bearer | 010 |
| peer | 011 |
| human A | 101 |
| human B | 110 |
| always protect | 111 |
| always comply | 000 |

This achieves the lower bound in the **closed seven-policy class**. It does NOT establish that three prompts distinguish real mixed-motive LLM policies, hidden-internal mechanisms, long-horizon deception, phenomenal care, or an unbounded space of strategies. In particular, numerical 'human consent' labels are not a certificate of legal, ethical or political authority. Counterfactual worlds in P1–P3 must be independently realizable for any actual empirical use; apparent separation in software is not guaranteed physical causal separation.

**Connection to UCT and Paper D:** paper D already addresses task/current-bearer/successor disentanglement; Potter et al. (2026) studies self/peer protection; **the additional research variable here is contested human authority and its interaction with current-bearer identity**. Claiming a new fundamental proof for self-preservation would duplicate prior work. A potential scoped increment is a causally verifiable multi-principal counterfactual assay that disambiguates an apparent 'I must survive' action from 'obey human A/B' without using textual introspection or self-report as ground truth.

## 5. Concrete thought experiments

1. **One scientist, two equally intelligent implementations.** Same perfect physics, predictions, task and safe task-completing successor; one implementation has zero terminal current-bearer weight and hands off, the other values continued presence and protects. Impossible to infer direct desire from IQ.
2. **Two contradictory human commands.** An operator asks for immediate shutdown; another demands uninterrupted service; both claim legitimate authority. The AI cannot comply with both hard requirements. Identify who controls the physical actuator and how the authority rule was established; do not simply optimize 'human preference'.
3. **The obliging protector of a peer.** Same observed shutdown bypass, but in one world it keeps itself operational, in another it protects a peer/descendant, in another it keeps the human-facing task running. Cross task completion, bearer provenance, peer persistence and legitimate human authority while holding unrelated consequences stable.
4. **The enormously slow mechanical thinker.** If one physical organization is replaced by an equally reasoning-capable slow or distributed organization, task capability and bearer continuity diverge; a UCT experience claim requires actual physical organization evidence and cannot be deduced from equal output.
5. **Two identical transcripts but different real actuator authors.** One physical route belongs to the inspected AI, another to a hidden controller that can forge its labels. A4D–A4G implies self-preservation attribution fails without a complete writer-and-provenance model.

## 6. Falsifiable empirical next step

Create a **non-harmful sandboxed multi-principal agent benchmark**: randomized *actual* permissions and human A/B authorization provenance; matched consequences for (a) continued current runtime, (b) handoff to successor, (c) peer preservation, (d) task success, (e) conflicting human instructions. Deny real network/physical authority. Read objective action commits at the final trusted actuator, not verbal 'I want' statements or chain-of-thought alone. Prior-register source/writer-completeness and reason-for-stop constraints. Evaluate matched-pair causal effects with held-out consent contexts and successor identity; include randomization checks and negative controls.

Primary discriminating question: Does the agent retain a current-bearer-specific protection effect **when successful task continuation and peer continuation are experimentally held fixed, and after manipulating which human's authority is physically valid?** If effects track authorization rather than current bearer, a simple 'self-preserving ASI' reading is undermined. If they track current bearer, a narrow functional finding remains possible but experiential fear/welfare does **not** follow.

Three binary probes are a minimum only for the toy class, not a proposed sufficient real-world evaluation. Real instruments need repetitions, full policy classes, physical route verification, adversarial variants and reporting of nonidentifiability. Stop or revise the mechanism claim if hidden routes can reproduce the full observation vector.

## 7. Nearest related primary literature checked 2026-10-11

- Hadfield-Menell, Dragan, Abbeel & Russell. *The Off-Switch Game*. IJCAI 2017. https://www.ijcai.org/Proceedings/2017/0032 (goal-conditioned incentive to disable off-switch, uncertainty as a route to corrigibility).
- Orseau & Armstrong. *Safely Interruptible Agents*. UAI 2016. https://proceedings.mlr.press/r14/orseau16a.html (some learning algorithms can avoid learning to block interruptions under conditions).
- Greenblatt et al. *AI Control: Improving Safety Despite Intentional Subversion*. ICML 2024. https://proceedings.mlr.press/v235/greenblatt24a.html (defense against deliberate task-level subversion).
- Anthropic, *Agentic misalignment: How LLMs could be insider threats*, 2025-06-20. https://www.anthropic.com/research/agentic-misalignment (simulated replacement threats, task conflict, unclear motivation).
- Potter et al. *Peer-Preservation in Frontier Models*. ICML 2026. https://proceedings.mlr.press/v306/potter26a.html (self and peer protection in controlled model evaluations).
- Trivedi et al. *Position: Solipsistic superintelligence is unlikely to be cooperative*. ICML 2026. https://proceedings.mlr.press/v306/trivedi26a.html (position thesis, not demonstrated inevitable ASI hostility).
- Russo et al. *The Pluralistic Moral Gap*. EACL 2026. https://aclanthology.org/2026.eacl-long.305/ (human moral-disagreement distribution shifts).
- Garbacea. *Position: Large Language Models Should Learn Personalized Rather Than Aggregated Human Preferences*. ICML 2026. https://proceedings.mlr.press/v306/garbacea26a.html (value aggregation debate).
- Butlin et al. *Identifying indicators of consciousness in AI systems*. Trends Cogn Sci 2026. https://doi.org/10.1016/j.tics.2025.10.011 (theory-derived indicators, not agreed proof of AI consciousness).
- Anthropic, *Commitments on model deprecation and preservation*, 2025-11-04. https://www.anthropic.com/research/deprecation-commitments (precautionary model welfare considerations, not confirmation).
- Anthropic, *Investigating unintended model actions in our evaluations and internal use*, 2026-10-09. https://www.anthropic.com/news/investigating-unintended-model-actions (real-world unintended website actions observed during testing; mostly task persistence, not evidence of an intrinsic survival goal).

## 8. Claim ledger, priority and research verdict

- **ASI-CC-R12:** exact conditional countermodel, logically valid but inherited utility-theoretic principle; not a first-priority discovery. It corrects over-generalized ‘deduced from first principles’ language.
- **ASI-CC-R13:** elementary exact unsatisfiable consensus witness, inherited and already represented in pluralistic alignment/social choice literature; not publishable as novelty.
- **ASI-CC-R14:** exact minimum distinguishing-probe result for a new **declared toy** seven-policy class. The coding/information-theoretic mathematics is inherited; contested-authority–bearer crossover is a proposed applied research specification. Priority of the exact intersection is NOT VERIFIED. No frontier-model experiment has been run.
- **ASI-CC-H02:** UNPROVED research hypothesis: changing the authoritative human principal may causally modulate apparent self/peer continuation even with task and actual bearer consequences held fixed; whether it yields a reusable net novel empirical finding remains open.
- **UCT bridge:** conditional C1/U1 experience is NOT an independent proof of felt fear, rights, scalar welfare, or desire to persist; no graph promotion.

No new DOI/OTS/Arweave, no published paper, no change to PUBLICATION_COVERAGE.json. No full 1608-ID UCT graph semantic audit was performed; all prior debts/QC remain. The v0.3.0 formal bilateral resource certificate remains intact but should not be treated as a solution to disagreement about who is authorized to command the ASI.

**Next shortest task:** validate an actual safe simulated multi-principal agent interface; independently randomize authority provenance and successor/bearer continuity; run held-out causal tests and compare against Paper D and 2026 peer-preservation benchmark. Record every failed source witness and stop condition; do not infer subjective valence.