# TA-TR-2026-13 v2 Research Gate — Independent Epistemic Viability

Date: 2026-09-22
Status: RESEARCH ONLY. Not a manuscript. Not authorized for DOI publication.
Published v1.0 remains unchanged: DOI 10.5281/zenodo.22866775.

## 1. Result of the second originality pressure test

The following candidate claims are NOT sufficient foundations because close or direct prior art exists:

- rate-induced or pacing failure under fast AI change;
- recursive AI R&D and self-improvement;
- AI generation time as a driver of acceleration;
- human skill decay and knowledge-regeneration failure;
- cognitive commons and loss of validation expertise;
- human-AI coevolution;
- major evolutionary transitions / new cognitive substrates;
- autonomous science and closed-loop experimentation;
- AI self-correction and external validation;
- human tacit judgment as a present structural requirement;
- counterfactual AI-withdrawal tests;
- viability theory, minimal path sets, or obligate/facultative dependence as mathematics;
- intelligence becoming reproducible capital;
- generic production of future researchers or human capital.

The v2 theory must use those literatures as predecessors, not rebrand them.

## 2. The surviving object

The strongest surviving object is not current intellectual output. It is:

**whether a declared cognitive substrate possesses an independently viable, cross-period frontier epistemic path.**

For a domain basket D, horizon tau, resource envelope B, inherited stock K_(t-1), and explicit infrastructure boundary I, define three requirements:

P — Frontier production:
The substrate can generate nontrivial new intellectual outputs that meet a declared external validation standard.

V — Independent validation:
The substrate can detect, reject, repair, and replace substantive errors through an evidence/evaluation path with sufficiently non-shared failure modes. Self-review by the same failure channel is not automatically independent validation.

S — Successor-capacity formation:
The substrate can create, train, or otherwise reproduce enough next-period cognitive capacity to keep P and V viable across the chosen horizon.

The object being tested is therefore not "can X do a task?" but:

**does there exist an admissible X-only cognitive trajectory that keeps P, V, and S jointly above their declared floors?**

"X-only" is cognitive, not physical autarky. Historical knowledge stock and declared noncognitive infrastructure are held fixed at the intervention boundary. The other substrate contributes no new cognition after the intervention time.

## 3. Viability-set formulation

Let X be H (human cognition) or A (AI cognition).

Let Pi_X(B,I) be the set of admissible adaptive policies available to X under the declared resource and infrastructure boundaries.

Let C_r(pi,t,u) be achieved capacity on requirement r in {P,V,S} at future time t+u.

Let theta_r be preregistered viability floors.

Define the independent epistemic viability margin:

m_X(t;D,tau,B,I)
=
sup over pi in Pi_X
inf over 0<=u<=tau
min over r in {P,V,S}
[ C_r(pi,t,u)/theta_r - 1 ].

Interpretation:

m_X >= 0:
at least one X-only adaptive trajectory keeps all three requirements viable over the horizon.

m_X < 0:
no admissible X-only trajectory keeps the full frontier epistemic cycle viable.

The exact metric is provisional. The important object is the existence/nonexistence of a viable path, which is naturally related to viability-kernel theory. Viability mathematics itself is not claimed as new.

Define joint human-AI margin m_HA analogously.

## 4. Two transition events that must not be conflated

### AI independent-sufficiency crossing

T_S = first time t at which m_A(t) >= 0.

Interpretation:
A current-human-cognition-free AI path becomes sufficient, under the declared boundary, to sustain frontier production, independent correction, and successor-capacity formation.

This is stronger than:
- AI writes most code;
- AI does most current R&D labor;
- AI can run a narrow autonomous science loop;
- AI can propose its own improvements.

### Human dependence crossing

T_D = first time t at which m_H(t) < 0.

Interpretation:
Without current AI cognitive contribution, the human cognitive subsystem no longer has an admissible path that sustains the same declared frontier cycle.

This is stronger than:
- people use AI a lot;
- human production share falls;
- humans become less productive without AI on one task;
- one profession becomes deskilled.

The central separation is:

AI sufficiency is not human dependence.

T_S and T_D are logically distinct events.

## 5. Four structural regimes

Assume the coupled system remains viable (m_HA >= 0).

1. Human-independent / AI-not-independent
   m_H >= 0, m_A < 0.

2. Dual independent viability
   m_H >= 0, m_A >= 0.

3. Coupled-only viability
   m_H < 0, m_A < 0, m_HA >= 0.

4. AI-independent / human-not-independent
   m_H < 0, m_A >= 0.

The four-quadrant logic resembles obligate/facultative dependence in ecology and is NOT itself an originality claim.

## 6. Corridor theorem candidate

Let t -> (m_H(t), m_A(t)) be continuous.

Suppose the system begins in:
m_H > 0, m_A < 0,

and later reaches:
m_H < 0, m_A > 0.

Then any continuous path between those regimes must either:

- enter the dual-independent quadrant (m_H>0, m_A>0), or
- enter the coupled-only quadrant (m_H<0, m_A<0), or
- pass through the simultaneous boundary point m_H=m_A=0.

Therefore a direct substrate switch without an intermediate structural corridor requires a simultaneous crossing. Under additional monotonicity assumptions, exactly one corridor is traversed.

This theorem is mathematically elementary. Its value, if any, is conceptual and empirical: it separates two events that current AGI discourse commonly collapses.

Define the sufficiency-dependence gap:

Delta = T_D - T_S.

Delta > 0:
AI sufficiency comes first. There is a possible redundancy interval in which both substrates retain independent viable paths.

Delta < 0:
human dependence comes first. There is a possible coupled-dependence interval in which civilization needs the human-AI combination before an AI-only path is sufficient.

Delta = 0:
simultaneous transition, a limiting/knife-edge case absent a mechanism forcing coincidence.

## 7. Flow–viability non-identification theorem candidate

Observed current production is an on-path quantity.
m_H and m_A are off-path counterfactual viability properties.

Construct two structural systems that have identical:

- current outputs;
- current Human/AI production shares;
- current effective governance shares;
- observed quality;
- current human employment;
- current AI usage;

but differ in dormant fallback capacity, independent validation paths, expert-reproduction pipelines, and successor-AI development ability.

The two systems are observationally equivalent on the realized human-AI trajectory while having opposite signs of m_H or m_A under substrate-removal interventions.

Therefore, without withdrawal/intervention data or additional structural assumptions:

**current-flow data do not identify independent epistemic viability.**

This is a causal-identification result, not merely a measurement complaint.

Consequence for v1.0:
CIPSA can measure realized intellectual-flow composition, but even a perfectly measured CIPSA does not by itself determine whether a deeper epistemic-substrate transition has occurred.

## 8. Structural discontinuity without a discontinuous capability curve

The user's "civilizational break" intuition should not be expressed as a claim that raw AI capability must have a mathematical discontinuity.

Let all underlying capability variables be smooth in time.

The feasibility set of substrate-specific P-V-S trajectories can nevertheless change when a viability margin crosses zero.

Thus the regime indicator:

R(t) = sign(m_H(t)), sign(m_A(t))

changes discretely even if all micro-capability trajectories are smooth.

The discontinuity is therefore a change in the topology/feasibility of viable epistemic paths, not necessarily a singularity in benchmark capability.

Caution:
this can become an artificial threshold if the viability floors theta_r are arbitrary. A serious paper must show robustness over a preregistered admissible family of thresholds, domains, horizons, and resource envelopes.

## 9. Time compression enters as a secondary, not primary, dimension

Existing literature already studies pacing, generation time, rate shocks, and fast AI R&D. The novelty cannot be "AI is fast."

However, once T_S and T_D are defined, transition speed becomes meaningful.

Let tau_E be the time required to form a new fully independent human expert cohort in the relevant domain.

Let tau_C be the duration of the structural transition corridor.

If tau_C << tau_E, the civilization may cross the entire corridor before a newly trained human cohort could restore independent human viability.

This gives a precise role to the user's "sub-generational discontinuity" intuition without pretending that rate theory is new.

## 10. Present empirical status, September 2026

Public evidence shows rapid movement toward stronger AI participation in AI R&D but does not establish AI-only P-V-S viability.

Anthropic reports that, as of August 2026:
- Claude leads 26% of measured AI R&D;
- more than 90% is at collaboration-or-higher;
- no measured AI R&D subset is fully autonomous (AL5);
- Anthropic explicitly defines recursive self-improvement as a model fully autonomously building its successor.

OpenAI reports an automated research intern and heavy internal coding-agent use, but states that people still set research priorities, judge which ideas and results to pursue, and decide whether to scale, pause, or deploy systems.

These facts make T_S a live empirical question, not a completed historical event.

## 11. Historical gate

The theory must not claim that machines helping create machines is unprecedented.

Historical and current counterexamples include:
- capital goods producing capital goods;
- self-hosting compilers;
- EDA and AI-assisted chip design;
- theorem provers and formal verifiers;
- self-driving laboratories;
- autonomous ML research pipelines.

The candidate AGI-specific event is narrower:
a nonhuman cognitive path satisfying broad frontier P, independent V, and cross-period S under an explicit boundary.

The historical research task is to determine whether any earlier technology satisfies that same criterion over comparable breadth. If yes, the "AGI-specific" historical claim must be weakened or abandoned.

## 12. Closest live threats to originality

1. Lovett 2026 Cognitive Commons:
links professional expertise regeneration to the ability to validate AI.

2. Nadendla 2026 FRFP:
formalizes conditions under which human tacit judgment remains structurally necessary in long-horizon human-AI workflows.

3. Nettasinghe & Zhao 2026:
models human skill, LLM skill, archive quality, and cross-learning.

4. Acemoglu, Kong & Ozdaglar 2026:
models knowledge collapse from AI-induced changes in human learning incentives.

5. Burtsev 2026:
defines recursive criticality / a reproduction number for AI self-improvement.

6. Chen, Wang & Qu 2026:
surveys loop closure in recursive self-improvement and emphasizes evaluator quality and research direction-setting bottlenecks.

7. Van Rooyen 2026:
develops recoverability under AI-mediated rate shocks using viability/rate-capacity ideas.

8. Autonomous-science and self-driving-lab literature:
already closes production-validation loops in narrow domains.

The candidate survives only if it remains explicitly about the bidirectional independent viability of a cross-period frontier epistemic cycle, not any component mechanism above.

## 13. Kill conditions before manuscript drafting

Do not draft v2 as a paper unless all conditions below survive:

A. Prior-art kill test:
No direct prior work already defines the T_S / T_D separation for a P-V-S frontier epistemic cycle.

B. Definition test:
P, V, and S can be operationalized without circularly defining "frontier" or "independent validation."

C. Identification test:
The observational-equivalence / non-identification result can be stated and proved cleanly.

D. Robustness test:
Regime classification is not an artifact of one arbitrary threshold, domain basket, or resource envelope.

E. Historical test:
Earlier technologies do not already satisfy the same broad cognitive-path criterion, or the historical claim is revised accordingly.

F. Empirical test:
At least one real domain admits a plausible measurement protocol capable of bounding m_H and m_A rather than merely naming them.

Only after A-F should a manuscript be written.
