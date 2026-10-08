#!/usr/bin/env python3
"""Exact finite checks for R171 universal-range certificate claims."""

from itertools import product
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent


def subsets(n, nonempty=False):
    start = 1 if nonempty else 0
    for mask in range(start, 1 << n):
        yield {i for i in range(n) if mask & (1 << i)}


def reachable(initial, transition):
    seen = set(initial)
    frontier = list(initial)
    while frontier:
        x = frontier.pop()
        y = transition[x]
        if y not in seen:
            seen.add(y)
            frontier.append(y)
    return seen


direct_checks = 0
proper_sample_witnesses = 0
for n in range(1, 8):
    universe = set(range(n))
    for target in subsets(n):
        for spec in subsets(n):
            for covered in subsets(n):
                if target <= spec and spec <= covered:
                    assert target <= covered
                    direct_checks += 1
        if target:
            for sample in subsets(n):
                if sample < target:
                    z = next(iter(target - sample))
                    world_closed = {x: True for x in target}
                    world_open = dict(world_closed)
                    world_open[z] = False
                    assert all(world_closed[x] == world_open[x] for x in sample)
                    assert all(world_closed.values()) and not all(world_open.values())
                    proper_sample_witnesses += 1


inductive_certificates = 0
inductive_reachability_checks = 0
for n in range(1, 4):
    transitions = list(product(range(n), repeat=n))
    for actual in transitions:
        for model in transitions:
            for initial in subsets(n, nonempty=True):
                for invariant in subsets(n):
                    for covered in subsets(n):
                        init_ok = initial <= invariant
                        closure_ok = all(model[x] in invariant for x in invariant)
                        refinement_ok = all(actual[x] == model[x] for x in invariant)
                        fiber_ok = invariant <= covered
                        if init_ok and closure_ok and refinement_ok and fiber_ok:
                            inductive_certificates += 1
                            reach = reachable(initial, actual)
                            assert reach <= covered
                            inductive_reachability_checks += len(reach)


witnesses = {
    "missing_initial_inclusion": {
        "actual": [0, 0], "model": [0, 0], "initial": [1], "invariant": [0], "covered": [0]
    },
    "missing_specification_closure": {
        "actual": [1, 1], "model": [1, 1], "initial": [0], "invariant": [0], "covered": [0]
    },
    "missing_actual_refinement": {
        "actual": [1, 1], "model": [0, 1], "initial": [0], "invariant": [0], "covered": [0]
    },
    "missing_fiber_coverage": {
        "actual": [1, 1], "model": [1, 1], "initial": [1], "invariant": [0, 1], "covered": [0]
    },
}


def obligation_bits(w):
    actual = tuple(w["actual"])
    model = tuple(w["model"])
    initial = set(w["initial"])
    invariant = set(w["invariant"])
    covered = set(w["covered"])
    return {
        "initial": initial <= invariant,
        "closure": all(model[x] in invariant for x in invariant),
        "refinement": all(actual[x] == model[x] for x in invariant),
        "fiber": invariant <= covered,
        "conclusion": reachable(initial, actual) <= covered,
    }


expected_missing = {
    "missing_initial_inclusion": "initial",
    "missing_specification_closure": "closure",
    "missing_actual_refinement": "refinement",
    "missing_fiber_coverage": "fiber",
}
witness_checks = {}
for name, w in witnesses.items():
    bits = obligation_bits(w)
    missing = expected_missing[name]
    assert bits[missing] is False and bits["conclusion"] is False
    assert all(bits[k] for k in ("initial", "closure", "refinement", "fiber") if k != missing)
    witness_checks[name] = bits


def status(valid, refuted, direct, inductive, specification, empirical):
    if not valid:
        return "INVALID_RANGE_PROTOCOL"
    if refuted:
        return "RANGE_CERTIFICATE_REFUTED"
    if direct:
        return "UNIVERSAL_RANGE_CERTIFIED_DIRECT"
    if inductive:
        return "UNIVERSAL_RANGE_CERTIFIED_REACHABLE"
    if specification:
        return "SPECIFICATION_ONLY"
    if empirical:
        return "EMPIRICAL_COVER_ONLY"
    return "UNRESOLVED"


status_counts = {}
status_assignments = 0
for bits in product((False, True), repeat=6):
    s = status(*bits)
    status_counts[s] = status_counts.get(s, 0) + 1
    status_assignments += 1
assert status_assignments == 64
assert set(status_counts) == {
    "INVALID_RANGE_PROTOCOL", "RANGE_CERTIFICATE_REFUTED",
    "UNIVERSAL_RANGE_CERTIFIED_DIRECT", "UNIVERSAL_RANGE_CERTIFIED_REACHABLE",
    "SPECIFICATION_ONLY", "EMPIRICAL_COVER_ONLY", "UNRESOLVED"
}


payload = {
    "schema": "UCT_R171_EXACT_CHECKS/v1",
    "status": "PASS",
    "direct_inclusion_checks": direct_checks,
    "proper_sample_nondetermination_witnesses": proper_sample_witnesses,
    "inductive_certificates": inductive_certificates,
    "inductive_reachability_state_checks": inductive_reachability_checks,
    "premise_independence_witnesses": witness_checks,
    "status_assignments": status_assignments,
    "status_counts": status_counts,
    "domain_family_audit": {
        "finite_hardware": ["actual realization", "initial/reset range", "all admissible inputs/modes", "inductive closure", "fiber/route cover"],
        "typed_program": ["operational semantics", "type preservation", "compiler/runtime/FFI refinement", "resource/environment scope", "fiber/route cover"],
        "sensorimotor": ["physical joint/actuator limits", "complete hybrid modes", "interval/reachability bounds", "model-error refinement", "fiber/route cover"],
        "biological_safety": ["admission population", "uncertainty/disturbance set", "controlled invariance", "monitor/actuator/failsafe", "fiber/route cover"]
    },
    "claim_limits": {
        "actual_hardware_range_validated": False,
        "actual_program_refinement_validated": False,
        "actual_sensorimotor_range_validated": False,
        "actual_biological_envelope_validated": False,
        "complete_organization_identified": False,
        "C1_derived": False,
        "B_min_validated": False,
        "basal_experience_gate": False
    },
    "failures": []
}
(HERE / "EXACT_CHECKS.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(payload, indent=2, ensure_ascii=False))
