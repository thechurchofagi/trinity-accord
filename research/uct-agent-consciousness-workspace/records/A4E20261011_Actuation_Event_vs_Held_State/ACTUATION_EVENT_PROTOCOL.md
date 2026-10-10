# A4E reset, anti-current challenge and event-witness protocol

## Aim

Distinguish a current actuator commit from a held prior state, then combine that result with A4D writer completeness. This is a prospective bounded-device protocol, not an installed robot or phenomenal measurement.

## Frozen trial contract

Freeze one device boundary, actuator, transition law, arbitration interval, writer inventory, target writer, same-interface rescue and independent clock. Immediately before arbitration record the physical pre-state `s-`. Generate `q=1-s-` only after non-target policies are frozen. A valid positive trial must show:

| Arm | Target route | Required level/event |
|---|---|---|
| baseline | enabled | timely transition `s- -> q` |
| target cut | faithfully disabled | no target commit and level remains `s-` |
| same-interface rescue | native route cut; rescue at same interface | timely transition `s- -> q` |
| hidden-writer negative control | target idle; declared alternative enabled | must be detected as non-target or invalidate completeness |

## Probe grades

1. `LEVEL_ONLY_UNINFORMATIVE` when `q=s-`.
2. `LEVEL_CHANGE_SOME_WRITE` when verified `q!=s-` and `s+=q`, but writer identity is not yet established.
3. `BOUND_EVENT_WITNESS` only when commit, selected physical writer, value and timestamp are captured after arbitration and before plant dynamics.
4. `DEVICE_RELATIVE_TARGET_ROUTE_EVIDENCE` only when grade 2 or 3 is conjoined with all A4D inventory, isolation, cut, rescue and chronology clauses.

## Invalid outcomes

An unverified pre-state, preselected/repeated challenge, level-only same-value observation, missing null/no-commit representation, asynchronous update, autonomous actuator drift, upstream provenance label, or rescue bypass yields `INVALID_OR_INCONCLUSIVE_ACTUATION_EVENT`. It is not evidence of no experience or no familiar mineness.
