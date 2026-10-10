# SCU20261010 source protocol v0.2

This is a finite mechanism protocol. No human or robot experiment is claimed.

## 0. Freeze the objects before probing

Record the same installation, effector, source carrier addresses, source emission events, motor intake, predictive intake, time order, reset state, plant map, and allowed interventions. Distinguish local support from external imposition and remote production by independently specified generator paths and process boundaries; do not derive these roles from a report or a success score.

State which model is being tested: fixed pure single-source consumer paths, an independently known motor source, or OR consumers of arbitrary nonempty source subsets. These support different exact query budgets. State whether the observer receives two individual readouts or only their mismatch. Validate the readouts and intervention addresses separately from the sought source equality.

## 1. Matched nominal comparison

Supply target `t` simultaneously to every source site and execute both nominal targets `0,1`. The selected actuator and predictor should both return `t` for every route allocation. Repeat with a target word if testing state traces; an initially calibrated R204 forward table remains unchanged under either feedback writer. Record actual write events separately from forward values.

All subsequent probe results are relative to the frozen installation. Probe perturbations may change success and prediction alignment; the claimed baseline matching does not extend to those values under intervention.

## 2. Choose the exact source query

### Unknown pure-route roots

For `n>=2`, assign the sources distinct binary words of length `ceil(log2 n)` and deliver one column-bit pattern per probe. The three-source schedule is `(0,1,0)`, then `(0,0,1)`. Under the contract, an all-zero mismatch vector supports equality of root sources. Any positive mismatch shows that the fixed roots differ. An all-zero vector alone never selects which source is shared.

If individual actuator/predictor readouts are available, decode each source through its unique code. If some source codes collide, report the exact remaining code fibers rather than selecting a source arbitrarily.

### Independently known motor root

Set the known motor source to `0` and every alternative source to `1`. Zero mismatch supports equality with that root under the fixed pure-route contract. One query is the exact minimum for `n>=2`. The same one-query conclusion holds against a nonempty OR predictor subset; an empty constant-zero predictor is outside this extension.

### Unknown nonempty OR source subsets

Use all `n` unit patterns `e_i`. The mismatch vector is the symmetric-difference indicator of the two source sets. This requires `n` probes in the worst case, even adaptively. The short binary code is invalid for this larger class: run the supplied four-source disjoint-set alias as a mandatory negative control if that class boundary is relevant.

## 3. Test the resolution of the source conclusion

Construct the shared-relay and separate-relay alternatives with one common root. Verify their complete source/consumer value tables match. Then distinguish:

- a write to the actual physical carrier read by the predictor, which reaches both consumers when the carrier is shared;
- a replacement signal injected only onto the predictor input edge, which reaches that branch alone in both alternatives.

A source-level result identifies composite ancestry only. A carrier result additionally requires validated physical targeting, timing, no compensating writer, and fixed consumer connections. Preserve the exact intervention event as a new origin; do not label injected data as an old source token.

## 4. Reject post-consequence prediction mimics

Run the late sensory-copy adversary. It has the same values on every source input but computes the alleged prediction after actuation. If time-order evidence is absent, return `PREDICTOR_ROLE_UNRESOLVED` even when source-code classification succeeds.

## 5. Required result classifications

1. `INVALID_SOURCE_ACCESS`: required source patterns cannot be delivered independently.
2. `INVALID_OR_UNRESOLVED_CLASS`: routes switch, unmodeled writers/bypasses intervene, or the claimed consumer class is not defended.
3. `PURE_ROOT_CONFLUENCE_SUPPORTED_RELATIVE_TO_CONTRACT`: valid pure-route code and zero mismatch; locality and intake identity remain separately unresolved.
4. `PURE_ROOT_DIFFERENCE_SUPPORTED_RELATIVE_TO_CONTRACT`: valid pure-route code and some mismatch.
5. `OR_ROOT_SET_EQUALITY_OR_DIFFERENCE_SUPPORTED_RELATIVE_TO_CONTRACT`: valid unit schedule in the OR class, reporting the symmetric difference.
6. `INTAKE_OCCURRENCE_UNRESOLVED`: source values match but carrier identity or node intervention premises are missing.
7. `PREDICTOR_ROLE_UNRESOLVED`: pre-consequence chronology has not been independently established.

These statuses may coexist at different target levels. None is a phenomenal label, an experience threshold, or a conclusion about RetBind or personal numerical identity. Applying the result to a previous unperturbed episode additionally requires same-installation and route-stability evidence; counterfactual source response is not an archived proof of that past read.

## Reproduction

Run `python check_source_consumers.py` in the module directory. The checker writes `EXACT_RESULTS.json`, `RUN_RECEIPT.json`, and `THREE_SOURCE_ROUTE_TABLE.csv`. Assertions test finite event models and independent schedule search; they do not verify the physical premises of any external device.
