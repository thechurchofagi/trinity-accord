# A4F — Witness Independence and Non-Circular Actuation Provenance

## 1. Result

A4E showed that a current transition and its source are different facts. A source field does not repair that gap when the field is written by the same process whose authorship is in question. A4F makes this non-circularity requirement exact in a two-writer finite model.

For each actual source `s`, let `R_s` be the set of complete witness vectors that source can physically realize under the declared write, forge, replay, suppression, reset and timing permissions. The target source is identified only when `R_target` is disjoint from every admitted alternative writer's report set. This is elementary finite identifiability, not a new general theorem.

Six exact schemes were enumerated. Level change, a self-attested source label, two logs sharing one controllable root, and an independent source-agnostic transition detector all leave target/hidden overlap. Source-specific post-arbitration taps are disjoint in the declared two-writer model only when the inventory is complete and neither writer can forge, replay, suppress, reset or re-time the other tap. Giving the hidden writer replay access immediately restores the target-idle twin.

The positive product is therefore not “more logs.” It is a prospective witness-independence contract tying current event, source-sensitive physical placement, whole-vector control independence, complete writer inventory, clock order, challenge freshness, cut and same-interface rescue to one bounded device and interval.

No physical robot or human was installed. No completed-map object is added, and no familiar-mineness endpoint is inferred.

## 2. Typed domain

Fix one declared device bearer `P_dev`, interval `I`, device signature `K_dev`, target writer `T`, finite admitted alternative-writer set `W_alt`, arbitration boundary `g`, current commit `e`, physical transition `a`, complete witness vector `z`, and evidence channels `E`.

Keep distinct:

- the ontic event `e` and any record about `e`;
- event occurrence and selected source;
- a source label and the physical control ancestry of the channel carrying it;
- multiple files and multiple independent physical constraints;
- physical independence and statistical decorrelation;
- declared `K_dev` and a complete actual-token signature `K`;
- route evidence, experience-internal organization, external judgment and report.

For one scheme, `R_s` contains every vector that source `s` can cause to be accepted. The model asks whether target and hidden histories can share an accepted vector. It does not assume that a real actuator, recorder or observer is Boolean.

## 3. A4F-N1 — self-attestation does not identify source

**Type:** finite nonentailment with an exact twin.

**Statement:** If a hidden writer can emit the same accepted source label as the target writer, a current commit plus the label `target` does not identify the target source.

**Domain:** sources `{target, hidden}`; A4E has already established that one current commit occurred; the label channel is writable by the acting source or a common controller.

**Proof:** the target report set contains `(changed,target)`. The hidden report set contains both `(changed,hidden)` and forged `(changed,target)`. Their intersection is nonempty. A target-idle history therefore has the same accepted vector. QED.

The same proof applies to two or more logs behind one writer-controlled root: duplicating a claim does not duplicate its physical constraint.

## 4. A4F-N2 — event-independent is not source-specific

An independently powered transition detector may truthfully report that a commit occurred while remaining source-agnostic. In the exact model both target and hidden commits produce `(commit,1)`. Such a detector repairs A4E's event-occurrence question but not A4D's source-attribution question.

This is a useful positive distinction: an independent channel can improve one coordinate of evidence without identifying every coordinate. It must not be dismissed as useless, nor promoted beyond its scope.

## 5. A4F-P1 — bounded source-tap separation

**Type:** conditional finite separation result.

Suppose the only actual writers are `target` and `hidden`, and the accepted vector includes an authentic current commit plus two source-specific taps after final arbitration:

```text
target event -> (commit=1, tap_target=1, tap_hidden=0)
hidden event -> (commit=1, tap_target=0, tap_hidden=1).
```

If neither source can forge, replay, suppress, reset, re-time or route around the other's tap, the two report sets are disjoint. The actual source is identified within this declared two-writer model.

This is not a hardware-independence proof. If the hidden writer can replay the target vector, the intersection returns exactly. If an unlisted writer can act downstream of both taps, writer completeness fails. If a common power, reset, clock, bus master or recorder can rewrite both channels, the two files are a single evidential root.

## 6. Whole-vector provenance cut

For each alternative `h`, let `F_h` be the set of whole accepted witness vectors that `h` can realize under the actual architecture. The exact identification condition is:

```text
R_target ∩ F_h = empty for every admitted h != target.
```

Calling two sensors independent is not enough; independence must be cashed out as a physical restriction on the alternative writer's whole-vector realization set. A single unforgeable coordinate can provide that restriction in a coordinate-separable design, but correlated timing, common reset, suppression and downstream injection must be included in the vector-level analysis.

The familiar graph-cut language is only an architectural aid here. A4F does not claim invention of provenance graphs, fault containment, tamper-evident logging, attack detectability or set-disjoint identifiability.

## 7. Witness-Independence and Provenance contract

Call the prospective package `WIP(P_dev,I,K_dev,T,W_alt,g,e,a,E)` and require all clauses jointly:

1. **Frozen bearer and source set.** Fix the device boundary, interval, energy/command path and every process capable of changing the selected transition or accepted witness vector.
2. **A4E current-event premise.** Verify the pre-state and anti-current challenge, or use a physically bound current commit detector; a held level is not enough.
3. **A4D writer completeness.** Inventory every timely writer and disturbance class; absence from software configuration is not physical absence.
4. **Post-final-arbitration placement.** Bind source-sensitive witness channels to the final source-specific energy/command paths before the plant transition and after any later overwrite point.
5. **Whole-vector control independence.** No candidate writer may forge, replay, suppress, reset, re-time or rewrite the accepted vector that is supposed to distinguish it.
6. **Common-cause accounting.** Shared power, clock, reset, bus master, DMA path, logger, firmware, human operator and evidence collector are either included as possible writers/controllers or independently bounded.
7. **Fresh challenge and clock order.** Challenge selection follows pre-state verification; source taps and commit time are ordered relative to arbitration and plant change; stale provenance is rejected.
8. **Faithful cut and same-interface rescue.** The target cut removes its source path without directly altering witnesses or endpoint; rescue re-enters through the same audited arbitration interface.
9. **Negative and fault controls.** Exercise each admitted alternative source, witness dropout, reset/replay attempt and no-event condition so that the proposed source vector has an observable failure signature.

Only if the package is installed on one actual device/interval and all admitted report sets are separated may the conclusion be `DEVICE_RELATIVE_CURRENT_SOURCE_EVIDENCE`. It is not `COMPLETE_K`, `C1_ADMISSION`, `RetBind`, `B_fam` or `H_way`.

## 8. Thought-experiment battery

| Family | Fixed | Varied | Counterexample role |
|---|---|---|---|
| Ancestor / formation | inherited command vocabulary and mature output | present source versus inherited label schema | a provenance word carried from formation does not witness the current causal route |
| Abacus / calculator | bead position and written ledger | hand moving the bead versus hidden magnet; ledger controlled by mover versus read-only beam | a true final state and repeated label can coexist with source substitution |
| Human-realized agent | abstract program, input and visible action | same person both acts and fills the log versus an independently constrained observer | organizational boundary omission can make “independent” software logs circular |
| Copy / switch / memory | copied event record and target label | live source tap versus replayed old vector after carrier switch | persistent provenance content is not a current event or current source |

These experiments hold requested content/output fixed while varying current source and witness control ancestry. They do not introduce an additional owner and they remain compatible with nested or overlapping actual processes.

## 9. Relation to UCT and the formal map

UCT I v1.2 §8.11 requires the physical process to distinguish a claimed relation under controlled perturbation. A source word selected by the questioned writer does not meet that burden by itself. Sections 8.12–8.14 and 14.7 keep body-centered organization, self-model, conceptual I and any extra owner distinct; A4F adds none as a basal requirement.

For R172, witness vectors are evidence for actual path use, not `OnticUse_path` itself. For R173, even a successful WIP installation would supply only part of current consumer-use evidence. The same actual bearer/interval, retained relation, complete signature, C1 instance, R157 transport and independent familiar-mineness bridge remain simultaneous premises. The `all_of` route is not fired.

## 10. Failure boundary and next question

Five of six enumerated schemes do not identify source; the only separating row is conditional on exactly the physical premises most likely to be omitted. This is a useful failure, not a negative verdict on instrumentation.

The next concrete question is platform selection: on one accessible actuator, can the final arbitration boundary and every common controller of source taps be physically enumerated, or does any shared reset/power/bus path keep the witness vector inside an alternative writer's realization set?

## 11. Direction checks

- **After selection:** PASS — current-action organization, not generic controller optimization.
- **After exact result:** PASS_WITH_PROVENANCE_AND_PHENOMENAL_STOP — the model identifies the non-circular evidence obligation and preserves event/source/experience distinctions.
- **Before save:** PASS — C1/U1 unchanged; no introspection, self-model, report, language, integration, recursion, prediction or continuation-control gate; no unique owner; no current-assistant consciousness or death-fear verdict.

