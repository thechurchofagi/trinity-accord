# A4D — Actuator-writer completeness and route evidence

## 1. Result

A4C rejected a direct endpoint-write twin because its recorded action sequence could not replay the copied endpoint. That is a real improvement over endpoint-only evidence, but it does not exclude a harder twin: an unlogged writer can act downstream of the named consumer, reproduce every tested actuator transition, and leave the named consumer causally idle.

A4D makes this residual precise. In a six-cell Boolean abstraction with challenge `q in {0,1}` and modes baseline/block/rescue, the genuine table is `q,0,q`. If an uncut hidden writer sees both `q` and mode, exactly one of its 64 Boolean tables reproduces all six actuator observations while the target connection is absent everywhere. Command, actuator and endpoint replay therefore do not by themselves identify writer identity.

A bounded positive result is also exact. If every non-target writer is independently known to be fixed across paired `q=0/q=1` trials and can see mode but not the current challenge, none of its eight possible tables reproduces all six cells. Testing only `q=1` leaves one exact mode-only twin. Thus challenge variation helps only together with a physical writer-inventory/isolation premise.

This is a negative identification result plus a prospective physical contract. No robot or human was installed, no completed-map node is promoted, and no familiar-mineness endpoint is inferred.

## 2. Typed device-relative domain

Fix a declared device bearer `P_dev`, interval `I`, device signature `K_dev`, retained trace occurrence `m`, target consumer `C`, target writer port `w_T`, finite writer set `W`, arbitration event `g`, actuator transition `a`, plant state transition `x -> x'`, and evidence channels `E`.

Keep distinct:

- the retained trace and the value delivered to `C`;
- the command emitted by `C` and the writer occurrence at `w_T`;
- the post-arbitration actuator transition and a telemetry record;
- the physical plant transition and the endpoint derived from it;
- actual route membership and evidence for that membership;
- the declared device signature and a complete ontic `K` for a UCT token;
- an experience-internal structural coordinate and the external label `H_way`.

The finite model below abstracts only writer identity. It does not assert that a physical actuator is Boolean or that all real writers can be enumerated by software inspection.

## 3. Exact hidden-writer twin

For `q in {0,1}` and `mode in {baseline, block, rescue}`, define the genuine actuator table

```text
G(q,baseline)=q,
G(q,block)=0,
G(q,rescue)=q.
```

The target writer is present in baseline and faithful rescue and is cut in block. Now construct a twin with the target disconnected in every cell. An unlogged writer receives `(q,mode)` and writes `H(q,mode)=G(q,mode)` after the target port. The actuator-proximal value, plant transition and every deterministic endpoint derived from it are identical in the two systems.

### Proposition A4D-N1 — replay does not identify the writer

**Domain.** The six cells above; deterministic plant/readout downstream of the actuator; an unobserved writer with timely access to `(q,mode)`.

**Premises.** The monitor observes declared command, post-arbitration actuator value and downstream transition, but does not independently establish the complete writer set or the provenance of the final write.

**Claim.** There exists a target-idle twin observationally identical on every tested cell.

**Proof.** Set the hidden writer's six-entry truth table equal to `G`. This table is one of the `2^6=64` possible Boolean functions on the tested cells. The exact enumerator finds exactly one full-table match. By construction the target is absent in all six twin cells, while every observed actuator value equals the genuine value. Any deterministic downstream replay is therefore also equal. QED.

This is an application of ordinary unknown-input/causal-identification logic, not a newly invented general control theorem.

## 4. What paired challenge variation can and cannot do

Restrict a hidden writer to a mode-only table `h(mode)`, fixed across paired trials and unable to acquire the current challenge before actuation. There are `2^3=8` such tables.

### Proposition A4D-P1 — bounded exclusion of challenge-blind writers

**Domain.** The same six cells.

**All premises.** (i) non-target writers are actually fixed across the paired challenges; (ii) they cannot access `q` or a correlate before the actuator transition; (iii) the post-arbitration probe is faithful; (iv) the target/rescue interface is the only admitted timely `q` channel; and (v) the block does not create another `q` channel.

**Claim.** No mode-only hidden writer reproduces `G` on all six cells.

**Proof.** At baseline, `G(0,baseline)=0` and `G(1,baseline)=1`, but `h(baseline)` has one fixed value. The same contradiction occurs at rescue. Exhaustive enumeration confirms zero matches among eight tables. QED.

If only `q=1` is tested, one mode-only table exactly matches the three arms. Challenge variation is therefore necessary for this bounded exclusion, but it is not sufficient to establish the physical premises. A hidden writer with timely challenge access restores the A4D-N1 twin.

## 5. Actuator-writer-completeness contract

Call the prospective package `AWC(P_dev,I,K_dev,m,C,w_T,W,g,a,E)` and require jointly:

1. **Frozen boundary and writer inventory.** `P_dev/I/K_dev` and every physical process capable of changing the selected actuator command/energy state during `I` are fixed before outcome inspection.
2. **Transition accounting.** Every selected actuator transition is attributed to one registered writer/arbitration event or to a separately bounded disturbance class; absence from a software log is not absence from `W`.
3. **Faithful target cut.** The cut disables `w_T` before arbitration without directly changing the actuator, plant endpoint or non-target writer policy.
4. **Non-target isolation.** Every non-target writer is cut, held fixed, or independently shown unable to access the current randomized challenge before the selected transition.
5. **Probe placement.** The actuator-proximal measurement occurs after writer arbitration and before the plant transition; a pre-arbitration command log does not satisfy this clause.
6. **Same-interface rescue.** Rescue re-enters through the same declared downstream interface/arbitration contract as the target writer; it does not write the actuator or endpoint directly.
7. **Upstream trace challenge.** Native/swap/block manipulations act before `C`; the challenge has a declared trace-content relation and is not chosen from the endpoint.
8. **Chronology and replay.** Trace delivery precedes consumer emission, writer arbitration precedes actuator transition, and actuator transition precedes plant/endpoint readout; transition replay uses the same law and registered disturbances.

If the full package holds and paired challenges reject every admitted non-target explanation, the result supports target-route use **within that declared device model**. It does not prove that `K_dev` is a complete UCT signature, that the process is admitted under C1, or that the route is familiar mineness.

## 6. Relation to A4C, R172 and R173

A4D narrows A4C-G2. A4C's replay condition excludes a direct endpoint overwrite but not an actuator-level overwrite that itself replays. A4D therefore moves the required evidence boundary one causal step closer to the physical plant and makes writer enumeration/isolation explicit.

For R172, logs and tests remain `CertUse_path` evidence, not `OnticUse_path`. `AWC` is a sufficient evidence package only relative to its physical premises. It must not be inserted as an internal experiential relation.

For R173, a physical AWC result would still establish at most part of `CurrentFrameConsumerUse`. The earlier same-lineage occurrence, trace continuation, complete actual-token binding, C1 instance, parameter transport and independent `B_fam` remain separate simultaneous premises. The completed all-of route is not fired.

## 7. Thought-experiment battery

| Family | Fixed | Varied | Counterexample role |
|---|---|---|---|
| Ancestor / formation | present actuator trajectory | whether an unlogged descendant process writes it | equal mature behavior does not identify which retained formation route remains active |
| Abacus / calculator | displayed answer and visible key log | hidden magnet or direct motor writer | replay of the display and logged keys can coexist with a bypass at the bead/actuator level |
| Human-realized agent | abstract controller and output | whether a participant silently supplies the physical action | software writer completeness can fail because constitutive human activity is outside `K_dev` |
| Copy / switch / memory | challenge table and plant trajectory | target writer versus challenge-aware duplicate writer | numerical equality and same endpoint leave actual writer identity underdetermined |

These witnesses do not select a unique owner. Nested and overlapping actual processes remain allowed.

## 8. External source comparison and novelty boundary

Pasqualetti, Dörfler and Bullo model attacks as unknown inputs and give conditions for undetectable/unidentifiable attacks in cyber-physical systems. Hosseinzadeh and Sinopoli study active detection for prevented actuation attacks. They support the general methodological point that unmodelled actuator-side inputs can defeat monitoring and that active intervention needs explicit plant/attack assumptions.

A4D does not rename unknown-input detectability, replay-attack detection or active monitoring as a UCT discovery. Its project-specific contribution is to locate the writer-completeness obligation inside the existing formation–retention–current-use evidence ladder and to preserve the organization/experience/semantic boundaries.

## 9. Negative results and stop rule

- Full actuator replay is insufficient if writer provenance is not independently grounded.
- A single nonzero challenge is insufficient even against a mode-only writer.
- Random challenges are not magical: if a hidden writer receives them in time, the exact twin returns.
- Source inspection cannot prove physical writer completeness for a device with omitted firmware, bus masters, safety controllers, power stages, mechanical couplings or human interventions.
- No physical robot, human, complete `K`, C1 admission, `RetBind`, `F_F`, `B_fam` or `H_way` result is claimed.

Stop at `DEVICE_RELATIVE_ROUTE_EVIDENCE` unless all AWC clauses are independently evidenced on one device and interval. Even then, stop before phenomenal interpretation until the separate target/measurement bridge is supplied.

## 10. Direction check after result

**PASS.** The result directly repairs a route-evidence weakness in the positive bodily/action organization account. It neither optimizes a controller nor substitutes an endpoint for experience. It clarifies what a future physical robot installation would have to establish before UCT's conditional structural transport could even be considered, while leaving C1, U1, `B_fam`, conceptual I and report in their proper roles.

