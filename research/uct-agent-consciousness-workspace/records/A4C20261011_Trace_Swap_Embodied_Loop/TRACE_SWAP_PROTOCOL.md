# A4C trace-content swap protocol

## Declared domain

The installed object is a deterministic one-dimensional embodied **simulation** with one software bearer, one retained-trace store, one current body-loop consumer, two formation contexts, one plant law and one organizational endpoint. It is not a physical robot or human, is not admitted as a complete `P_actual` token, and has no phenomenal endpoint.

The plant and controller are

```text
x[t+1] = x[t] + u[t] + b
u[t]   = -0.5*x[t] - z
```

where `b` is the context's physical disturbance and `z` is the trace value delivered at the named consumer interface. Formation estimates `b` from four earlier calibration events in each context and stores both traces in the same bearer.

## Fixed items

- bearer: `A4C-embodied-simulation-bearer-v1`
- consumer: `A4C-body-loop-consumer-v1`
- plant, gain, start state, 12-step horizon and endpoint rule
- contexts `plus` (`b=+1`) and `minus` (`b=-1`)
- formation process, trace schema, carrier, digest validation and action ledger
- endpoint: final context-aligned signed state `b*x[12]`
- endpoint collector reads no intervention label before the registry join

## Intervention arms

| Arm | Native read | Value delivered at consumer | Route-local meaning |
|---|---:|---|---|
| intact | yes | native same-context trace | positive route control |
| swap | no | opposite-context trace from the same bearer | content-specific perturbation |
| block | no | zero | read removal |
| rescue | blocked | faithful native value at the consumer interface | route-local rescue |

All four arms retain the bearer, consumer, plant and endpoint rule. The selector takes only `(store, context, mode)` and returns a consumer input. It receives neither plant state nor endpoint. A static source audit and action-ledger replay test this declared locality; neither proves absence of unrepresented physical channels.

## Predeclared directional test

Across balanced contexts:

```text
mean(intact) = mean(rescue) < mean(block) < mean(swap).
```

The swap prediction is not merely that an endpoint changes. The opposite-context content should double the uncompensated disturbance relative to blocking, and every action must replay to the recorded endpoint.

## Exclusion witness

An endpoint-only twin copies the swap endpoint onto an intact action ledger. It matches the final number but fails replay and the no-direct-write clause. Therefore endpoint equality or endpoint direction alone is not evidence of a retained route.

## Stop rule

Stop at a software/simulation organizational result if any bearer, chronology, validation, consumer, replay, locality, blinding or directional check fails. Even on success, do not infer a physical robot/human route, complete `K`, `H_way`, familiar mineness, C1's empirical truth, unique ownership, report identity or basal-experience gate.

Run with:

```bash
python records/A4C20261011_Trace_Swap_Embodied_Loop/run_trace_swap_study.py run
```
