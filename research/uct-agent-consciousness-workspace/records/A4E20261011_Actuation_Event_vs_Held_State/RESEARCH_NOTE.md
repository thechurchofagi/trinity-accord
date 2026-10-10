# Actuation Event Evidence versus Held State

## 1. Problem

A4D requires a post-arbitration/pre-plant probe, but a probe may record only the actuator's current level. A stable level does not say whether a writer committed that value during the current trial or whether the actuator simply retained its earlier state. This matters to the UCT main line because a current body/action route requires an actual current relation, not a value that merely happens to agree with a command.

## 2. Typed objects

For one declared device and trial let `s-` be the verified pre-arbitration actuator state, `q` the challenge, `e` the post-arbitration commit event (possibly null), `src(e)` its physically bound selected writer when non-null, and `s+` the probed level. A level probe observes `(s-,q,s+)`; an event witness observes `(s-,q,e,src(e),s+)`. Command logs, request labels and endpoint reports are separate evidence objects.

## 3. A4E-N1: held-state nonidentification

**Type:** exact finite negative result.

**Statement:** When `q=s-`, a no-write history, a target write of `q`, and a hidden write of `q` have the same level observation `(s-,q,s+)`, although their current event and source facts differ.

**Domain:** binary state; one trial; sources `{none,target,hidden}`; a write sets the level to `q`, while no write holds `s-`.

**Proof:** direct enumeration. Among 12 histories there are six level-only signatures. The two `q=s-` signatures each contain all three histories. A post-arbitration level therefore cannot by itself witness a current commit.

**Counterexample role:** a latched actuator, a cached register, an abacus bead already in the requested position, or a human-held limb already at the commanded posture can display the requested value without a new target-route event.

**Status:** `NEGATIVE_RESULT_EXACT_FINITE`; no graph promotion.

## 4. A4E-N2: level change still does not identify the writer

**Type:** exact finite negative result.

When `q != s-`, a level change from `s-` to `q` rules out no-write in the declared hold-or-write model. It still leaves target-write and hidden-write histories level-equivalent. This is why A4E does not replace A4D writer completeness; the two obligations are conjunctive.

## 5. A4E-C1: bounded reset-and-anti-current consequence

**Type:** conditional device-relative result.

For one declared device/trial, suppose all of the following hold simultaneously:

1. `s-` is independently verified immediately before arbitration;
2. challenge `q` is chosen after that verification with `q != s-`;
3. A4D's complete writer inventory, non-target isolation and chronology premises hold;
4. the target cut is faithful and local;
5. rescue enters through the same selected interface;
6. the probe is physically bound to the post-arbitration/pre-plant level or commit event.

Then the pattern baseline `s+=q`, target-cut `s+=s-`, rescue `s+=q` supports a current device-relative target-route contribution in this model. The anti-current challenge makes a write necessary for each positive cell; A4D premises attribute the necessary write to the target route rather than an omitted writer.

This is not a universal theorem about actuators. Hardware with autonomous dynamics, analog drift, pulse-width integration, hidden energy storage or asynchronous commits requires a correspondingly richer transition law.

## 6. Event-witness option

An authentic event witness `(commit, selected source, value, time)` separates all 12 finite histories. But its authenticity is a physical premise: a software tag at request time is not a post-arbitration witness, and a selected-source label can be forged or detached from the energy-changing event. Provenance metadata is evidence, not the ontic event itself.

## 7. Thought experiments

- **Ancestor/formation:** fix lineage and learned command; vary only whether the current actuator transition occurs. Formation history cannot manufacture a missing present event.
- **Abacus/calculator:** a bead already showing `1` versus a bead moved to `1` has the same snapshot; only the transition history differs.
- **Human-realized agent:** a person may keep a switch at the requested level without executing the named algorithmic instruction; observed level is not current consumer use.
- **Copy/switch/memory:** a copied register already containing `q` can be switched into view, matching the level while changing carrier, writer and chronology.

These experiments fix output and requested content while varying present event, source or carrier. None contains a phenomenal variable.

## 8. UCT interpretation and stop

A4E advances only the evidence needed for an actual present body/action relation. Under a separately admitted complete C1 instance, an actual relation may have its structural counterpart inside experience. A4E neither supplies that complete token nor identifies familiar bodily/action mineness. It adds no basal-experience gate, report requirement, self-model, language condition, unique owner or verdict about the current assistant.

## 9. Direction check after result

**PASS_WITH_EVENT_AND_PHENOMENAL_STOP.** The correction prevents a static value from being mistaken for current organizational use, while the positive result gives a bounded way back to a real device. It is not a new control score or a substitute for `H_way`.
