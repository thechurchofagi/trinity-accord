# TA-TR-2026-13 v2 Research Gate — Identification and Viable Path Sets

Date: 2026-09-22
Status: RESEARCH ONLY. Not a manuscript. Not authorized for DOI publication.
Published v1.0 remains unchanged: DOI 10.5281/zenodo.22866775.

## 1. Result after Gates B/C/D

The surviving candidate is NOT:
- an AI output-share threshold;
- rate-induced tipping by itself;
- recursive self-improvement by itself;
- human deskilling or knowledge collapse by itself;
- non-human knowledge or independent validation by itself;
- generic human-AI symbiosis, coevolution, or obligate dependence;
- generic viability, minimal-path, or reliability theory.

The surviving object is the existence and loss of cross-period viable cognitive paths that jointly sustain:
P = frontier epistemic production;
V = independent error detection/correction;
S = successor-capacity formation.

The candidate AGI-era contribution is the separation between:
1. AI independent sufficiency: a viable P-V-S path exists without current human cognitive input.
2. Human dependence on AI: no viable P-V-S path remains without current AI cognitive input.

These events need not coincide and cannot be inferred from current production shares alone.

## 2. Non-circular operational definitions

### 2.1 P — Frontier epistemic production

Do not define "frontier" as "whatever a frontier actor does."

Freeze an information set K_(t-1) and a domain-specific external evaluation protocol before the test.

A production event counts toward P only if it creates an epistemic increment relative to K_(t-1), operationalized by at least one pre-specified criterion such as:
- resolving a pre-registered open problem;
- producing a novel prediction confirmed on held-out or later-acquired evidence;
- producing an experimentally validated new result;
- improving a domain frontier under contamination-controlled evaluation;
- discovering a new construction, proof, design, mechanism, or causal relation that survives independent validation.

P is a vector across domain task families, not a universal "intelligence unit."

### 2.2 V — Independent validation/correction

V is not self-consistency, self-critique, peer agreement among copies of the same model, or a human signature.

A validation path counts only if it can:
- detect substantive false claims or failures;
- reject or repair them;
- produce an alternative when the original path is wrong;
- draw on an evidential/evaluative channel with sufficiently non-shared failure modes relative to the producer.

This is consistent with current independent-validation literature, including Lewin (2026) and Vallverdu (2026). Independence may be graded rather than binary.

### 2.3 S — Successor-capacity formation

Avoid the circular definition "S means the successor has S."

One-step definition:
Under a declared intervention boundary, the current substrate must be able to create, train, configure, or institutionally reproduce a successor cognitive system/cohort which, after formation, independently re-passes the P and V test suite at or above pre-registered floors.

Multi-period sustainability is then a property of the induced transition dynamics, not part of the one-step definition itself.

For humans, S may include education, apprenticeship, practice, mentoring, institutional reproduction, and tacit-skill transfer.
For AI, S may include AI R&D, model/data/evaluation design, coding, experimentation, training, system integration, and successor evaluation.
The physical infrastructure boundary must be stated separately.

## 3. Cognitive intervention boundary

"Human-only" and "AI-only" refer to cognitive contribution, not physical autarky.

At intervention time t:
- inherited knowledge stock K_(t-1) is frozen as common history;
- declared noncognitive infrastructure I is held available;
- current-period cognitive contributions from the removed substrate are set to zero;
- the surviving substrate may adapt, reorganize, retrain, simplify, and allocate resources within a declared envelope B.

This prevents a false test in which AI is required to mine silicon or humans are required to abandon books, computers, power grids, and instruments.

## 4. Viable cognitive support sets

Let C be the set of cognitive components: human expert cohorts, AI systems, independent validators, training/evaluation organizations, and other explicitly modeled cognitive nodes.

For an assumption package theta = (D, tau, B, I, thresholds, validation-independence rule, inherited-stock boundary), define:

Phi_t(X; theta) = 1

if there exists an admissible adaptive policy using cognitive support set X that keeps P and V above their floors and repeatedly produces successors that re-pass P and V over horizon tau.

A set X is a viable cognitive support set when Phi_t(X;theta)=1.

A minimal viable cognitive support set is viable and no proper subset is viable.

This directly borrows the minimal-path-set logic of coherent reliability systems. The mathematics is established reliability theory and is NOT an originality claim.

Let M_t(theta) be the family of minimal viable cognitive support sets.

Let H be human-cognition nodes and A be AI-cognition nodes.

AI independent sufficiency at (t,theta):
there exists M in M_t(theta) such that M intersect H is empty.

Human dependence on AI at (t,theta):
for every M in M_t(theta), M intersect A is non-empty.

Human structural necessity:
for every M in M_t(theta), M intersect H is non-empty.

These three statements are distinct.

## 5. Continuous viability margins

For estimation, binary path existence is too brittle. Attach a margin to each support set.

For support X define q_t(X;theta) as the maximal worst-case normalized slack above the P/V/successor floors over the declared horizon.

Define:

m_H(t;theta) = max q_t(X;theta) over all viable candidate X with X intersect A empty.

m_A(t;theta) = max q_t(X;theta) over all viable candidate X with X intersect H empty.

Interpretation:
m_H >= 0: at least one AI-free human cognitive path is viable.
m_H < 0: no AI-free path reaches all floors.

m_A >= 0: at least one human-free AI cognitive path is viable.
m_A < 0: no human-free path reaches all floors.

The binary path-set and continuous-margin formulations are two views of the same object.

## 6. Two transition events

For fixed theta:

T_S(theta) = first t such that m_A(t;theta) >= 0.
AI independent-sufficiency crossing.

T_D(theta) = first t such that m_H(t;theta) < 0.
Human-dependence crossing.

Define the Sufficiency-Dependence Gap:

Delta(theta) = T_D(theta) - T_S(theta).

Delta > 0:
AI sufficiency arrives first; a dual-viability / redundancy corridor can exist.

Delta < 0:
human dependence arrives first; a coupled-only dependence corridor can exist before an AI-only path is sufficient.

Delta = 0:
simultaneous crossing, a limiting case unless a mechanism forces coincidence.

## 7. Corridor proposition

Assume m_H(t) and m_A(t) are continuous and begin with signs (+,-), later ending with signs (-,+).

If their zero crossings are distinct, the trajectory must pass through either:
- (+,+): both substrates independently viable, or
- (-,-): neither substrate independently viable, while the coupled system may remain viable.

A direct switch from (+,-) to (-,+) without one of those corridors requires simultaneous zero crossing.

This is mathematically elementary; its value is conceptual separation, not mathematical novelty.

## 8. Flow-Viability Non-Identification Theorem

### Statement

Even perfect observation of the realized coupled Human-AI production trajectory does not, without additional intervention data or structural restrictions, identify m_H, m_A, T_S, or T_D.

### Proof construction

Let A_on = 1 denote that current AI cognitive input is available.
Let O_t be the entire observable history under the realized coupled regime, including:
- Human/AI output shares;
- quality;
- workflow logs;
- effective governance;
- employment;
- AI usage;
- current task performance.

Consider any structural model M that reproduces the observed law of O under A_on=1.

Construct two alternative models M+ and M- whose transition functions are identical to M whenever A_on=1, but differ by a term multiplied by (1-A_on) on the human fallback branch.

Because (1-A_on)=0 on every observed coupled-history point, M+ and M- generate exactly the same observed distribution.

Under the intervention do(A_on=0), however, choose the otherwise-unconstrained fallback term so that:
- M+ retains P/V/successor capacity above all floors;
- M- falls below at least one floor.

Therefore M+ and M- are observationally equivalent on the coupled regime but imply opposite signs for m_H.

The same construction applies symmetrically to m_A under removal of current human cognitive input.

Hence m_H and m_A are not point identified from coupled observational data alone.

This is an application of standard counterfactual non-identification / support logic, not a new causal theorem. The substantive result is that realized intellectual-flow accounting and independent cross-period epistemic viability are different estimands.

### Stronger implication

The construction can use smooth structural functions. Therefore smoothness of underlying capability curves does not rescue identification.

With sufficiently flexible unobserved counterfactual branches, the same realized flow history can be consistent with different orders of T_S and T_D.

So:
AI output share, even if measured without error, cannot determine whether AI sufficiency precedes human dependence or vice versa.

## 9. Partial identification instead of false precision

Let Theta be the admissible set of:
- domain baskets;
- horizon lengths;
- resource envelopes;
- inherited-stock boundaries;
- validation-independence criteria;
- P/V floors;
- successor-formation assumptions;
- unobserved fallback-capacity constraints.

Define identified sets:

M_H(t) = { m_H(t;theta): theta in Theta and theta is consistent with evidence }
M_A(t) = { m_A(t;theta): theta in Theta and theta is consistent with evidence }.

Robust human independent viability:
inf M_H(t) >= 0.

Robust human dependence:
sup M_H(t) < 0.

Robust AI independent sufficiency:
inf M_A(t) >= 0.

Robust AI insufficiency:
sup M_A(t) < 0.

Otherwise status is unresolved.

For transition times:

T_S_set = { T_S(theta): theta in Theta and evidence-consistent }
T_D_set = { T_D(theta): theta in Theta and evidence-consistent }.

Define the identified set for the gap:

Delta_set = { T_D(theta)-T_S(theta): theta in Theta and evidence-consistent }.

If inf Delta_set > 0:
robust sufficiency-first / redundancy-first ordering.

If sup Delta_set < 0:
robust dependence-first / coupled-lock-in ordering.

If 0 belongs to Delta_set:
ordering is not identified.

This extends v1.0's partial-identification logic from current contribution shares to structural counterfactual transition states.

## 10. Structural discontinuity without a discontinuous capability curve

The user's "civilizational break" intuition does not require a singular or non-differentiable AI capability curve.

Suppose every component capability c_i(t) evolves smoothly.

The family of feasible minimal cognitive support sets M_t can still change at a time when one support-set viability margin crosses zero.

Then a discrete structural statement such as:

"every viable cross-period frontier path requires human cognition"

can change from true to false while all c_i(t) are smooth.

The discontinuity is therefore in viable-path topology / regime classification, not necessarily in raw model capability.

Caution:
A threshold can manufacture an artificial discontinuity. This is why all claims must be repeated over Theta and reported as robust, refuted, or unresolved.

## 11. Sub-generational compression diagnostic

Let tau_E be the time required to form an independent human expert cohort for the chosen domain.
Let tau_C be the duration of the structural transition corridor.

Define:

Kappa = tau_E / tau_C.

Kappa >> 1 means the structural regime can traverse its transition corridor faster than a newly trained human cohort could be produced.

This captures a potentially important AGI-era time-compression feature, but rate mismatch itself is not claimed as new.

## 12. Strong prior art and what it removes from the novelty claim

### Human-AI hybrid knowledge production
Eccles (2026), "Production of Knowledge in Human-Machine Collaborations: The Hybrid Intelligent Team as Epistemological Form."
It argues that loop-level human-machine ideation can produce warranted knowledge and uses a human coherence anchor/final recognizer.
It does not model successor-capacity viability or T_S/T_D.

### Non-human epistemology and independent validation
Vallverdu (2026), "Xenoepistemics," Philosophies 11(2):57, DOI 10.3390/philosophies11020057.
It explicitly develops non-anthropocentric knowledge, structural epistemic criteria, and independent validation.
It still localizes validation chains in humanly auditable anchors and does not model successor-capacity formation or the T_S/T_D separation.

### Expertise regeneration and validation
Lovett (2026), "The Tragedy of the Cognitive Commons," Human Resource Development Review, DOI 10.1177/15344843261470602.
It links erosion of internalized mastery to the loss of the expertise needed to validate AI.
It does not define AI independent sufficiency as a cross-period P-V-S viability event.

### Knowledge collapse
Acemoglu, Kong, Ozdaglar (2026), NBER w34910, DOI 10.3386/w34910.
It proves that better agentic recommendations can raise current decision quality while eroding human learning incentives and long-run general knowledge.
It does not pair that human-collapse event with an independently defined AI-sufficiency event.

### Human structural necessity in long-horizon workflows
Nadendla (2026), FRFP, DOI 10.5281/zenodo.18529064 / 10.5281/zenodo.19686127.
It formalizes explicit processes versus tacit human correctness judgment and proves non-automation/governance results.
It is a present workflow architecture, not a bidirectional cross-period viability phase map.

### Recursive AI improvement
Burtsev (2026), arXiv:2609.00137, "Recursive Criticality of AI Self-Improvement."
It defines a recursive reproduction number and supercritical self-amplification.
It covers the AI-to-AI improvement loop, not the coupled question of human-independent and AI-independent P-V-S paths.

### Collective knowledge dynamics
Nettasinghe & Zhao (2026), WWW 2026, DOI 10.1145/3774904.3792665.
It jointly models human skill, LLM skill, archive dynamics, human learning from LLMs, and LLM learning from human feedback.
A generic 2x2 mutual-learning matrix is therefore not novel.

### Major evolutionary transitions
Rainey & Hochberg (2025), PNAS, DOI 10.1073/pnas.2509122122.
It explicitly discusses human-AI interdependence, obligate dependence, loss of human functions without AI, and a possible new evolutionary individual.
Therefore "human dependence on AI" is not a new concept.

### Autonomous science
Self-driving laboratory and autonomous-science literatures already contain narrow-domain closed production/experiment/analysis loops.
Therefore P+V closure alone is not new.

## 13. Historical counterexamples that kill weaker claims

### Printing press
Dittmar (2011) documents rapid diffusion from Mainz across Europe during 1450-1500 and large subsequent city-growth effects.
This was a profound information technology revolution, so v2 must not claim earlier civilization was technologically static.
However, diffusion still depended on human printers/apprentices carrying technical know-how; the press did not form a non-human successor-capacity pathway for frontier cognition.

### Electrification and IT
General-purpose-technology research documents decades-long complementary investment and productivity dynamics.
Therefore "large technological revolution" and "institutional lag" are old phenomena.

### Self-hosting compilers
Self-hosting compilers have existed since the early 1960s.
Therefore "software can help reproduce software that builds software" is not an AGI novelty.

### AI-designed AI hardware
AlphaChip has designed layouts used in multiple generations of Google TPUs; AlphaEvolve has optimized next-generation TPU circuitry and AI infrastructure.
Therefore "AI helps create the hardware for future AI" is already real and cannot define the proposed transition.

### Narrow autonomous science and formal mathematics
Self-driving laboratories can design/execute/analyze iterative experiments with limited human input.
Formal theorem-proving systems can generate and mechanically verify proofs in bounded domains.
Therefore "AI can close a production-validation loop" is already too weak a criterion.

The candidate historical discontinuity, if any, must be broader:
a human-free cognitive path sustaining P, independent V, and successor P/V capacity across a broad frontier domain basket, plus a distinct possible loss of the AI-free human path.

## 14. Current empirical boundary, September 2026

Anthropic reports:
- no measured AI R&D subset at full AL5 autonomy;
- Claude leads 26% of measured AI R&D;
- more than 90% is at collaboration-or-higher;
- its automation index is explicitly intended to track proximity to a model autonomously building its successor.

OpenAI reports:
- an automated research intern is now available for well-defined research tasks under human direction;
- an automated AI researcher is a stated 2028 target;
- humans still set research priorities, judge which ideas/results to pursue, and decide whether to scale, pause, or deploy.

These observations show rapid movement in current-flow automation but do not establish robust m_A >= 0 for the P-V-S criterion.

## 15. Gate verdict

Gate B — Definition:
SURVIVES provisionally after replacing circular S with one-step successor re-testing of P and V.

Gate C — Identification:
SURVIVES strongly. A clean observational-equivalence construction establishes that on-path flow data do not identify off-path independent viability.

Gate D — Robustness:
SURVIVES provisionally via partial identification over an admissible assumption set rather than one threshold.

Gate E — Historical:
SURVIVES only in the narrow broad-P-V-S form. Weaker claims are falsified by historical and contemporary counterexamples.

Remaining high-risk gates:
- prove that P/V/S can be operationalized in at least one real domain without smuggling in human authority by definition;
- determine whether the T_S/T_D distinction already exists under another vocabulary in evolutionary-transition, reliability, autonomy, or technology-dependence literature;
- build a measurement protocol that can actually tighten M_H and M_A rather than leave [negative infinity, positive infinity]-style vacuous bounds.

Do not draft a manuscript until those gates are addressed.
