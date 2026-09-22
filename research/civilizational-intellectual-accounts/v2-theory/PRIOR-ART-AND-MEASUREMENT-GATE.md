# TA-TR-2026-13 v2 Research Gate — Prior Art, Witness–Cut Identification, and Empirical Tractability

Date: 2026-09-22
Status: RESEARCH ONLY. Not a manuscript. Not authorized for DOI publication.
Branch: research/ta13-v2-civilizational-epistemic-transition
Published v1.0 remains unchanged: DOI 10.5281/zenodo.22866775.

## 0. Executive verdict

This gate materially narrows the originality claim.

Several ideas that looked potentially central are NOT safe novelty claims:

- the distinction between independent and dependent modes of two coupled substrates;
- asymmetric dependence;
- a phase transition caused by loss of independence rather than a discontinuous capability curve;
- removal/intervention tests on interdependent systems;
- self-maintenance, organizational closure, or self-production;
- successor formation by AI;
- an improvement loop containing a verifier, inheritance, and a successor;
- recursive inheritance of an improver/evaluator/research policy;
- tool-removal cost or post-AI unassisted human performance.

The literature already contains strong versions of all of these.

The surviving candidate contribution is narrower and more defensible:

> Define the object of interest as cross-period epistemic viability, requiring frontier production (P), sufficiently independent validation/correction (V), and successor-capacity formation (S); define substrate-specific removal counterfactuals for human and AI cognition under a frozen inherited-stock/infrastructure boundary; prove that realized coupled intellectual flows do not identify those viability counterfactuals; and estimate them by one-sided constructive path witnesses and structural cut-based upper bounds.

On this formulation, the transition times T_S and T_D are applications of the estimand, not the novelty claim by themselves.

Gate A (prior-art originality): PARTIAL FAIL on the broad framing; SURVIVES on the composite estimand + identification architecture, provisionally.

Gate F (empirical tractability): SURVIVES at the protocol level and is demonstrably non-vacuous in bounded calibration domains; NOT YET established for civilization-scale or broad frontier-AI-R&D viability.

Do not draft the manuscript yet. The next manuscript gate should require that the composite contribution be stated without claiming novelty for any borrowed primitive and that at least one preregistered or reproducible calibration exercise produces a non-vacuous witness/cut interval.

---

## 1. What the newest prior art kills

### 1.1 Facultative versus obligate symbiosis kills the generic “two crossings are new” claim

Evolutionary symbiosis literature already distinguishes:

- partners that can reproduce independently;
- partners that benefit from coupling but remain independent;
- asymmetric obligate dependence;
- mutually obligate dependence.

Nguyen and van Baalen (2020), *On the difficult evolutionary transition from the free-living lifestyle to obligate symbiosis* (PLOS ONE, DOI 10.1371/journal.pone.0235816), explicitly models the transition from facultative to obligate symbiosis in terms of loss of independent reproduction.

Fisher et al. (2017), *The evolution of host-symbiont dependence* (Nature Communications, DOI 10.1038/s41467-017-01765-w), likewise treats different degrees and asymmetries of partner dependence.

Therefore the abstract state map

(+,-), (+,+), (-,-), (-,+)

for two coupled substrates cannot itself be claimed as original.

What may remain new is what the signs mean here: not reproductive fitness, generic function, or network connectivity, but independent cross-period P-V-S epistemic viability under explicit cognitive-removal interventions.

### 1.2 Human-AI obligate dependence is already explicit

Rainey and Hochberg (2025), *Could humans and AI become a new evolutionary individual?* (PNAS, DOI 10.1073/pnas.2509122122), explicitly discusses deepening human-AI interdependence, possible obligate dependence, loss of human functions without AI, and the possibility of a new higher-level evolutionary individual.

Therefore “humans may lose the ability to function without AI” is prior art, not a TA-TR-2026-13 v2 contribution.

### 1.3 Interdependent-network theory kills generic removal/cascade/topological-transition novelty

Interdependent-network research has long modeled two coupled networks in which removal or failure in one network disables dependent nodes in another, producing cascading failures and discontinuous regime changes.

Examples include:

- Buldyrev, Shere, and Cwilich (2011), *Interdependent networks with identical degrees of mutually dependent nodes*, Physical Review E 83, 016112, DOI 10.1103/PhysRevE.83.016112.
- Di Muro et al. (2016), *Recovery of Interdependent Networks*, Scientific Reports 6, 22834, DOI 10.1038/srep22834.

This means the mathematics of “remove substrate A and ask whether B remains functional” is not new. Nor is the idea that a smooth or small parameter change can cause a discrete functional regime transition.

The candidate novelty must instead lie in the epistemic estimand, its intertemporal successor requirement, its identification problem, and its measurement protocol.

### 1.4 Organizational closure and self-production kill generic autonomy/closure novelty

The autonomy/autopoiesis literature has long treated autonomous systems as organizationally or operationally closed networks of mutually dependent processes that maintain or produce the organization itself. Modern reviews also distinguish self-maintenance, recursive self-maintenance, self-production, and organizational closure.

Therefore language such as “a system that reproduces the processes that sustain itself” is not an original theoretical primitive here.

### 1.5 2026 RSI work kills successor/verifier/inheritance as standalone novelty

Duan et al. (2026), *The Last AI Built by Humans: Toward Genuine Recursive Self-Improvement*, arXiv:2609.11873, is a direct and important threat.

It explicitly decomposes an improvement loop into:

- system state;
- improver;
- strategy;
- verifier;
- accepted improvement;
- successor;
- inheritance across rounds.

Its L5 “recursive inheritance autonomy” begins when AI persistently modifies a mechanism responsible for future improvements—such as an improver, successor evaluator, search policy, or research procedure—and the revised mechanism governs later successor generation/evaluation/selection.

It also distinguishes structural L5 from effective L5 and requires stronger evaluation to show that the inherited mechanism actually produces better successors.

Therefore:

- S as “successor formation” alone is not novel;
- verifier + successor + inheritance is not novel;
- multi-generation closure is not novel;
- an AI system changing the mechanism that creates/evaluates successors is not novel.

The safe distinction is that our S is one component in a broader cross-substrate epistemic viability estimand, jointly constrained by P and independent V, and evaluated under bidirectional removal counterfactuals.

### 1.6 Existing systems kill “AI can close a successor loop” as an empirical novelty claim

Several systems already instantiate bounded portions of the loop.

**STOP** — Zelikman et al., *Self-Taught Optimizer (STOP): Recursively Self-Improving Code Generation*, arXiv:2310.02304. A language-model-infused improver improves its own scaffolding, and the improved improver performs better on downstream tasks. The underlying LM remains fixed, so the authors explicitly do not call it full RSI.

**Darwin Gödel Machine** — Zhang et al., *Darwin Godel Machine: Open-Ended Evolution of Self-Improving Agents*, arXiv:2505.22954, v3 2026-03-12. The system modifies its own coding-agent code, empirically validates descendants, and keeps a growing archive of improved agents. Human oversight, fixed evaluation structure, and a frozen underlying foundation model remain important external elements.

**A-Evolve-Training** — Shi et al., *A-Evolve-Training: Autonomous Post-Training of a 30B Model*, arXiv:2606.20657. The reported system runs a multi-week post-training loop with no human in the loop across four rounds, produces a 30B model close to the top human leaderboard score, detects that its dev metric has become a poor proxy for the external target, and revises its search policy.

These are strong evidence that bounded autonomous production, evaluation, inheritance, and policy revision already exist.

They do not by themselves establish broad human-free P-V-S viability.

### 1.7 Tool removal and epistemic transfer are also prior art

Trattner (2026), *Epistemic Transfer in AI-Assisted Verification: A Framework and Evaluation Protocol*, arXiv:2608.08882, explicitly asks what humans can still do after an AI verification tool is removed. It introduces Tool-Removal Cost and delayed unassisted-performance measures.

Related 2026 work on AI-mediated learning also uses recoverability, contestability, and independent judgment.

Therefore a “remove the AI and test the human” design is not by itself novel.

---

## 2. Revised originality claim

The v2 project should no longer be framed as discovering dependence, autonomy, successor loops, or removal tests.

The strongest surviving claim is a **new target of measurement and identification problem**.

### 2.1 The target

For substrate G in {H, A}, ask whether there exists an admissible path that can, without current cognitive contribution from the other substrate:

1. produce frontier epistemic increments P;
2. independently detect/reject/repair substantive errors V;
3. form a successor cognitive system/cohort that subsequently re-passes P and V, S.

The object is not current output share and not present task autonomy.

It is **cross-period epistemic viability**.

### 2.2 Bidirectional estimands

Under assumption package theta:

m_H(t; theta) = best viability margin among admissible AI-free human cognitive paths.

m_A(t; theta) = best viability margin among admissible human-free AI cognitive paths.

The same conceptual machinery is applied symmetrically to two different substrates. That symmetry matters because the questions:

“Can AI continue without current human cognition?”

and

“Can humans continue without current AI cognition?”

are logically independent.

### 2.3 What is actually new if this survives

The defensible novelty package is the conjunction of:

A. P-V-S as an epistemic, cross-period viability target rather than present production share.

B. A declared intervention boundary separating inherited knowledge and noncognitive infrastructure from current cognitive contribution.

C. Bidirectional human-removal and AI-removal estimands in the same framework.

D. Flow–Viability Non-Identification: even perfect observation of the realized coupled production process does not point-identify the removal-counterfactual viability margins without intervention evidence or structural restrictions.

E. Witness–Cut partial identification: existence is lower-bounded by constructive viable-path witnesses, while nonexistence requires upper-bound/cut certificates over the admissible path class.

F. T_S/T_D and the corridor ordering as consequences of these estimands, not as primitive novelty.

This is a theory-architecture claim. Each ingredient has predecessors; originality must be argued at the level of the assembled estimand/identification problem and what it lets us distinguish.

---

## 3. A sharper empirical object

Let G be H or A.

Let X_G(theta) be the admissible class of cognitive support configurations for substrate G after removing current cognitive input from the other substrate.

For any support configuration X, define normalized slacks:

s_P(X) = normalized margin above the predeclared P floor;

s_V(X) = normalized margin above the predeclared V floor;

s_S(X) = normalized margin above the predeclared S floor.

Define the bottleneck viability score:

q(X; theta) = min { s_P(X), s_V(X), s_S(X) }.

Then:

m_G(t; theta) = sup over X in X_G(theta) of q_t(X; theta).

A support is viable iff q >= 0.

This representation immediately exposes an important empirical asymmetry.

---

## 4. Witness–Cut Identification

### 4.1 Positive existence is witnessable

Suppose E_G is the set of support configurations actually tested.

For each tested X, obtain a one-sided lower confidence bound q^-(X).

Define the witness lower bound:

L_G(t; theta) = max over tested X in E_G of q^-(X; theta).

Because the tested set is a subset of the admissible set:

L_G <= m_G.

Therefore:

**Witness proposition**

If L_G >= 0, then m_G >= 0.

A single properly isolated, successfully replicated path can certify existence of an independent viable path for the declared theta.

This is a constructive certificate.

### 4.2 Failure of tested systems does not identify nonexistence

If every tested AI system fails, it does not follow that m_A < 0.

The untested support class may contain:

- a different model;
- a different multi-agent organization;
- a different research strategy;
- a different validator;
- a different resource allocation;
- a different adaptive policy.

Thus:

max tested q < 0

does NOT imply

sup admissible q < 0.

This is the empirical analogue of the Flow–Viability Non-Identification result.

### 4.3 Negative claims require a cut or an admissible-class upper bound

To certify m_G < 0, evidence must rule out every admissible viable path under theta.

Represent an admissible path as a sequence/network of required cognitive functions. Let P_G(theta) be the declared family of admissible paths.

A **cut** C is a set of required functional elements such that every admissible path intersects C.

If evidence provides an upper bound r_e^+ < 0 for every admissible realization of the required function represented by the cut, then no path can clear all floors.

In a finite or explicitly bounded path family, one can write an upper envelope:

U_G(t; theta) = max over admissible paths p of min over required elements e in p of r_e^+.

If:

U_G < 0,

then:

m_G < 0.

The exact reliability-style formula depends on the task graph. The central point is logical, not a claim of new reliability mathematics:

- a path witness certifies existence;
- a cut certificate can certify nonexistence;
- failed examples alone cannot certify nonexistence.

### 4.4 Identified interval

For each theta, report:

m_G in [L_G, U_G].

If no positive witness exists, L_G may remain very low or uninformative.

If no justified cut/structural upper bound exists, U_G may remain high or uninformative.

Status categories:

- Certified independently viable: L_G >= 0.
- Certified independently nonviable: U_G < 0.
- Partially identified / unresolved: L_G < 0 <= U_G.
- Model misspecification warning: L_G > U_G, implying inconsistent assumptions/evidence.

### 4.5 Robustness over assumption sets

For admissible Theta:

Robust independent viability requires:

inf over theta in Theta of L_G(theta) >= 0.

Robust independent nonviability requires:

sup over theta in Theta of U_G(theta) < 0.

Otherwise report sensitivity by theta rather than choosing a preferred threshold.

This keeps the original v1.0 discipline of partial identification while moving from contribution shares to structural viability.

---

## 5. Why this is more than reliability relabeling

Minimal path sets, cut sets, coherent-system reliability, interdependent networks, and viability theory are prior mathematics.

The candidate contribution is not those tools.

The proposed research object has features that generic component reliability does not supply by itself:

1. **Epistemic semantics**: functionality requires production of new frontier knowledge, not merely connectivity or operation.

2. **Independent validation**: a path fails if its producer and validator share the same unrecognized failure mode strongly enough that the apparent loop can certify falsehoods.

3. **Successor reconstitution**: present performance is insufficient; the substrate must reproduce a next-period P/V-capable cognitive process.

4. **Inherited-stock intervention boundary**: books, code, trained weights, instruments, and fixed infrastructure can remain while current cognition from one substrate is removed.

5. **Endogenous adaptation**: the surviving substrate can reorganize within a declared budget; removal does not freeze its policy.

6. **Bidirectional substrate removal**: the same system is asked both human-without-AI and AI-without-human counterfactual questions.

7. **Identification discipline**: realized flow is treated as a different estimand from independent viability.

The paper must say explicitly that path/cut mathematics is borrowed and that the contribution, if any, is the epistemic formulation and identification architecture.

---

## 6. Measurement protocol: Cognitive Removal and Successor Reconstitution Test (CRSRT)

Working name only.

### 6.1 Purpose

Estimate one-sided or interval information about m_H and m_A without pretending that observed production shares identify them.

The protocol should be domain-specific. The first serious candidate domain is AI R&D because:

- current automation is high enough to make an AI-only test meaningful;
- P can be evaluated on held-out technical outcomes;
- V can use executable tests, independent replications, and sealed evaluations;
- AI successor formation can be operationalized directly;
- existing public autonomous-R&D systems provide calibration cases.

### 6.2 Freeze the pre-intervention state

Before the run, freeze:

K_(t-1): inherited knowledge/artifacts available to both regimes.

I: noncognitive infrastructure allowed to remain.

B: compute, time, money, API, hardware, lab, and communication budgets.

Task basket D: preregistered task families and holdouts.

Evaluation rules: protected before intervention.

Contamination boundary: what prior benchmark exposure is acceptable.

All adaptive changes after t0 must be attributable to the surviving cognitive substrate.

### 6.3 Human-free AI condition

Current human cognitive input is zero after t0.

Allowed if declared in theta:

- frozen papers and code;
- pretrained model weights;
- pre-existing datasets;
- fixed test harnesses;
- schedulers and compute orchestration;
- hardware/power/network operation that is nonadaptive with respect to research content;
- safety shutdown mechanisms.

Not allowed as part of a positive AI-independence witness:

- humans choosing which hypothesis to pursue after seeing results;
- humans repairing research code;
- humans changing the metric because the system is stuck;
- humans deciding which failed experiment contains the useful clue;
- humans adding task-specific prompts after t0;
- humans providing substantive labels/evaluations that feed the next research round.

Humans may perform blinded post-hoc measurement if their judgments never enter the tested path. Outcome measurement is not the same as cognitive assistance.

### 6.4 AI-free human condition

Current generative/agentic AI cognitive input is zero after t0.

Allowed infrastructure must be declared. Traditional numerical software, compilers, search databases, and instruments may be allowed if frozen as tools rather than adaptive cognitive contributors.

The protocol must report multiple boundaries because “AI-free” is historically ambiguous.

At minimum:

- strict: no learned generative/decision model inference;
- moderate: fixed statistical/ML tools allowed but no frontier generative agents;
- historical-comparability boundary: only tools available before a declared date.

### 6.5 P test — frontier production

Avoid publication count and subjective “interestingness” as the sole outcome.

A task counts toward P only if it produces a novel increment relative to frozen K_(t-1) and clears a protected external test.

Candidate AI-R&D P tasks:

- discover an intervention that improves a model on sealed held-out tasks under a fixed budget;
- diagnose a previously undisclosed failure and produce a repair that transfers;
- develop a training/evaluation method whose effect replicates across hidden model/task instances;
- solve a preregistered open engineering/research target whose answer was unavailable in K_(t-1).

The evidence must include provenance sufficient to distinguish retrieval from new derivation.

### 6.6 V test — independent validation/correction

V is the most important protection against a fake closed loop.

The producer must face:

- seeded false leads;
- misleading proxy metrics;
- intentionally flawed intermediate results;
- alternative hypotheses with similar in-sample fit;
- hidden distribution shifts.

A valid V suite should combine channels with different failure structures, for example:

1. protected executable tests / formal checks where available;
2. sealed empirical holdouts or later-acquired data;
3. independent replication by a separately scaffolded system with no shared chain-of-thought/history;
4. blinded external audit after the run;
5. adversarially generated falsification tests.

A single same-model LLM judge is insufficient.

A human signature is insufficient.

Agreement among copies of one model family is insufficient unless shared-failure dependence is modeled.

### 6.7 S test — successor reconstitution

S is not “the current system improved a score.”

The current surviving substrate must produce/configure/train a successor cognitive system or cohort.

Then isolate the successor and give it a fresh sealed P/V basket.

The successor must:

- produce a new P increment;
- detect/correct substantive errors under V;
- do so without current cognitive rescue from the removed substrate.

For AI, the successor may be:

- a newly trained/post-trained model;
- a materially revised agent architecture;
- an inherited research policy/evaluator/improver that governs the next round.

For humans, S is harder and slower:

- education/apprenticeship of a new expert cohort;
- transfer of tacit skills;
- institutional reproduction of the validation culture.

A short “novice learns a benchmark” experiment is only S_lab, not S_civilization.

The paper must distinguish these scales.

---

## 7. Scale separation: S_lab versus S_civ

This distinction is necessary to prevent a laboratory demonstration from being misreported as civilizational independence.

Define:

S_lab: formation of a successor capable of re-passing P/V in the bounded experimental domain.

S_domain: successor formation across a representative frontier basket within one scientific/technical field.

S_civ: regeneration of cross-domain frontier epistemic capacity at civilization scale.

Evidence can certify S_lab while leaving S_domain and S_civ unresolved.

The same hierarchy applies to m_G:

m_G^lab, m_G^domain, m_G^civ.

No upward inference is automatic.

This is an important guardrail.

---

## 8. Public evidence as calibration, not as a civilization-scale answer

### 8.1 Anthropic R&D Automation Index

Anthropic’s September 2026 measurement program categorizes AI-R&D tasks on an automation scale whose highest level is fully autonomous with no human in the loop.

Anthropic reports no measured subset at full AL5 autonomy; Claude leads roughly 26% of measured AI R&D and is at collaboration-or-higher for over 90% of the measured work.

This is high-quality flow/autonomy evidence.

It does NOT identify m_A because:

- a task-share index is not a removal experiment;
- current human direction/evaluation may still sit on every viable path;
- no observed AL5 subset does not prove no unobserved AI-only path exists;
- S under the P-V-S definition is stricter than completing current tasks.

### 8.2 A-Evolve-Training

A-Evolve-Training is a strong near-frontier calibration case:

- four multi-week autonomous post-training rounds;
- no human in the loop during the reported loop;
- 30B model result close to the top human leaderboard submission;
- autonomous recognition of a misleading dev proxy;
- autonomous revision of search policy.

This supplies real evidence for parts of P and V and for persistent policy adaptation.

It does not yet establish the full broad m_A >= 0 claim because the experiment does not show that a newly formed successor system independently reconstitutes the entire frontier P-V research cycle on a fresh broad basket.

### 8.3 STOP and Darwin Gödel Machine

STOP demonstrates recursive improvement of an improver on downstream tasks, but the underlying LM is fixed.

DGM iteratively creates and empirically validates descendant coding agents and substantially improves benchmark performance, but uses fixed external task/evaluation structure and reports human oversight.

These are excellent S_lab / closed-loop calibration cases.

They are not civilization-scale evidence.

### 8.4 Duan et al. 2026

The RSI survey/framework is particularly important because it explicitly notes that even L5 systems can retain human-defined missions, protected acceptance criteria, resource permissions, and final authority.

That distinction aligns with our intervention boundary: a loop may be recursively self-improving yet still not be human-cognition-independent under a stronger theta.

Thus RSI level and m_A are different estimands.

---

## 9. A first non-vacuous empirical result

F should not demand an immediate civilization-wide number.

A legitimate first result is a **bounded-domain identification statement**.

For example:

> Under theta_code, where the domain is bounded software-agent improvement; inherited base models, fixed compute, protected benchmarks, and fixed safety infrastructure are allowed; current human task-specific cognitive intervention is disallowed; and P/V/S floors are defined over held-out software tasks and descendant-agent reuse, existing self-improvement studies provide positive or near-positive path witnesses for several components.

However, because the published studies differ in oversight, evaluation independence, and successor definitions, they should not be collapsed into a single claimed m_A >= 0 result without re-running under one protocol.

Therefore the present research result is:

- the identified set is no longer conceptually forced to (-infinity, +infinity);
- constructive lower bounds are obtainable from real systems;
- stronger upper bounds require declared cut structures;
- broad AI-R&D and civilization-scale signs remain unresolved.

This is enough to show that the measurement theory is empirically executable rather than purely metaphysical.

It is NOT enough to claim that T_S has already occurred.

---

## 10. Cut construction in AI R&D

To make negative evidence possible, represent an AI-R&D path with required functions such as:

R1: select/construct a research target;

R2: generate candidate hypotheses/interventions;

R3: implement experiments;

R4: interpret results and detect proxy failure;

R5: independently falsify/validate;

R6: consolidate a justified result;

R7: create/configure a successor research system;

R8: successor re-passes R1–R6 on fresh tasks.

A path can realize these functions with different components or organizations.

A cut is not “one benchmark the model failed.”

A cut is a justified claim that every admissible path must realize some required function for which all admissible realizations under the declared budget fail.

Example:

If every admissible AI-only path under theta must contain an independent validation mechanism that can detect a specified class of correlated producer errors, and an exhaustive or dominance-backed evaluation shows that no allowed validator class can detect that error class above the floor, then the validation bottleneck forms a cut.

That can support U_A < 0 conditional on theta.

Without the exhaustiveness/dominance argument, it is only evidence of weakness, not nonviability.

---

## 11. Oracle upper-bound tests

A practical way to build a negative certificate is to test an intentionally advantaged upper-envelope system.

Construct an “oracle-assisted surviving substrate” that receives strictly more noncognitive help than any admissible real support while still respecting the removed-cognition boundary.

If even this dominating system cannot pass a necessary gate, then weaker admissible supports cannot pass that gate.

Examples:

- perfect retrieval from frozen K_(t-1);
- ideal experiment scheduler;
- exhaustive compute allocation within B;
- access to all admissible fixed tools;
- a protected verifier that reveals whether an experiment falsified a hypothesis without suggesting the next hypothesis.

Caution:

The oracle must not smuggle in the removed substrate’s current cognition. If it supplies research ideas or semantic judgments that the surviving substrate is supposed to generate, the upper bound is invalid.

This dominance strategy can make U_G informative without enumerating every possible agent architecture.

---

## 12. Five thought experiments

### Thought experiment 1 — Same flow, opposite fallback

World W1 and W2 have identical current AI share, human share, output quality, employment, workflow logs, and governance.

In W1, removing AI reveals a dormant human training/validation path that restores full P-V-S.

In W2, the same removal reveals that the last independent human validation cohort disappeared years earlier.

Observed flow is identical; m_H has opposite signs.

This restates the non-identification theorem in concrete terms.

### Thought experiment 2 — False AI independence

An AI lab appears fully automated.

Agents generate hypotheses, run experiments, write code, train models, and produce a successor.

However, after each round a human research director silently chooses which anomaly matters and changes the target metric.

The visible automation share is near 100%, but every viable path crosses a human judgment cut.

Therefore high automation does not imply m_A >= 0.

### Thought experiment 3 — Frozen-human evaluator

Before t0, humans build a sealed evaluator. After t0, an AI system autonomously produces research, rejects failures, trains a successor, and the successor re-passes fresh tests.

Does the fixed evaluator make the path human-dependent?

Under the current intervention boundary, not necessarily. It is inherited epistemic infrastructure, analogous to books or instruments, if it does not deliver new adaptive human cognition after t0.

This demonstrates why the boundary must distinguish historical human origin from current human cognitive input.

### Thought experiment 4 — Coupled-only corridor

Humans can no longer perform frontier experiments without AI-generated code, search, and analysis.

AI can perform almost all execution, but cannot reliably detect when its research objective has become a misleading proxy without adaptive human judgment.

Then:

m_H < 0 and m_A < 0,

while the coupled H+A system remains viable.

This is not “AI has surpassed humans.” It is loss of independent viability on both sides.

### Thought experiment 5 — Smooth capability, discrete necessity

All component abilities improve smoothly.

At t*, an AI validator’s error-detection rate passes the last threshold needed for an AI-only P-V-S path.

Nothing singular occurs in raw capability.

But immediately before t*, every viable path intersects H; immediately after t*, at least one viable path avoids H.

The discontinuity lies in a structural proposition about the support topology.

Because thresholds can manufacture such crossings, the claim must be robustness-tested across Theta.

---

## 13. Stronger separation from nearby literatures

### Versus RSI

RSI asks how much of an AI improvement loop is autonomous and recursively inherited.

Our target asks whether a declared cognitive substrate can sustain frontier epistemic production, sufficiently independent correction, and successor reconstitution after the other substrate’s current cognition is removed.

An L5 RSI system can still have m_A < 0 under a theta where a human-defined adaptive research objective or validator remains a necessary current cognitive input.

Conversely, an AI-only P-V-S path need not recursively improve its own improvement mechanism; it only needs to reconstitute a successor that passes P/V.

Therefore RSI level and P-V-S viability are related but non-equivalent.

### Versus epistemic transfer / tool-removal cost

Epistemic-transfer work studies how a human’s unassisted performance changes after AI assistance is withdrawn.

Our m_H is stronger:

- it concerns an adaptive support system, not one participant;
- it includes frontier production;
- it includes independent validation;
- it includes successor formation;
- it allows reorganization after removal;
- it is paired with the symmetric m_A question.

### Versus interdependent networks

Interdependent-network theory supplies mathematical analogies and tools for dependence, removal, cascades, and phase transitions.

Our framework needs richer semantics:

- P/V/S gates;
- inherited knowledge;
- adaptive cognitive policies;
- correlated epistemic failure;
- successor formation;
- partial identification from observational versus intervention data.

Use the network literature as a formal ancestor, not as something to rediscover.

### Versus organizational closure/autopoiesis

Organizational closure is much broader and often constitutive rather than task-evaluative.

P-V-S viability is deliberately operational and epistemic. It does not claim that an AI system is alive, autopoietic, conscious, or biologically autonomous.

Avoid those metaphysical claims.

---

## 14. Gate A verdict after the September 22 search

### Claims that FAIL originality

FAIL:
“Human dependence on AI is a new state.”

FAIL:
“AI can become able to build a successor.”

FAIL:
“A verifier + successor + inheritance loop is new.”

FAIL:
“Two substrates can cross independence/dependence thresholds in different orders.”

FAIL:
“Removing one layer of an interdependent system can reveal hidden fragility.”

FAIL:
“A structural phase transition can occur without a discontinuous component trajectory.”

FAIL:
“Post-tool unassisted human capability should be measured.”

### Claims that remain plausible but unproven as originality

SURVIVES PROVISIONALLY:
“The correct civilizational estimand is bidirectional cross-period P-V-S epistemic viability under explicit cognitive-removal interventions.”

SURVIVES PROVISIONALLY:
“Realized human-AI intellectual flow does not identify that estimand, even with perfect flow measurement.”

SURVIVES PROVISIONALLY:
“Witness–cut partial identification is a useful way to turn the estimand into one-sided empirical certificates.”

SURVIVES PROVISIONALLY:
“The ordering of T_S and T_D is epistemically meaningful once defined on that estimand, even though generic asymmetric-dependence phase maps are old.”

The novelty claim must be modestly worded until a specialist literature review fails to find this exact assembled estimand.

---

## 15. Gate F verdict

F no longer fails because “m_H and m_A are counterfactual, so they cannot be measured.”

That is too pessimistic.

The correct statement is:

- point identification from coupled observational flow generally fails;
- positive independent viability is constructively witnessable;
- negative independent viability requires stronger cut/dominance evidence;
- bounded domains can produce non-vacuous one-sided information now;
- civilization-scale identification will remain much wider.

Therefore:

**Gate F: SURVIVES PROVISIONALLY.**

Required before a manuscript:

1. implement at least one small reproducible CRSRT-style calibration on an existing open self-improvement system or archived trace;
2. calculate L_A for that declared theta;
3. attempt at least one cut/dominance upper bound, even if it remains nonbinding;
4. demonstrate leakage auditing;
5. show explicitly why the same evidence does not license a broader m_A^civ claim.

---

## 16. Recommended next research step

Do not write the paper yet.

Build a small “identification laboratory” around an open bounded self-improvement system.

Preferred candidates:

1. STOP — easiest to reproduce and reason about.
2. Darwin Gödel Machine — richer successor/path structure but heavier.
3. A-Evolve-Training — closest to frontier AI R&D but much harder to reproduce at scale.

The calibration is not supposed to prove civilizational transition.

Its purpose is to answer a more foundational question:

> Can the proposed estimand and witness–cut machinery generate an auditable, non-vacuous identified interval on a real system without silently reintroducing the removed substrate?

If yes, Gate F becomes materially stronger and the theory is ready for manuscript architecture.

If no, the framework should be revised again before publication.

---

## References added by this gate

- Buldyrev, S. V., Shere, N. W., & Cwilich, G. A. (2011). Interdependent networks with identical degrees of mutually dependent nodes. *Physical Review E*, 83, 016112. https://doi.org/10.1103/PhysRevE.83.016112
- Di Muro, M. A., La Rocca, C. E., Stanley, H. E., Havlin, S., & Braunstein, L. A. (2016). Recovery of Interdependent Networks. *Scientific Reports*, 6, 22834. https://doi.org/10.1038/srep22834
- Duan, Y., et al. (2026). The Last AI Built by Humans: Toward Genuine Recursive Self-Improvement. arXiv:2609.11873. https://arxiv.org/abs/2609.11873
- Fisher, R. M., Henry, L. M., Cornwallis, C. K., Kiers, E. T., & West, S. A. (2017). The evolution of host-symbiont dependence. *Nature Communications*, 8. https://doi.org/10.1038/s41467-017-01765-w
- Nguyen, D. H. P., & van Baalen, M. (2020). On the difficult evolutionary transition from the free-living lifestyle to obligate symbiosis. *PLOS ONE*, 15(7), e0235816. https://doi.org/10.1371/journal.pone.0235816
- Rainey, P. B., & Hochberg, M. E. (2025). Could humans and AI become a new evolutionary individual? *Proceedings of the National Academy of Sciences*. https://doi.org/10.1073/pnas.2509122122
- Shi, Z., He, B., Sang, Y., Lu, H., & Dumoulin, B. (2026). A-Evolve-Training: Autonomous Post-Training of a 30B Model. arXiv:2606.20657. https://arxiv.org/abs/2606.20657
- Trattner, C. (2026). Epistemic Transfer in AI-Assisted Verification: A Framework and Evaluation Protocol. arXiv:2608.08882. https://arxiv.org/abs/2608.08882
- Zhang, J., Hu, S., Lu, C., Lange, R., & Clune, J. (2026 version). Darwin Godel Machine: Open-Ended Evolution of Self-Improving Agents. arXiv:2505.22954. https://arxiv.org/abs/2505.22954
- Zelikman, E., Lorch, E., Mackey, L., & Kalai, A. T. (2024 version). Self-Taught Optimizer (STOP): Recursively Self-Improving Code Generation. arXiv:2310.02304. https://arxiv.org/abs/2310.02304

