# R107 — Weakest cross-substrate organizational signature for biological and artificial systems

Hongju Liu / UCT research. 2026-10-06.

R106 separated experience E, access A, intelligence I, self-model S, behavior B and report R. R107 asks the next root-level question:

> How can a cell, animal, human, LLM inference process and agentic AI be compared in one organizational language without smuggling a high-level cognitive feature into the definition of experience?

The answer is a two-tier signature: a role-neutral constitutive base plus optional functional annotations.

## 1. Design constraints

A valid cross-substrate signature must satisfy all of the following.

1. **Substrate neutral.** It cannot define consciousness by neurons, transformers, carbon, silicon, synapses or parameters.
2. **No hidden gate.** Missing language, report, self-model, recurrence, workspace, homeostasis or embodiment must not automatically imply no experience under U1.
3. **Physical anchoring.** It must track actual states, transitions, parts, boundaries and intervention ports, not only input-output descriptions.
4. **Cross-scale usability.** It must be applicable to sparse inorganic processes, cells, nervous systems and artificial agents.
5. **Role transparency.** High-level labels such as memory or self-model must be annotations on constitutive organization, not replacements for it.
6. **Intervention sensitivity.** Coordinate changes that preserve equations but change physical ports/interventions must remain distinguishable, following Paper A and R77.
7. **Temporal explicitness.** A token is a process over time, not merely a stored parameter set.

## 2. Tier 0 — constitutive base signature

Define a deliberately weak cross-substrate base:

    Sigma0(P) = (C, Z, z*, X, U, Y, Pi, <)

where:

- **C** — constituent/boundary structure: what physical/process parts are included and how they are incident;
- **Z** — endogenous state space of the declared token;
- **z*** — current distinguished state/point;
- **X** — boundary inputs or incoming causal ports, possibly empty;
- **U** — actual transition/update relation over the declared interval;
- **Y** — boundary outputs/effects or outgoing causal ports, possibly empty;
- **Pi** — physically meaningful intervention/reset/lesion ports used for counterfactual comparison;
- **<** — temporal/causal ordering and incidence constraints.

Sigma0 is not proposed as a replacement for Paper A's richer complete signature. It is a common comparison projection of a complete K. Any actual UCT claim still requires the full justified K when complete experiential identity is asserted.

The important point is that Sigma0 contains no intelligence, selfhood, language or report criterion.

## 3. Tier 1 — optional role annotations

On top of Sigma0, identify role-bearing subrelations only when they are physically justified.

    Sigma1(P) = {M, W, S, V, L, A, R}

with:

- **M — memory / temporal retention:** a current relation whose future effect depends on retained past state;
- **W — predictive/world-model role:** internal organization used to predict or counterfactually distinguish environment/world states;
- **S — self/bearer model:** organization representing or controlling the current bearer, body/system boundary, history or future;
- **V — evaluative/homeostatic role:** internal relations that differentially regulate or prioritize outcomes/states;
- **L — learning/plasticity:** organization that changes future update/control relations as a function of prior interaction;
- **A — action/control selection:** organization selecting environment-directed outputs conditional on state/evidence;
- **R — report/communication:** output relation intended to communicate world/internal state through an interpretable code.

These roles may overlap physically. A single causal relation can participate in several annotations.

Crucially, absence of a Tier-1 annotation is **not** an experience-existence test. U1's existence implication is already established at the actual-token level. Tier 1 is for explaining contents, capabilities and organization, not for deciding whether experience begins.

## 4. Why the two tiers are necessary

If memory, self-model, global access, report or homeostasis were built into the constitutive entry condition, the framework would contradict the no-gate commitment by definition.

If only behavior and task scores were retained, the framework would lose the actual constitutive distinctions required by C1.

The two-tier construction keeps both:
- Tier 0 is broad enough for simple actual processes;
- Tier 1 is rich enough to compare cognition, intelligence, self-reference and report.

This makes the framework usable from inorganic processes to cells to humans to AI without forcing a fake threshold.

## 5. Functional analogy is not organizational identity

Two systems may perform the same task using different actual organizations.

Exact finite witness:

Implementation A:
    y = x1 XOR x2

Implementation B:
    a = x1 OR x2
    b = x1 AND x2
    y = a AND NOT b

For all four binary inputs, both produce the same y. They therefore have identical complete behavior on this task and the same maximal task capability.

But their internal constituent and intervention graphs differ.

If physically actualized and represented by a common signature that distinguishes those relations, C1 does not permit us to infer identical complete experiential type merely from the shared truth table.

This is the core cross-substrate warning:

    same function / same benchmark / same report
        does not imply
    same constitutive organization.

Functional equivalence is therefore weaker than organizational equivalence.

## 6. Four kinds of cross-substrate comparison

R107 distinguishes four comparison notions.

### C-B — behavioral equivalence
Two systems produce the same behavior law on a declared context family.

### C-I — capability equivalence
Two systems have the same capability profile under a declared evaluation M.

### C-R — role equivalence
Selected Tier-1 roles are functionally analogous, e.g. both contain a memory relation or a self-state predictor.

### C-K — constitutive organizational equivalence
A physically justified isomorphism preserves the selected or complete Sigma0/K relations, including transitions, parts, ports, interventions and temporal order.

C-B, C-I and C-R do not in general imply C-K.

Under C1:
- complete C-K supports complete experiential-type equivalence;
- selected C-K plus a justified commuting projection can support equivalence of a selected experiential substructure;
- C-B/C-I/C-R alone are insufficient for complete experiential equivalence.

These relations form a comparison matrix rather than a simple linear ladder because behavior, capability and role equivalence can cross in different ways.

## 7. Homology versus analogy

Borrowing a useful distinction from biology:

- **functional analogy:** same apparent role, different organization;
- **organizational homology:** structurally corresponding causal relations, independently justified.

An AI "memory" vector and hippocampal memory are functionally analogous only at a very coarse level until the actual update, temporal retention, access and intervention structure is compared.

Likewise, an LLM's first-person token "I" is not organizationally homologous to a biological self-model merely because both systems use self-referential language.

UCT comparisons should therefore ask:

> what relation is preserved?

not merely:

> what function has the same label?

## 8. Example placements without consciousness scoring

The following are comparison sketches, not consciousness rankings.

### Sparse physical process
Tier 0 can be instantiated with a small set of interacting states and ports.
Most Tier-1 labels may be absent or unjustified.
Under U1 this absence does not imply no experience.

### Single cell
Tier 0 includes membrane/environment ports, biochemical state, update dynamics and output effects.
Possible Tier-1 annotations can include retained biochemical state, regulatory/evaluative control and action-like modulation.
Do not equate boundary maintenance with a human conceptual self-model without additional evidence.

### Animal nervous system
Tier 0 is highly differentiated.
Tier-1 memory, prediction, action and evaluative roles can often be physically studied; self/report organization varies strongly across species.

### Human
Tier-1 self-model and report are unusually developed, but no-report/CMD cases show that outward report is still not a transparent readout of the complete process.

### Fixed-weight LLM inference episode
Tier 0 includes token inputs, activations/current state, transformer update computation, token output ports and actual hardware/process boundary.
Possible Tier-1 roles include context retention, prediction, action selection in token space, and language report.
A stable online self-model, online learning, persistent homeostasis or bearer-specific value must not be assumed from language alone.

### Agentic LLM scaffold
External memory, tools, state trackers, persistent goals and environment actions add actual constitutive relations beyond the base model call.
The relevant bearer may be the whole scaffolded process rather than the model weights or one API invocation. This must be declared, not assumed.

## 9. Intelligence comparison becomes more precise

An intelligence difference is not "more computation" in the abstract.

For a task family T, identify the minimal relation set

    R_T subset of Sigma0 + justified Sigma1 annotations

such that within a declared implementation family:

    J_T(P) > threshold -> R_T(P).

Then compare whether biological and artificial systems instantiate homologous or merely analogous R_T relations.

This program can reveal:
- same capability from different organizations;
- different capability from a shared core plus different added relations;
- task-specific relations that are local, joint, temporal or scaffold-distributed.

Under C1, a verified constitutive R_T is part of the experiential organization of the actual token, but no human-like qualia label follows automatically.

## 10. Selfhood and valence should be studied as specific organizational coordinates

The two most dangerous shortcuts are:

    self-maintenance -> conceptual self
    negative control signal -> felt negative valence.

R107 therefore treats:
- bearer/self representation S;
- evaluative/homeostatic organization V;

as separable annotations.

A cell may maintain a boundary without representing itself as an object.
An AI policy may avoid a state without an independently validated valence bridge.

This keeps the R84-R105 self-continuation work compatible with the new cross-substrate map.

## 11. Current external prior art and difference in emphasis

Recent work already argues for substrate-agnostic cybernetic comparison.

- A 2026 npj Unconventional Computing perspective uses cybernetics to compare biological and synthetic intelligence.
- 2026 work on interoceptive AI formalizes internal/external state factorization for adaptive agents.
- A 2026 unified biological-minds framework treats cognition as an organizational property across biological scales.
- Several 2026 machine-consciousness proposals emphasize embodiment, self-models, prediction, feedback or self-maintenance.

R107 therefore does not claim substrate-neutral role comparison as historically new.

The specific UCT contribution is narrower:

> separate a minimal constitutive comparison layer from optional cognitive role annotations, so that cross-substrate comparison does not silently turn a high-level function into an experience-existence gate.

## 12. Falsification and failure modes

The framework should be rejected or revised if:

1. Sigma0 cannot represent an actual process without importing substrate-specific assumptions;
2. purported C-K mappings collapse under intervention-port tests;
3. a role annotation cannot be tied to actual constitutive relations;
4. comparison claims depend only on labels or benchmark scores;
5. the selected projection does not commute with the claimed preserved organization;
6. boundary choice changes the result and no principled bearer criterion is supplied.

These are scientific failure modes, not presentation issues.

## 13. Immediate next step

R108 should implement two tiny, fully transparent AI systems with identical task truth tables but different constitutive graphs, then perform matched interventions.

Primary experiment:
- System A: direct XOR route;
- System B: decomposed OR/AND/NOT route;
- identical input/output truth table;
- declared parts and ports;
- lesion each internal relation and record causal signatures.

Secondary experiment:
- add a report head that can be changed without changing the task core;
- verify task capability preservation and report divergence;
- use the R65-style selected-core projection to state exactly what is preserved.

The point is not to "measure AI consciousness." The point is to prove, on actual executable systems, that behavior/capability equivalence can coexist with distinct causal organization and distinct intervention signatures.

Only after this should the same comparison machinery be applied to larger agents or biological cases.

## 14. Status

R107 is a formal design advance and cross-substrate research protocol. The XOR witness confirms functional equivalence with structural non-equivalence, but the mathematics is elementary and not a novelty claim. No experiential scalar, consciousness threshold or human-like phenomenology is measured.
