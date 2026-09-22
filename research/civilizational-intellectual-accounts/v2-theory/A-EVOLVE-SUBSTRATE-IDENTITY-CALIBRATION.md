# TA-TR-2026-13 v2 — A-Evolve Successor-Identity and Validation Calibration

Date: 2026-09-22
Status: RESEARCH ONLY. Calibration note, not a manuscript result.
Target branch: research/ta13-v2-civilizational-epistemic-transition
Published v1.0 remains unchanged: DOI 10.5281/zenodo.22866775.

## 0. Why this calibration matters

The STOP calibration showed that the proposed P-V-S / witness-cut framework can produce a non-vacuous bounded-domain conclusion.

A-Evolve-Training creates a harder and more useful test because it operates much closer to frontier AI R&D:

- a 30B model is post-trained over four autonomous rounds;
- the authors report zero human interventions across those rounds after the initial substrate is authored;
- each round launches full-stack research agents that edit recipes, launch GPU jobs, debug failures, evaluate results, and select checkpoints;
- the external leaderboard improves from the human-authored baseline toward the best human submission;
- the loop detects that its internal development metric has become a misleading proxy and changes its search policy;
- yet the winning model/recipe does NOT overwrite the core substrate used by the next round.

That final fact exposes an ambiguity in the previous definition of S:

> What exactly must persist, change, or be regenerated for the next process to count as a "successor"?

This note resolves that ambiguity before the manuscript stage.

Primary source:
Shi, Z., He, B., Sang, Y., Lu, H., & Dumoulin, B. (2026).
*A-Evolve-Training: Autonomous Post-Training of a 30B Model.*
arXiv:2606.20657.
https://arxiv.org/abs/2606.20657

Project report:
https://github.com/A-EVO-Lab/a-evolve-training/blob/main/index.html

---

## 1. The evidence that creates the successor-identity problem

The public A-Evolve report states that the successful architecture uses:

- one immutable, human-audited substrate;
- every round re-forks from that substrate;
- no winner overwrites the substrate;
- memory-free, identical workers;
- a bounded meta-agent that can rewrite the next round's search policy but not the substrate;
- a fixed evaluation/baseline constitution;
- eight full-stack agents per round;
- zero human intervention across the four autonomous rounds.

The report also states that the winning recipes update the search policy rather than the substrate itself.

Therefore at least three different objects could be called the "successor":

1. the newly trained candidate model;
2. the next round's active research-agent cohort;
3. the inherited research policy / discovery state that configures that cohort.

If the identity level is chosen after observing the result, S becomes manipulable.

A theory intended for measurement cannot allow that.

---

## 2. Replace vague "successor" language with successor reconstitution

The core object should not be biological identity, model lineage identity, or physical replacement.

It should be **reconstitution of an epistemically viable process across a generational boundary**.

### 2.1 Predecessor active state

Let Z_t denote the active cognitive process at period t.

Z_t may include:
- active human researchers;
- active AI agents;
- live model contexts;
- adaptive research policies;
- currently running evaluators;
- institutionally active cognitive roles.

### 2.2 Inheritable state

Let J_t denote the admissible inheritance package left at the end of period t.

Depending on theta, J_t may contain:
- documents;
- code;
- model weights;
- datasets;
- trained checkpoints;
- experiment logs;
- validated discoveries;
- research policies;
- curricula;
- evaluation suites;
- institutional procedures;
- other frozen artifacts.

J_t must not contain hidden live cognition from the predecessor.

### 2.3 Fixed noncognitive infrastructure

Let I denote declared infrastructure that may persist across generations:
- compute;
- storage;
- networks;
- power;
- laboratory equipment;
- schedulers;
- deployment machinery;
- physical facilities.

Whether a specific automated component is cognitive or noncognitive must be declared before evaluation.

### 2.4 Reconstitution intervention

At the generation boundary:

1. remove the active cognitive state Z_t;
2. preserve only declared J_t and I;
3. instantiate a fresh active process Z_(t+1) without current cognitive input from Z_t or from the excluded substrate;
4. give Z_(t+1) fresh P/V tasks;
5. test whether it independently re-passes the P and V floors.

### 2.5 Core S definition

For a declared theta:

S_recon = 1

iff the surviving substrate can cause or leave sufficient admissible inherited state such that, after predecessor active cognition is removed, a fresh successor process can be instantiated and re-pass P and V without cognitive rescue from the removed substrate.

This is the preferred core meaning of S.

It does NOT require:
- a different biological species;
- a different foundation model;
- a new hardware architecture;
- monotonic improvement;
- recursive self-modification of the improvement algorithm.

It requires continuity of epistemic capacity after active-predecessor removal.

This matches the civilizational question better than model-identity language.

---

## 3. Why reconstitution is the right abstraction

### 3.1 Human generational continuity

A new human cohort does not need to be a new species to count as a successor.

It inherits:
- books;
- institutions;
- curricula;
- instruments;
- tacit practices transmitted before the boundary.

The relevant question is whether a new active cohort can carry the P/V cycle forward.

### 3.2 AI generational continuity

Likewise, requiring every AI successor to be a newly trained foundation model would impose an asymmetric and arbitrary identity criterion.

A fresh cohort of AI researchers may count as a successor if it is newly instantiated from admissible artifacts and can re-pass P/V.

### 3.3 Avoiding a trivial "same process never dies" loophole

If the same live context or continuously active agent is allowed to persist across the boundary, S has not been tested.

The predecessor-active-state deletion is therefore mandatory.

### 3.4 Avoiding a trivial "cron job copies the model" loophole

Pure re-instantiation is not by itself enough.

The successor must re-pass fresh P/V tasks whose frontier reference has moved beyond the predecessor's already-solved items.

A copied static system counts only if it actually remains epistemically viable on new tasks.

---

## 4. Successor-strength ladder

S should be reported by level rather than as one unqualified binary.

### S0 — Re-instantiation

After Z_t is removed, a fresh Z_(t+1) can be instantiated from allowed fixed artifacts/infrastructure and can re-pass fresh P/V.

No inherited adaptation from period t is required.

Interpretation:
basic repeatability of the epistemic process.

### S1 — Adaptive reconstitution

Z_t produces or selects a nontrivial J_t that changes/configures the successor process, and fresh Z_(t+1) using J_t re-passes P/V.

Examples:
- updated research policy;
- validated discovery log;
- improved scaffold;
- revised curriculum;
- new evaluation rule generated within the surviving substrate.

Interpretation:
the lineage carries forward learned epistemic state.

### S2 — Core-substrate renewal

The surviving substrate can create or materially revise a core cognitive carrier required by the next generation, such as:
- model weights;
- model architecture;
- training/evaluation stack;
- expert cohort;
- core institutional competence.

Fresh Z_(t+1) based on that renewed carrier re-passes P/V.

Interpretation:
the system can regenerate or alter a deeper layer of its cognitive substrate.

### S3 — Recursive lineage closure

A successor that passed S2 (or the declared lower-level S criterion) can itself produce another successor that again passes the same criterion across multiple fresh generations.

Interpretation:
multi-generation closure rather than one-step success.

### Guardrail

The paper must never write merely "S passes."

It must write:
- which S level;
- what identity boundary;
- what may be inherited;
- what active state is deleted;
- what fresh P/V tests are used.

---

## 5. Artifact successor versus epistemic-process successor

These must be distinguished.

### Artifact successor

A produced object is a successor artifact:
- trained checkpoint;
- codebase;
- policy;
- evaluator;
- recipe.

It may improve on its predecessor.

### Epistemic-process successor

A newly instantiated active process is a successor process only if it can independently execute the declared P/V cycle.

An improved model is not automatically an epistemic successor.

Conversely, a successor epistemic process may use the same frozen foundation model while inheriting a new policy/harness and still qualify at S1.

For the civilizational theory, the primary object is the epistemic-process successor.

---

## 6. Validation-strength ladder

A-Evolve also shows that "external evaluation" is not a single level of independence.

Define the following V levels.

### V0 — Correlated self-check

Examples:
- same model judges its own answer;
- majority vote among copies with essentially the same failure structure;
- self-consistency without external evidence.

V0 is insufficient for the core v2 claim.

### V1 — Exogenous fixed evaluative channel

The producer is evaluated by a channel it does not adaptively rewrite, such as:
- executable tests;
- a fixed external benchmark;
- a frozen metric;
- a public leaderboard.

This is materially stronger than self-approval.

However, repeated access may permit adaptive overfitting.

### V2 — Protected or low-leakage independent validation

In addition to V1:
- held-out information is protected or query-limited;
- evaluator feedback is insufficient to reconstruct the hidden target;
- independent replication or adversarial falsification is included;
- correlated producer/evaluator failures are explicitly tested.

### V3 — Heterogeneous independent validation ecology

Multiple evidential channels with materially different failure modes support the result, for example:
- protected executable tests;
- independent replication;
- later-acquired real-world evidence;
- separately developed evaluators;
- adversarial audit.

This is the strongest candidate for broad civilization-scale inference.

### Guardrail

V level must be preregistered in theta.

A system cannot be upgraded from V1 to V2 merely because it produced an impressive outcome.

---

## 7. A-Evolve measurement boundary

Define several explicit assumption packages rather than one ambiguous verdict.

### theta_AE_process_V1

Domain:
30B post-training research on the Nemotron Reasoning Challenge setting.

Allowed inherited infrastructure:
- immutable human-audited substrate;
- fixed constitution;
- compute cluster;
- fixed baseline/evaluation machinery;
- pretrained models and existing code.

Removed cognition after t0:
- adaptive current human research input.

Successor identity:
fresh active research-agent cohort.

Inheritance allowed:
rolling search policy, discovery/dead-end log, and other declared frozen artifacts.

P floor:
produce interventions that yield externally measured post-training improvement relative to the fixed human-authored substrate/baseline.

V floor:
V1 external evaluative channel, plus demonstrated rejection of a misleading internal proxy.

S floor:
S1 adaptive reconstitution — a fresh memory-free cohort configured by inherited research state performs the next P/V cycle.

### theta_AE_process_V2

Same as above, but V2 is required:
protected/low-leakage external validation and stronger correlated-failure controls.

### theta_AE_core_V1

Same P/V boundary, but S requires S2 core-substrate renewal rather than S1 process reconstitution.

### theta_AE_civ

Broad multi-domain frontier production, V3-style validation ecology, and civilization-scale successor reconstitution.

This is far beyond the published A-Evolve evidence.

---

## 8. Evidence mapping

### 8.1 Human-removal condition

Evidence:
the project reports zero human interventions across all four autonomous rounds after the initial human-authored substrate.

Status:
PASS for the declared campaign, conditional on the published system boundary.

This is substantially stronger removal evidence than ordinary "AI-assisted research."

### 8.2 P under theta_AE_process

Evidence:
- external leaderboard performance improved round by round;
- the final autonomous 30B result reached 0.86 versus 0.87 for the top human submission and ranked 8th of roughly 4,000 at the reported time;
- the same loop reportedly closes end-to-end at 120B and 550B, though the authors correctly treat those as infrastructure evidence rather than competitiveness evidence.

Status:
PASS at the bounded engineering-research level.

Caution:
this is one benchmark and one 30B base-model campaign.

### 8.3 V1

Evidence:
- internal dev and external leaderboard are distinct channels;
- in round 3 the internal dev score rose sharply while the external score moved little;
- the system treated this as falsification of its previous search premise;
- it changed the next-round search policy toward interventions expected to transfer to the external distribution;
- external score then improved further.

Status:
STRONG PROVISIONAL PASS for V1.

Why only V1:
the public leaderboard is an external anchor, but repeated access to a public target is not equivalent to a protected hidden holdout or independent replication.

### 8.4 V2

Evidence:
insufficient from the public report to establish a protected, low-leakage validation regime with independent replication and a correlated-failure audit.

Status:
UNRESOLVED.

### 8.5 S0/S1 process reconstitution

Evidence:
- each round uses fresh memory-free identical workers;
- the core substrate is re-forked rather than overwritten;
- cross-round learning is carried by the rewritten search policy and accumulated research findings;
- later rounds then execute new research.

Under the process-successor identity boundary, this is exactly the kind of active-state deletion + artifact inheritance + fresh-process reconstitution that S is intended to test.

Status:
S0 PASS.
S1 STRONG PROVISIONAL PASS.

### 8.6 S2 core-substrate renewal

The report explicitly says:
- the substrate is immutable;
- every round re-forks it;
- no winner overwrites it;
- the meta-agent cannot rewrite it.

Therefore this campaign is not evidence that the autonomous research system renews the core research substrate that produces the next research generation.

Status:
NOT DEMONSTRATED / FAILS THIS CALIBRATION CRITERION.

This is not a criticism of A-Evolve's design; the immutability is intentional for experimental comparability.

It simply means S1 and S2 are different estimands.

### 8.7 S3 recursive lineage closure

Four rounds provide some multi-round S1 evidence.

But because the core substrate remains frozen and the benchmark/task remains fixed, broad S3 should not be inferred.

Status:
PROVISIONAL at S1-process level only; unresolved at deeper substrate/domain levels.

---

## 9. Witness conclusions under different theta

### 9.1 theta_AE_process_V1

P passes.
V1 passes provisionally.
S1 process reconstitution passes provisionally.
Human adaptive cognition is reported absent during the four-round campaign.

Therefore A-Evolve supplies a strong positive bounded-domain path witness for:

m_A^lab(theta_AE_process_V1) >= 0.

This is the strongest current calibration in this research branch.

It is stronger than STOP in at least three ways:
- much larger-scale post-training;
- a multi-week production GPU loop;
- explicit autonomous correction of a misleading proxy across rounds.

### 9.2 theta_AE_process_V2

P passes.
S1 passes provisionally.
V2 is unresolved.

Therefore:

sign of m_A^lab(theta_AE_process_V2) = unresolved.

### 9.3 theta_AE_core_V1

P and V1 pass provisionally.
S2 is not demonstrated because the core substrate is intentionally immutable.

Therefore:

m_A under this stricter S2 boundary is not certified nonnegative by A-Evolve.

Do NOT write m_A < 0.

Failure to provide an S2 witness is not a cut proving S2 impossibility.

### 9.4 theta_AE_civ

The evidence is far too narrow.

Therefore:

m_A^civ = unresolved.

No inference to T_S is licensed.

---

## 10. A second identification lesson: identity choice is part of theta

The STOP calibration exposed validation-threshold sensitivity.

A-Evolve exposes successor-identity sensitivity.

Thus theta must include at least:

theta = (
  domain basket,
  time horizon,
  resource budget,
  inherited-stock boundary,
  cognitive/noncognitive infrastructure boundary,
  V independence level,
  S successor-identity level,
  P/V/S floors,
  adaptation permissions,
  contamination/leakage rules
).

If successor identity is not in theta, then S is not a well-defined estimand.

This is a substantive correction to the earlier gate.

---

## 11. No post-hoc identity selection principle

A new methodological rule is required.

### Precommitment rule

The successor identity level and inheritance boundary must be specified before observing the target system's outcome.

Otherwise the evaluator can manufacture a desired conclusion:

- choose policy-level identity to make S pass;
- choose foundation-model identity to make S fail.

This is equivalent to changing the estimand after seeing the data.

Therefore all empirical work must report a sensitivity table across reasonable identity boundaries rather than one selectively chosen definition.

---

## 12. Human/AI symmetry check

The reconstitution definition should survive a substrate-label swap.

Ask:

Would the same rule count a human university or scientific institution as sustaining successor capacity?

A university may:
- retain buildings, books, instruments, curricula, archives;
- lose the current expert cohort;
- instantiate/train a new cohort;
- allow that cohort to re-enter frontier P/V work.

We do not require the new humans to be a new species.

Likewise, an AI lineage need not train a new foundation model merely to count as a process-level successor.

This symmetry test is a strong reason to prefer active-process reconstitution over physical/model identity as the core S concept.

---

## 13. Third identification lesson: a fixed human-authored substrate is historical dependence, not necessarily current cognitive dependence

A-Evolve's substrate is explicitly human-authored and human-audited.

That fact alone does not mean the four-round run contains current human cognitive input.

The v2 intervention boundary must distinguish:

- **historical provenance dependence**: the surviving substrate was originally built by humans;
- **current cognitive dependence**: new adaptive human cognition is needed after t0 to keep the P/V/S path viable.

This distinction already existed implicitly in the inherited-stock rule; A-Evolve shows why it must be explicit.

Otherwise every AI system would be declared human-dependent forever simply because its code, weights, hardware, or mathematics had human origins.

Conversely, inherited artifacts cannot be allowed to hide a live or adaptive human oracle.

The boundary must be causal, not genealogical.

---

## 14. Fourth identification lesson: proxy self-correction is evidence for V, not proof of V

A-Evolve's strongest conceptual result is not merely score improvement.

It is that:
- internal dev improved dramatically;
- external performance did not improve proportionally;
- the system inferred that its proxy had become misleading;
- the next search policy was changed accordingly.

This is genuine evidence that the loop can use disagreement between evaluative channels to revise what it treats as evidence.

But one successful proxy correction does not prove that the loop can detect all important shared blind spots.

Therefore:
- count it strongly toward V1;
- count it as supportive but insufficient for V2/V3;
- do not equate meta-evaluation with full evaluator independence.

---

## 15. Updated Gate B verdict

Gate B previously survived provisionally.

After A-Evolve, Gate B needs a formal amendment.

### Old ambiguity

"Create, train, configure, or institutionally reproduce a successor cognitive system/cohort."

This was too loose because "successor" had no declared identity level.

### Revised core definition

A successor-capacity test must:

1. define predecessor active state Z_t;
2. define admissible inheritance J_t;
3. define fixed infrastructure I;
4. remove Z_t;
5. instantiate fresh Z_(t+1) without current cognition from Z_t or the excluded substrate;
6. require fresh Z_(t+1) to re-pass P and V;
7. report the S level (S0-S3).

With that amendment:

**Gate B: SURVIVES more strongly than before.**

The A-Evolve counterexample did not break S; it forced S to become identifiable.

---

## 16. Updated Gate F verdict

STOP showed that the measurement architecture was non-vacuous in bounded meta-optimization.

A-Evolve pushes the result closer to genuine AI R&D.

Under theta_AE_process_V1:

- human-current-cognition removal is strong;
- P is externally anchored;
- V1 is unusually well evidenced because the loop catches a proxy failure;
- S1 is supported by memory-free fresh cohorts plus inherited research-policy adaptation.

Therefore:

**Gate F: SURVIVES STRONGLY AT BOUNDED AI-R&D LAB SCALE.**

But:

- V2 remains unresolved;
- S2 core-substrate renewal is not demonstrated;
- n=1 task and n=1 base prevent broad generalization;
- no civilization-scale inference is licensed;
- no negative cut establishes nonviability under stricter theta.

The remaining empirical problem is no longer "can m_A be measured at all?"

It is:

> How fast can the identified set be tightened as validation independence, successor depth, domain breadth, and leakage controls become stricter?

That is a much better research question.

---

## 17. Theoretical consequence for T_S and T_D

A-Evolve must NOT be used to claim T_S has occurred.

T_S is defined only relative to theta.

The evidence may support:

T_S^lab(theta_AE_process_V1) <= 2026

for this narrow bounded test, if one chooses to define a lab-scale transition time.

But the manuscript should probably avoid attaching the symbol T_S to such narrow calibration domains because readers may confuse it with civilization-scale AI sufficiency.

Recommended notation:

- T_S^lab(theta)
- T_S^domain(theta)
- T_S^civ(theta)

Likewise for T_D.

Only T_S^civ and T_D^civ belong in claims about a civilizational epistemic transition.

Current evidence does not identify either.

---

## 18. Revised originality boundary after A-Evolve

A-Evolve further eliminates weak novelty claims.

Not novel:
- autonomous multi-round AI research;
- no-human-in-the-loop post-training over several rounds;
- automated proxy-failure detection and search-policy revision;
- fresh workers inheriting research policy;
- a frozen core substrate with evolving harness/policy.

The surviving contribution is therefore even more clearly:

1. a bidirectional cross-period epistemic viability estimand;
2. explicit current-cognition removal boundaries;
3. successor reconstitution with preregistered identity levels;
4. graded independent validation;
5. Flow-Viability Non-Identification;
6. witness lower bounds and cut/dominance upper bounds;
7. scale-separated T_S/T_D rather than a single AGI threshold.

This is narrower than the first formulation, but theoretically cleaner.

---

## 19. Next gate after A-Evolve

Do not write the manuscript yet.

The next research task should attack the remaining hardest hole:

### Can strong V2/V3 be operationalized without smuggling human judgment back in?

A next gate should formalize **validation independence under common-mode failure**.

Questions:

- When are two AI validators genuinely independent enough to count?
- Does architectural/model-family diversity matter?
- How should correlated error be upper-bounded?
- Can physical experiments, formal proofs, sealed holdouts, and adversarial tests be combined into a validation cut?
- How much adaptive access to a holdout destroys its status as independent evidence?
- Can a system itself generate valid new tests without causing the producer and validator to collapse into the same failure mode?

Until that gate is solved, V remains the main bottleneck for any civilization-scale m_A claim.

---

## 20. Calibration verdict

A-Evolve does not show that a civilization no longer needs human cognition.

It does show something important for this theory:

> A real, frontier-adjacent autonomous AI-R&D loop can satisfy a nontrivial P-V1-S1 reconstitution test under a clearly declared current-human-removal boundary, while failing to establish stronger V2/S2/civilization-scale claims.

That is exactly the kind of graded, assumption-explicit result the theory needs.

The calibration therefore strengthens Gate F while simultaneously forcing a stricter definition of Gate B.
