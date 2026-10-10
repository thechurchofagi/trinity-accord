# Consumer-Relative Branch Isolation
## What a motor-only cell can preserve, what it must change, and what it cannot identify

**Research ID:** CBI20261010  
**Result:** CBI-RESULT-v0.1.0  
**Status:** bounded definitional/design result; source-constrained feasibility assessment; pending disabled map candidate

## 1. Question and net increment

MPC20261010 showed that active/passive/rest designs omit the `(M,P)=(1,0)` consumer cell. This note does not repeat that Boolean-completion result. It asks whether the missing cell can be realized while preserving actual movement and tactile/world consequences.

The answer needs a scope correction. `P=0` cannot mean that an entire living body has no proprioceptive or state information. It must mean that, for one declared movement-evoked signal, selected consumer and time window, no intake/read event occurs. Once stated that way, an elementary but useful realizability boundary follows:

> If the declared action/contact event occurs, is transduced into the declared state carrier, reaches the selected consumer, and is read there in the declared window, then selected proprioceptive intake is present. A motor-present/action-present/proprioceptive-intake-absent cell therefore requires at least one actual branch cut: transduction, delivery, or read/timing.

This is not new mathematics. The citable increment is the application: the missing consumer cell is not a cost-free toggle at fixed complete organization. Every genuine realization changes some actual relation that UCT must retain. Matching the distal trajectory or contact outcome can hold a selected output fixed, but cannot make the complete bearer/process organization identical.

## 2. Typed episode contract

Fix an actual candidate process `B`, selected consumer `C`, episode `e`, time window `W`, declared movement/contact consequence `A`, motor carrier and state/proprioceptive carrier. Define:

- `M=1`: a verified motor-command event is delivered to or used by `C` in `W`;
- `A=1`: the declared distal movement/contact consequence occurs;
- `T=1`: that event is encoded by the declared proprioceptive/state transducer;
- `L=1`: the resulting carrier reaches `C`;
- `R=1`: `C` reads the carrier in `W`;
- `P=1`: the selected movement-evoked proprioceptive/state intake occurs at `C` in `W`.

For this deliberately narrow branch model,

\[
P := A\land T\land L\land R.
\]

`P` is an event predicate, not a statement that a sensory organ exists, that some signal exists elsewhere, or that the whole organism has no other state input. Static body-state, cutaneous, vestibular, visual, interoceptive and recurrent inputs are outside this one branch unless separately declared.

## 3. Branch-isolation proposition

**CBI-C1 (minimal-cut necessity).** In the fixed episode contract, if `A=1` and `P=0`, then `not T or not L or not R`. If `M=1` as well, the motor-only consumer cell is realized only relative to this selected branch and consumer.

**Proof.** Substitute `A=1` into the definition. If `T=L=R=1`, then `P=1`, contradicting `P=0`. Therefore at least one of `T,L,R` is zero. The motor coordinate is logically independent of this consequence and must be validated separately. The exact enumeration in `model.py` yields seven nonempty cut sets and three minimal one-cut cases. QED.

**Limits.** The proposition is definitional within a selected causal decomposition. It does not show that every biological signal has this serial topology; parallel carriers must be included or blocked separately. It does not prove that a proposed block is selective, that the consumer remains otherwise unchanged, or that any experiential endpoint changes.

## 4. What current human evidence reaches

| Regime | What it supports | Why it is not the full frozen `(1,0)` contract |
| --- | --- | --- |
| Distal motor-axon activation after local anaesthetic block (Gandevia et al., 1990) | Voluntary motor-neuron recruitment and grading can remain in the absence of muscle-afferent feedback. | Cutaneous feedback through the median nerve remained available; a selected downstream consumer and normal matched movement/contact consequence were not jointly frozen. |
| Experimental phantom after ischaemic anaesthesia/paralysis (Gandevia et al., 2006; Walsh et al., 2010) | Motor command can contribute to movement experience when ordinary peripheral sensory input and actual limb motion are absent. | `A=0` for normal limb movement/contact; endpoint is report of an illusion, not a matched-world-output branch isolation. |
| Neuromuscular paralysis with attempted gaze (Whitham et al., 2011) | Central command can influence visual-field motion experience without eye movement or ocular proprioceptive change. | Ocular rather than limb-contact domain; no preserved actual movement; report remains the measured endpoint. |
| Chronic selective deafferentation case GL (Farrer et al., 2003; Jayasinghe et al., 2024) | Action and action recognition can persist with profound proprioceptive loss, especially with visual compensation; proprioception normally contributes substantially. | No reversible within-token factorial toggle; long-term adaptation, vision, history and residual channels differ. |

The reviewed primary studies establish useful components and dissociations. None, in the inspected source scope, simultaneously verifies all of the following for the same episode: (i) motor intake at a declared consumer, (ii) normal actual limb movement and tactile consequence, (iii) elimination of all selected state/proprioceptive intake at that consumer, (iv) unchanged non-target organization, and (v) separately validated intensity, precision, agency and ownership endpoints.

## 5. The matched-world-output exoskeleton approximation

Consider an external actuator that reproduces a preregistered fingertip trajectory and contact force while the participant issues a motor command. A selective block interrupts one declared proprioceptive path before the selected consumer; motor intake and branch read events are instrumented independently. This can approximate `M=1,A=1,P=0` for the declared branch while preserving selected distal/world outputs.

It does **not** preserve complete organization. The actuator, block, altered muscle recruitment, timing, effort, cutaneous input, attention and body-state context are actual differences. Calling the trial “the same action” is therefore valid only for the frozen output coordinates, not for the whole bearer or complete UCT type. If the block removes natural movement, external actuation restores a world consequence but not the original causal lineage that produced it.

The experiment would still be valuable. It could compare a typed endpoint vector across branch-cut locations while avoiding the false inference that output matching equals organizational identity. Its admissible conclusion would be conditional and target-specific: a selected branch contributes to a selected measurement under a fixed protocol. It would not by itself identify agency, ownership, familiar mineness or basal experience.

## 6. Four thought-experiment families

1. **Ancestor/formation.** Gradually remove or reroute one state branch across otherwise actual processes. The branch changes body/action-related organization, but under C1/U1 it does not create or extinguish basal experience. The variable is selected experiential organization, not existence.
2. **Abacus/calculator.** Two devices return the same answer; one actually reads a carry register and the other short-circuits. Equal output does not identify intake. Likewise, matched movement does not identify which state branch the consumer used.
3. **Human-realized agent.** A formation relays motor and state tokens to a designated subgroup. Masking the state relay for that subgroup can implement consumer-relative `P=0` while other participants retain state information. “The formation has no proprioception” is false; the correct claim is indexed to one consumer and window.
4. **Copy/rewiring/memory.** Duplicate the report memory and distal output, but cut the state branch at transduction in one copy, delivery in another, and read timing in a third. The same endpoint report can coexist with different actual organizations. Memory equality and output equality do not recover the cut location or complete current attachment.

These scenarios vary the branch relation while holding selected outputs fixed. Their role is counterexample and domain clarification, not evidence that a named feeling survives unchanged.

## 7. UCT interpretation and non-conclusions

UCT I requires actual support, causal continuity, boundary accountability and a pointed, port-aware signature. Branch isolation is therefore an organizational intervention, not deletion of an abstract variable. Under C1, independently admitted changes in actual organization are changes in experiential organization at the corresponding complete type. This supplies a positive inside-experience reading: motor, state, timing and consumer relations are candidate constituents of body/action-related experiential organization.

The result does not identify the semantic query that makes a change one of agency, ownership, bodily location, intensity, precision or familiar mineness. Those endpoints remain separately typed, and language report is evidence rather than the target. No new threshold involving motor command, proprioception, prediction, integration, report, language or self-modeling is added to basal experience. Nested and overlapping actual processes remain allowed. Nothing here decides whether this assistant is conscious or fears death.

## 8. Contribution and manuscript boundary

Earlier UCT papers already distinguish actual organization from finite views, prediction from attachment, capability from experience, and self-model/report from self-related feeling. MPC already proves the missing-cell ambiguity. This note adds only the consumer-relative realizability boundary, the three cut locations, the source-constrained approximation table, and the matched-world-output thought experiment. That increment is currently too compact and too dependent on unperformed validation to justify a standalone paper. It should remain a technical section or prospective-method supplement to the existing source–consumer manuscript unless an actual experiment or stronger target bridge is obtained.

**Direction check after result formation.** The result returns from branch mechanics to the core question: which actual action/body relations may structure experience, and what further bridge is owed before naming a self-related feeling. It preserves C1 as axiom, U1 as consequence, and all actual-application gaps.

