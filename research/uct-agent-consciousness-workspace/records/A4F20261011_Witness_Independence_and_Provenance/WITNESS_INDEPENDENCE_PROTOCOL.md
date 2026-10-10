# A4F witness-independence protocol

## Intended conclusion

`DEVICE_RELATIVE_CURRENT_SOURCE_EVIDENCE(P_dev,I,T,e)` only. The protocol never returns a complete UCT token, experience predicate, familiar-mineness label, report identity or exclusive owner.

## Pre-registration

1. Freeze `P_dev`, interval `I`, `K_dev`, final arbitration boundary, target source `T`, every admitted alternative source, disturbance class and evidence controller.
2. Draw the physical command/energy path and separately draw the power, reset, clock, bus, DMA, logger and human-control ancestry of every witness channel.
3. State the device-specific transition law, pre-state verifier, challenge generator and clock order.
4. Enumerate for every source the complete witness vectors it can realize, including forge, replay, suppression, reset, delay and downstream-injection permissions.
5. Declare the target vector and the exact disjointness checks before outcome inspection.

## Required arms

| Arm | Target path | Alternative path | Fresh anti-current challenge | Required observation |
|---|---|---|---|---|
| no event | disabled | disabled | yes | no commit; all source taps inactive |
| target native | enabled | isolated | yes | current commit and target-specific vector |
| target cut | cut locally | isolated | yes | pre-state held or declared failure vector |
| same-interface rescue | restored at audited interface | isolated | yes | current commit and target-specific vector |
| each alternative source | disabled | one alternative enabled | yes | a vector disjoint from the target vector |
| replay/reset fault | as declared | injected fault | yes | replay/reset rejection or explicit invalidation |
| common-controller fault | as declared | common root perturbed | yes | dropout/failure, not a falsely accepted target vector |

## Admission rule

Admit target-source evidence only if, for every registered alternative `h`, the empirically and architecturally allowed accepted-vector sets satisfy `R_target ∩ R_h = empty` on the same device, interval and frozen architecture. A second file, checksum or statistical independence score is not a substitute for physical control independence.

## Stop rules

- An unlisted writer or common evidence controller stops source attribution.
- A pre-arbitration source label stops source attribution.
- A source-agnostic transition sensor permits only event-occurrence evidence.
- Failure of cut locality, rescue interface identity, freshness or chronology stops the corresponding comparison.
- Success stops at device-relative source evidence; the separate R173 and phenomenal obligations remain open.

