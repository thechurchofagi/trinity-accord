# Area-3a downstream-use endpoint contract

## Frozen same-instance tuple

Freeze one animal, limb, source intervention `S`, area-3a response variable `R`, neighbouring-region record, area-3a block `G`, matched neighbour and sham operations, replay/rescue operation `Q`, downstream endpoint `Y`, common hardware clock, analysis window, admissible spillover class and exclusion evidence before outcomes are examined.

`Y` must be acquired by a sensor or process whose value is not computed from the analyzed area-3a channel. This prevents circular readout, but it does **not** by itself prove that `R` causes `Y`.

## Endpoint causal firewall

| Gate | Required evidence | Failure code | What passing does not establish |
|---|---|---|---|
| `E` endpoint independence | `Y` has a predeclared physical acquisition/construction path independent of the analyzed `R` samples | `POSTHOC_ENDPOINT` | mediation or experience |
| `S` source stability | source delivery, peripheral volley, movement and contact remain within the declared matched envelope | `SOURCE_DRIFT` | source purity outside that envelope |
| `B` selective block | `G` changes the declared area-3a signal before `Y`, with dose, latency, spatial footprint and recovery checks | `INVALID_BLOCK` | absence of remote network effects |
| `N` region controls | matched neighbouring-region and sham operations are logged on the same clock | `NO_REGION_CONTROL` | exclusion of an area-3a-specific off-target path |
| `X` exclusion witness | independent evidence bounds direct `G→Y` and shared-writer routes outside the declared `R→Y` path | `EXCLUSION_UNGROUNDED` | all unimagined alternatives |
| `Q` path-specific rescue | while `G` remains active, `Q` faithfully restores the relevant signal at the named downstream port, with its own no-direct-effect check | `NO_SELECTIVE_RESCUE` | arbitrary-mechanism identification |
| `T` chronology | issue, arrival, local effect, rescue, consumer event and endpoint are ordered on one clock | `CLOCK_OR_ORDER_FAILURE` | complete organization |

All `E∧S∧B∧N∧X∧Q∧T` premises apply to one episode family. They cannot be assembled from different animals or studies. A failed manipulation or exclusion check is `INVALID_PROTOCOL`, not evidence of no use, no mineness or no experience.

## Exact declared-model targets

For binary exposition, let `S` denote source delivery, `G` the validated area-3a block, `R` the local signal, `Q` a faithful downstream replay and `Y` the external endpoint.

- **Use model:** `R=S(1-G)`, `Y=R∨(QS)`.
- **Spill model:** `R=S(1-G)`, `Y=S(1-G)` through a direct `G→Y` suppression; `R` is not consumed.

With `Q=0`, both models agree on every `S×G` cell, including the apparently causal cell in which area-3a block suppresses both `R` and `Y`. Neighbour and sham controls can also be identical because the direct off-target effect may be specific to the area-3a intervention. Therefore region controls are necessary but not sufficient.

With `S=G=Q=1`, the declared use model has `(R,Y)=(0,1)` and the spill model `(0,0)`. This rescue contrast separates **these two models only if** the block and replay exclusion premises are independently supported. If `Q` itself drives `Y`, or `G` still directly suppresses `Y`, rescue is not path-specific.

## Interpretation ladder

1. `E+S+B+N+T`: a well-bound perturbation-associated endpoint contrast.
2. plus `X`: a bounded candidate for area-3a-mediated contribution relative to the declared alternative class.
3. plus `Q`: a discriminating rescue within the declared two-model class.
4. plus actual bearer, interval, complete-signature and route-membership evidence: an actual organizational-use candidate.
5. plus C1: a conditional experience-internal structural counterpart.
6. plus an independently calibrated `H` bridge: only then a candidate familiar-mineness interpretation.

No rung is a new basal-experience threshold, and none chooses a unique owner.
