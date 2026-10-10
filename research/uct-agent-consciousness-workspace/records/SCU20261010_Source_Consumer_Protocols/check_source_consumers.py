#!/usr/bin/env python3
"""SCU20261010 exact finite source/consumer protocol; no phenomenal variable.

The event simulator, exhaustive intervention set-cover search, and analytic code
construction are separate implementations. Constants are not passed in as
'active/passive/self' role answers. The selected consumer paths perform reads.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, product
from pathlib import Path
import csv
import hashlib
import json
import platform
import time


@dataclass(frozen=True)
class Occurrence:
    name: str
    carrier: str
    time: int
    value: int
    parents: tuple[str, ...]


@dataclass(frozen=True)
class Episode:
    action: int
    prediction: int
    mismatch: int
    installed_action_sources: tuple[int, ...]
    installed_prediction_sources: tuple[int, ...]
    action_origins: tuple[str, ...]
    prediction_origins: tuple[str, ...]
    action_intake: str
    prediction_intake: str
    prediction_precedes_action: bool
    events: tuple[Occurrence, ...]


def episode(
    x: tuple[int, ...], action_sources: tuple[int, ...],
    prediction_sources: tuple[int, ...], *, realization: str = "direct",
    prediction_node_clamp: int | None = None,
    prediction_edge_clamp: int | None = None,
) -> Episode:
    """Emit source tokens, copy/aggregate if installed, then execute both reads.

    Source tuples use OR when length > 1. The direct single-source class is the
    logarithmic theorem domain. Other realizations are explicit adversaries.
    A node clamp targets the physical carrier used by the predictor. A branch
    clamp replaces only the signal at its incoming edge.
    """
    assert x and all(v in (0, 1) for v in x)
    assert action_sources and prediction_sources
    events: list[Occurrence] = []
    carriers: dict[str, Occurrence] = {}

    def emit(name: str, carrier: str, phase: int, value: int,
             parents: tuple[str, ...]) -> Occurrence:
        event = Occurrence(name, carrier, phase, value, parents)
        events.append(event)
        carriers[carrier] = event
        return event

    roots = [emit(f"s{i}", f"source{i}", 0, v, ()) for i, v in enumerate(x)]

    def source_signal(indices: tuple[int, ...], role: str) -> Occurrence:
        if len(indices) == 1:
            return roots[indices[0]]
        parents = tuple(roots[i].name for i in indices)
        # Execute every source-value read before the Boolean aggregation.
        # A short-circuit generator here would not justify treating every
        # listed parent as dynamically read in the modeled episode.
        values = tuple(roots[i].value for i in indices)
        value = int(any(values))
        return emit(f"aggregate_{role}", f"aggregate_{role}", 1, value, parents)

    motor = source_signal(action_sources, "motor")
    pred = source_signal(prediction_sources, "prediction")
    if realization == "shared_relay":
        assert action_sources == prediction_sources and len(action_sources) == 1
        shared = emit("shared_copy", "shared_register", 1, motor.value, (motor.name,))
        motor = pred = shared
    elif realization == "separate_relays":
        motor = emit("motor_copy", "motor_register", 1, motor.value, (motor.name,))
        pred = emit("prediction_copy", "prediction_register", 1, pred.value, (pred.name,))
    elif realization not in ("direct", "late_sensory_bypass"):
        raise ValueError(realization)

    if prediction_node_clamp is not None:
        # Locate the actual predictor-intake carrier; a shared carrier write is
        # visible to both consumers. Its physical identity is a premise.
        emit("node_injection", pred.carrier, 2, prediction_node_clamp, ())
    motor = carriers[motor.carrier]
    pred = carriers[pred.carrier]
    if prediction_edge_clamp is not None:
        pred = emit("edge_injection", "prediction_edge", 2,
                    prediction_edge_clamp, ())
    if realization == "late_sensory_bypass":
        action_event = emit("actuation", "actuator", 3, motor.value, (motor.name,))
        pred = emit("late_sensory_copy", "late_prediction_register", 4,
                    action_event.value, (action_event.name,))
        prediction_event = emit("prediction_read", "prediction_readout", 5,
                                pred.value, (pred.name,))
        pred_roots = action_sources
    else:
        prediction_event = emit("prediction_read", "prediction_readout", 3,
                                pred.value, (pred.name,))
        action_event = emit("actuation", "actuator", 4, motor.value, (motor.name,))
        pred_roots = prediction_sources
    by_name = {event.name: event for event in events}

    def leaf_origins(event_name: str) -> set[str]:
        event = by_name[event_name]
        if not event.parents:
            return {event_name}
        out: set[str] = set()
        for parent in event.parents:
            out.update(leaf_origins(parent))
        return out

    # Configured installation roots and actually consumed provenance diverge
    # under node/edge writes. Injection leaves remain explicit; they are not
    # mislabeled as the superseded source registers.
    return Episode(action_event.value, prediction_event.value,
                   action_event.value ^ prediction_event.value,
                   action_sources, pred_roots,
                   tuple(sorted(leaf_origins(action_event.name))),
                   tuple(sorted(leaf_origins(prediction_event.name))),
                   motor.carrier, pred.carrier,
                   prediction_event.time < action_event.time, tuple(events))


def binary_schedule(n: int) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple((i >> bit) & 1 for i in range(n))
                 for bit in range((n - 1).bit_length()))


def probe_trace(n: int, a: tuple[int, ...], b: tuple[int, ...], schedule,
                **kwargs) -> tuple[int, ...]:
    return tuple(episode(tuple(x), a, b, **kwargs).mismatch for x in schedule)


def nonempty_subsets(n: int) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(i for i in range(n) if mask >> i & 1)
                 for mask in range(1, 1 << n))


def nominal_forward_trace(n: int, a: int, b: int, word: tuple[int, ...],
                          gate: int, writer: str):
    """Install R204's predictor-row law on the yoked source allocation.

    Return the actual forward-register state trajectory and selected values;
    write-event occurrences are recorded separately from value transitions.
    """
    forward = [0, 1]
    state_trace = [tuple(forward)]
    values = []
    writes = []
    for t in word:
        e = episode((t,) * n, (a,), (b,))
        predicted = forward[e.prediction]
        values.append((e.action, predicted))
        should_write = bool(gate and (writer == "reflex" or predicted != e.action))
        if should_write:
            forward[e.prediction] = e.action
        writes.append(should_write)
        state_trace.append(tuple(forward))
    return tuple(state_trace), tuple(values), tuple(writes)


def exact_minimum_separating_schedule(n: int, redundant: bool) -> dict:
    """Independently solve the finite set-cover problem by exhaustive subsets.

    An intervention covers a pair of distinct source sets iff the two actual
    OR consumers disagree. Equality produces the all-zero transcript. Remove
    only probes that provably cover no pair; enumerate every remaining subset
    until a full cover exists. No analytic lower bound is passed to this code.
    """
    candidates = nonempty_subsets(n) if redundant else tuple((i,) for i in range(n))
    pairs = tuple(combinations(candidates, 2))
    all_covered = (1 << len(pairs)) - 1
    probes = []
    masks = []
    for x in product((0, 1), repeat=n):
        mask = 0
        # Separate evaluator from the event simulator.
        outputs = {s: int(any(x[i] for i in s)) for s in candidates}
        for j, (a, b) in enumerate(pairs):
            if outputs[a] != outputs[b]:
                mask |= 1 << j
        if mask:
            probes.append(x)
            masks.append(mask)
    checked = 0
    for k in range(len(probes) + 1):
        winners = []
        for indices in combinations(range(len(probes)), k):
            checked += 1
            coverage = 0
            for idx in indices:
                coverage |= masks[idx]
            if coverage == all_covered:
                winners.append(indices)
        if winners:
            return {
                "n": n, "consumer_class": "nonempty_OR_subsets" if redundant else "single_source",
                "minimum_probes": k, "candidate_source_sets": len(candidates),
                "distinct_pairs_to_separate": len(pairs),
                "all_schedules_checked_through_minimum": checked,
                "optimal_schedule_count": len(winners),
                "one_optimum": [list(probes[i]) for i in winners[0]],
            }
    raise AssertionError("Unit probes must separate every distinct source set.")


def main() -> None:
    started = time.time()
    counts = {"baseline_episodes": 0, "coded_pure_route_episodes": 0,
              "all_matrix_fiber_pairs": 0, "known_root_episodes": 0,
              "relay_source_comparisons": 0, "transported_source_coordinate_comparisons": 0,
              "nominal_forward_state_word_comparisons": 0,
              "OR_unit_probe_pairs": 0}
    n3_rows = []
    # Baseline success/alignment for every actual one-source path allocation.
    # Constants denote only physical source addresses, not phenomenology.
    for n in range(2, 9):
        schedule = binary_schedule(n)
        for a, b in product(range(n), repeat=2):
            for target in (0, 1):
                e = episode((target,) * n, (a,), (b,))
                assert e.action == target and e.prediction == target
                assert e.mismatch == 0 and e.prediction_precedes_action
                counts["baseline_episodes"] += 1
            observed = []
            for x in schedule:
                e = episode(x, (a,), (b,))
                observed.append(e.mismatch)
                counts["coded_pure_route_episodes"] += 1
            assert (not any(observed)) == (a == b)
            if n == 3:
                n3_rows.append({"motor_root": a, "predictor_root": b,
                                "baseline_success": 1, "baseline_alignment": 1,
                                "same_root": int(a == b),
                                "probe_1_mismatch": observed[0],
                                "probe_2_mismatch": observed[1]})
            # Exact same-root probe given independently known motor root.
            x = tuple(int(i != a) for i in range(n))
            e = episode(x, (a,), (b,))
            assert (e.mismatch == 0) == (a == b)
            counts["known_root_episodes"] += 1

    # Every binary nominal target word through length four, all 3x3 route
    # allocations and both R204 writer implementations/gates. Word equality
    # is stronger than matching only the first successful episode.
    for length in range(5):
        for word in product((0, 1), repeat=length):
            reference = nominal_forward_trace(3, 0, 0, word, 0, "error_gated")
            for a, b, gate, writer in product(range(3), range(3), (0, 1),
                                             ("error_gated", "reflex")):
                trace = nominal_forward_trace(3, a, b, word, gate, writer)
                assert trace[:2] == reference[:2]
                counts["nominal_forward_state_word_comparisons"] += 1

    # Every k-probe binary matrix for n<=4 and k<=ceil(log2 n), including
    # degenerate/colliding codes. Check exact observation fibers, not just the
    # hand-picked optimum.
    for n in range(2, 5):
        for k in range((n - 1).bit_length() + 1):
            for columns in product(range(1 << k), repeat=n):
                schedule = tuple(tuple((c >> bit) & 1 for c in columns) for bit in range(k))
                for a, b in product(range(n), repeat=2):
                    observed = probe_trace(n, (a,), (b,), schedule)
                    assert (not any(observed)) == (columns[a] == columns[b])
                    counts["all_matrix_fiber_pairs"] += 1

    # Full source interventions do not distinguish a shared relay occurrence
    # from equal-valued copies with the same source ancestry.
    for n in range(2, 6):
        for a in range(n):
            for x in product((0, 1), repeat=n):
                shared = episode(x, (a,), (a,), realization="shared_relay")
                copied = episode(x, (a,), (a,), realization="separate_relays")
                assert (shared.action, shared.prediction) == (copied.action, copied.prediction)
                assert shared.action_intake == shared.prediction_intake
                assert copied.action_intake != copied.prediction_intake
                counts["relay_source_comparisons"] += 1
                # Execute again after a transported cyclic permutation of
                # all source coordinates. This checks route parameters and
                # actual source inputs are moved together, not placards only.
                perm = tuple((i + 1) % n for i in range(n))
                transported_x = [0] * n
                for i, value in enumerate(x):
                    transported_x[perm[i]] = value
                transported = episode(tuple(transported_x), (perm[a],), (perm[a],),
                                      realization="separate_relays")
                assert (copied.action, copied.prediction) == (transported.action, transported.prediction)
                assert transported.installed_action_sources == tuple(perm[i] for i in copied.installed_action_sources)
                assert transported.action_origins == (f"s{perm[a]}",)
                counts["transported_source_coordinate_comparisons"] += 1

    # Node-vs-edge intervention distinction: a common carrier write differs
    # from replacing just one consumer edge. Edge evidence does not establish
    # that upstream intake occurrences are one numerical carrier.
    intervention_controls = []
    for realization in ("shared_relay", "separate_relays"):
        node = episode((0, 0, 0), (0,), (0,), realization=realization,
                       prediction_node_clamp=1)
        edge = episode((0, 0, 0), (0,), (0,), realization=realization,
                       prediction_edge_clamp=1)
        intervention_controls.append({"realization": realization,
                                      "node_clamp": [node.action, node.prediction],
                                      "edge_clamp": [edge.action, edge.prediction],
                                      "node_clamp_actual_origins": [list(node.action_origins), list(node.prediction_origins)],
                                      "edge_clamp_actual_origins": [list(edge.action_origins), list(edge.prediction_origins)]})
    assert intervention_controls[0]["node_clamp"] == [1, 1]
    assert intervention_controls[1]["node_clamp"] == [0, 1]
    assert intervention_controls[0]["edge_clamp"] == intervention_controls[1]["edge_clamp"] == [0, 1]
    assert intervention_controls[0]["node_clamp_actual_origins"] == [["node_injection"], ["node_injection"]]
    assert intervention_controls[1]["node_clamp_actual_origins"] == [["s0"], ["node_injection"]]
    assert intervention_controls[0]["edge_clamp_actual_origins"] == intervention_controls[1]["edge_clamp_actual_origins"] == [["s0"], ["edge_injection"]]

    # Sensory echo masquerading as prediction: source I/O signatures match,
    # but audited chronology rejects the pre-consequence-predictor role.
    late_bypass = []
    for x in product((0, 1), repeat=3):
        direct = episode(x, (0,), (0,))
        late = episode(x, (0,), (2,), realization="late_sensory_bypass")
        assert (direct.action, direct.prediction, direct.mismatch) == (late.action, late.prediction, late.mismatch)
        assert direct.prediction_precedes_action and not late.prediction_precedes_action
        late_bypass.append({"input": list(x), "readouts": [late.action, late.prediction],
                            "valid_predictive_chronology": False})

    # The canonical two-bit code for four single sources aliases a disjoint
    # redundant OR source set. This refutes the overgeneralized pure-route test.
    n = 4
    schedule = binary_schedule(n)
    alias = probe_trace(n, (3,), (1, 2), schedule)
    unit = tuple(tuple(int(i == j) for i in range(n)) for j in range(n))
    corrected = probe_trace(n, (3,), (1, 2), unit)
    assert not any(alias) and any(corrected)
    or_alias = {"motor_sources": [3], "predictor_sources": [1, 2],
                "binary_source_code": [list(x) for x in schedule],
                "binary_code_mismatch_trace": list(alias),
                "unit_probe_mismatch_trace": list(corrected),
                "baseline_0_and_1_both_successful_calibrated": True,
                "source_sets_disjoint": True}

    for n in range(2, 6):
        unit = tuple(tuple(int(i == j) for i in range(n)) for j in range(n))
        for a, b in product(nonempty_subsets(n), repeat=2):
            trace = probe_trace(n, a, b, unit)
            assert (not any(trace)) == (a == b)
            counts["OR_unit_probe_pairs"] += 1

    # Independent exact optimization, not a numerical restatement of formula.
    optima = []
    for n in range(2, 6):
        for redundant in (False, True):
            result = exact_minimum_separating_schedule(n, redundant)
            expected = n if redundant else (n - 1).bit_length()
            assert result["minimum_probes"] == expected
            optima.append(result)

    output = {
        "result_id": "SCU-RESULT-v0.2.0", "status": "PASS",
        "violations": 0, "scope": "Finite controlled source/consumer event models only",
        "phenomenal_variables_generated": False,
        "counts": counts, "n3_unknown_source_schedule": [list(x) for x in binary_schedule(3)],
        "n3_all_route_allocations": n3_rows,
        "exhaustive_minimum_probe_results": optima,
        "relay_node_edge_controls": intervention_controls,
        "postconsequence_bypass_counterexample": late_bypass,
        "OR_redundancy_counterexample": or_alias,
        "key_boundaries": [
            "Unknown pair, fixed pure routes, independent binary source addressing: ceil(log2 n).",
            "Independently known single motor root: one complement probe for n>=2.",
            "Arbitrary nonempty OR root sets at both consumers: n probes for uniform equality decision.",
            "Source signatures identify source-ancestry fibers, not relay factorization or intake occurrence identity.",
            "Actual retrospective token use, RetBind, local membership, felt agency and H are not inferred.",
            "Nominal success/alignment are fixed; diagnostic interventions deliberately change inputs."
        ],
    }
    here = Path(__file__).resolve().parent
    encoded = json.dumps(output, indent=2) + "\n"
    (here / "EXACT_RESULTS.json").write_text(encoded)
    with (here / "THREE_SOURCE_ROUTE_TABLE.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(n3_rows[0]))
        writer.writeheader()
        writer.writerows(n3_rows)
    receipt = {
        "result_id": output["result_id"], "command": "python check_source_consumers.py",
        "python": platform.python_version(), "elapsed_seconds": round(time.time() - started, 6),
        "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "result_sha256": hashlib.sha256(encoded.encode()).hexdigest(),
        "status": "PASS", "empirical_participants": 0,
        "actual_device_or_neural_experiment": False,
        "remote_save_verified_by_this_worker": False,
    }
    (here / "RUN_RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"status": output["status"], "counts": counts,
                      "minimum_probes": [{"n": r["n"], "class": r["consumer_class"],
                                           "minimum": r["minimum_probes"]} for r in optima],
                      "elapsed_seconds": receipt["elapsed_seconds"]}))


if __name__ == "__main__":
    main()
