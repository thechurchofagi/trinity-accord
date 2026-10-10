# A4D prospective actuator-writer protocol

## Aim and scope

Test whether a named retained-trace consumer reaches a selected physical actuator transition through a declared writer port, rather than through an unlogged parallel writer. This is a preinstallation device-relative protocol, not a completed robot/human experiment and not a phenomenal endpoint.

## Frozen objects

- one device bearer `P_dev`, interval `I` and declared device signature `K_dev`;
- retained trace carrier `m`, consumer `C`, target writer `w_T`, arbitration event `g`, actuator transition `a`, plant transition and endpoint;
- complete claimed writer set `W`, including firmware, bus masters, safety/override controllers, power-stage control, direct mechanical/energy inputs and human/manual paths inside the selected boundary;
- a randomized paired challenge `q in {0,1}` generated after non-target policies are frozen;
- baseline, target-cut and same-interface rescue modes;
- a post-arbitration/pre-plant probe and independent clock binding.

## Required arms

| Arm | Upstream trace/consumer | Target writer | Non-target writers | Expected actuator relation |
|---|---|---|---|---|
| baseline | challenge reaches `C` | enabled | isolated/fixed | transition follows `q` |
| cut | same challenge schedule | disabled before arbitration | isolated/fixed | selected `q` dependence disappears |
| rescue | native target remains cut; faithful value enters same interface | rescue through target interface | isolated/fixed | `q` dependence returns |
| hidden-writer negative control | target idle | disabled | one declared alternative allowed | must reveal the probe/inventory failure rather than count as target use |

## Joint admissibility clauses

All eight AWC clauses in `RESEARCH_NOTE.md` are AND premises. A failed clause yields a typed non-result:

- `INVALID_WRITER_INVENTORY`
- `INVALID_CUT_LOCALITY`
- `INVALID_NON_TARGET_ISOLATION`
- `INVALID_PROBE_PLACEMENT`
- `INVALID_RESCUE_INTERFACE`
- `INVALID_TRACE_CHALLENGE`
- `INVALID_CHRONOLOGY_OR_REPLAY`
- `INCONCLUSIVE_DEVICE_RELATIVE`
- `DEVICE_RELATIVE_ROUTE_EVIDENCE`

No failure state is evidence of no experience, no familiarity or no route outside the declared device model.

## Falsifiers

The target-route claim fails if any unregistered writer can reproduce the paired challenge, if the probe is upstream of arbitration, if rescue bypasses the target interface, if the cut changes plant or other-writer behavior directly, or if actuator/plant replay fails under the registered transition law.

## Return to the UCT main line

If and only if the device-relative package succeeds, combine it with independently grounded formation lineage and current trace consumption. Do not infer a complete actual UCT signature or `H_way`. The next UCT question remains whether a complete same-instance physical relation is admitted and, separately, whether an independently fixed `B_fam` maps it to familiar bodily/action mineness.

