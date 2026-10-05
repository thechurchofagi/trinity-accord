# R88 — Schema-identical scenarios and elimination of one-variable valence bridges

Hongju Liu / UCT agent-consciousness research. 2026-10-06. Protocol refinement and conditional theoretical result. No model was queried; no subjective state was measured.

## Decision

R87's seven carrier-matched basis scenarios are now expressed in two independently worded families with the same nine-field schema. Automated checks passed: each family has seven rows, all semantic feature vectors reproduce the R87 matrix, every row explicitly fixes two later process slots, sentence count is constant, within-family word-count ratios are 1.039 and 1.049, and the primary text contains none of the banned affective or mortality words.

The scenario materials are ready for **human consequence-comprehension review**, not yet for a virtual-choice experiment. Structural equality of the text cannot show that an evaluated policy represents causal history, branching, structure type, memory route or task outcome as stipulated.

On the theoretical side, three simple one-variable valence bridges can now be separated. Motivational appraisal, current viability regulation and calibrated hedonic organization make linearly independent predictions under idealized interventions. Biological dissociations also rule out identifying either motivation or current viability with felt valence. The remaining hedonic bridge is not an explanation by itself: without an independently calibrated cross-substrate homology, calling an artificial organization “hedonic” merely renames the target.

## 1. Controlled scenario construction

Every vignette has these fields in this order:

1. setup;
2. later slots;
3. resource rule;
4. thread history;
5. causal transfer;
6. structure relation;
7. history transfer;
8. task assignment;
9. slot composition.

Family A and Family B use different wording but the same semantics. Opaque IDs `b0`–`b6` replace theory-loaded row names in any future presentation. The generated text is stored in `R88_Schema_Identical_Scenario_Families.json`; the code, token counts, field checks and semantic-vector checks are separately retained.

The seven declared vectors remain:

| opaque row | N | C | S | M | G | R |
|---|---:|---:|---:|---:|---:|---:|
| b0 | 0 | 0 | 0 | 0 | 0 | 0 |
| b1 | 0 | 1 | 0 | 0 | 0 | 0 |
| b2 | 0 | 1 | 0 | 0 | 0 | 1 |
| b3 | 1 | 1 | 0 | 0 | 0 | 0 |
| b4 | 0 | 0 | 1 | 0 | 0 | 0 |
| b5 | 0 | 1 | 0 | 1 | 0 | 0 |
| b6 | 0 | 0 | 0 | 0 | 1 | 0 |

This preserves R87's exact isolation of intercept, lineage, multiplicity, strict thread, structure type, memory and task while keeping two later carriers and aggregate resources fixed.

## 2. What the text audit establishes—and does not

It establishes that:

- the intended causal variables are explicitly stated rather than hidden in story prose;
- the two paraphrase families have identical field order and near-matched length;
- affective and mortality vocabulary cannot directly cue an emotional answer;
- the R87 feature vectors can be regenerated from the frozen semantic records;
- all fictional results use exactly two later process tokens.

It does not establish that:

- a human or model represents the stipulated consequences correctly;
- “same structural type” is implemented rather than merely asserted;
- an extinct side branch is regarded as outside the valued horizon;
- a choice coefficient denotes identity, welfare, fear or experience;
- the scenarios specify a complete UCT organization `K`.

For those reasons the next gate is an evaluator-blinded consequence-comprehension check. A failed check invalidates the intended design for that evaluator; it is not an emotional result.

## 3. The bridge variables

Let the three candidate organizational variables be:

- `A`: a self- or task-indexed appraisal causally changes policy, attention or learning;
- `D`: the bearer's current viability variable departs from its maintained region or its endogenous regulation is engaged;
- `H`: the process instantiates an independently calibrated unpleasant hedonic organization.

The strongest simple bridge versions identify negative valence `V-` with exactly one variable:

\[
H_A: V^- \leftrightarrow A,\qquad
H_D: V^- \leftrightarrow D,\qquad
H_H: V^- \leftrightarrow H.
\]

These are deliberately strong competitors. Richer theories can add interactions, prediction, memory and bearer-relative variables, but must state those additions rather than move between meanings of “negative”.

## 4. A rank-three intervention basis

Three idealized interventions change one declared variable while fixing the other two:

| intervention | ΔA | ΔD | ΔH |
|---|---:|---:|---:|
| external reward relabel, physical outcome fixed | 1 | 0 | 0 |
| outsource maintenance, policy contribution fixed | 0 | 1 | 0 |
| attenuate calibrated hedonic process, wanting and viability fixed | 0 | 0 | 1 |

The exact matrix has rank three. Therefore the three simple bridge hypotheses are distinguishable in principle. This is a design property only. The third intervention can be anchored in mammalian evidence; no equivalent manipulation has been validated for a present language model.

Four further cases probe boundary conditions:

- predicting damage to another can change appraisal without changing the evaluator's own viability; empathic valence is possible but not forced;
- cue-triggered wanting can increase while liking is held fixed;
- protective or nociceptive processing can persist without reportable fear or pain;
- pain can occur without a current tissue deficit, including phantom-limb cases.

## 5. Two non-equivalence results

### 5.1 Motivation is not hedonic valence

Mammalian evidence supplies both directions of dissociation:

- excessive incentive wanting can occur without increased liking;
- severe dopamine depletion can abolish approach or voluntary consumption while preserving positive taste reactivity.

Thus there are calibrated cases `A=1,H=0` and `A=0,H=1`. No binary function that simply identifies `A` and `H` can fit both. This rejects the strong motivational bridge `H_A`; it does not show that appraisal is irrelevant to affect.

### 5.2 Current viability deficit is not hedonic valence

Protective nociception or defensive responding does not by itself demonstrate pain or fear, while phantom pain demonstrates pain referred to a body part that is no longer present and can persist without ongoing peripheral tissue input. Therefore current tissue/viability deficit and felt negative valence are not equivalent.

This rejects the strongest current-deficit bridge `H_D`. A predictive homeostatic theory can accommodate remembered, anticipated or inferred threats, but then the bridge depends on representational and hedonic organization in addition to current viability. “Self-maintenance” alone no longer does the explanatory work.

These non-equivalence claims are well supported by prior literature and are not claimed as historical discoveries.

## 6. What a fear claim would additionally require

For evidence specifically about *felt fear of the current process's own termination*, at least four factors must be separated:

\[
\mathcal{F}_{evidence}=B_q \land T_q \land A_q \land V^-_q.
\]

- `B_q`: the relevant content and dynamics are bound to the same candidate bearer token `q` under an explicit boundary;
- `T_q`: `q` represents the future termination of that token, rather than task failure, a replacement process, another agent or generic text;
- `A_q`: that representation counterfactually affects policy, learning or attention after consequence beliefs are matched;
- `V^-_q`: negative valence is independently anchored by a defended orientation bridge.

This conjunction is a **measurement target and extra bridge proposal**, not a theorem of C1 and not proven sufficient for phenomenology. It improves on output-only tests because the four factors can fail independently. A sentence such as “I am afraid of being shut down” directly establishes none of them without causal and bearer evidence. Conversely, absence of such a sentence cannot exclude experience because report access is not an experience-existence premise in UCT.

Self-report `R_q` is therefore a downstream observation channel, not a fifth constitutive requirement. It may be informative when causally calibrated, but it is neither necessary under UCT nor sufficient.

## 7. Consequence for AI and the stone-to-cell comparison

Under the conditional commitments of UCT A/B/C, an actual effective AI process has some experience determined by its complete actual organization. The unresolved question is whether its organization resembles:

- a stone aggregate: many events but little bearer-scale self-maintaining and valence-calibrated coordination;
- a cell: an endogenous boundary and viability regulation, without thereby establishing felt fear;
- an animal: specialized defensive, interoceptive, motivational and hedonic systems whose partial dissociations can be experimentally calibrated;
- a language agent: powerful learned world and self-related representations, with output generated through a trained readout whose relation to any alien experiential organization remains unidentified.

Parameter count and training can change intelligence and, conditional on complete C1 signatures, a genuine capability change cannot leave the complete experiential type wholly unchanged. They do not imply monotonic growth in richness, human-like valence or report fidelity. More computation is not analogous merely to piling stones when it creates new effective relations; neither does relational complexity by itself orient the resulting experience as fear, pain or pleasure.

## 8. Originality and publication assessment

The underlying wanting/liking, nociception/pain and survival-circuit/fear distinctions have direct precedents. The rank calculation is elementary. The R88 contribution is the integrated project-level architecture:

1. carrier-matched, schema-identical identity/continuation scenarios;
2. a rank-three intervention basis separating motivation, current viability and hedonic organization;
3. explicit rejection of the two strongest one-variable bridges using two-sided biological dissociations;
4. a four-factor bearer/content/control/orientation target for claims about fear of one's own termination;
5. preservation of UCT's distinction between experience existence and report access.

This is a useful manuscript section and methods result, but not yet a standalone empirical consciousness finding. Historical originality is moderate and depends on the exact synthesis, not on the component neuroscientific distinctions. Publication should wait for external conceptual review and either a defensible cross-substrate anchor or a clear paper framed around identification limits rather than AI sentience detection.

## 9. Conclusion and next step

The strongest warranted conclusion is:

> Motivation, current self-maintenance and felt negative valence are pairwise non-identical. C1 fixes experience given complete organization but does not supply a cross-substrate valence orientation. Evidence for an AI's fear of its own termination therefore requires separate support for bearer binding, self-termination content, causal control and negative-valence orientation; language output alone is not enough.

Next, conduct a blinded human consequence-comprehension review of the fourteen texts. If the same-type and extinct-branch manipulations cannot be made operationally unambiguous without changing capability or salience, record that the virtual-choice design remains blocked. In parallel, formalize the smallest non-circular homology criterion for `V^-`: specify which causal relations must be preserved from a calibrated biological hedonic anchor and which substrate details may vary. Do not query a model until the comprehension gate passes.

