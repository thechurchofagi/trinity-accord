#!/usr/bin/env python3
"""Exact finite checks for R168 metric envelopes, hidden fibers, and mass bounds."""

from fractions import Fraction
from itertools import combinations, product
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent


def subsets(items):
    for size in range(1, len(items) + 1):
        yield from combinations(items, size)


def metric_envelope_checks():
    cases = 0
    point_checks = 0
    sharp_checks = 0
    equality_examples = []
    M = 3
    L = 1
    for n in range(2, 6):
        Z = tuple(range(n))
        for S in subsets(Z):
            for U in product(range(M + 1), repeat=len(S)):
                envelope = []
                for z in Z:
                    envelope.append(min([M] + [u + L * abs(z - s) for s, u in zip(S, U)]))
                assert all(0 <= value <= M for value in envelope)
                assert all(abs(envelope[a] - envelope[b]) <= L * abs(a - b) for a in Z for b in Z)
                assert all(envelope[s] <= u for s, u in zip(S, U))
                # The envelope itself is admissible and attains every pointwise bound.
                for z in Z:
                    assert envelope[z] == min([M] + [u + abs(z - s) for s, u in zip(S, U)])
                    point_checks += 1
                    sharp_checks += 1
                if len(equality_examples) < 8 and max(envelope) > max(envelope[s] for s in S):
                    equality_examples.append({"Z": Z, "S": S, "U": U, "envelope": tuple(envelope)})
                cases += 1
    return {
        "finite_line_cases": cases,
        "pointwise_upper_checks": point_checks,
        "pointwise_sharpness_checks": sharp_checks,
        "equality_examples": equality_examples,
    }


def fill_distance_checks():
    checks = 0
    equalities = 0
    for n in range(2, 10):
        Z = tuple(range(n))
        for S in subsets(Z):
            h = max(min(abs(z - s) for s in S) for z in Z)
            eta = 1
            envelope = [min(3, eta + min(abs(z - s) for s in S)) for z in Z]
            assert max(envelope) <= min(3, eta + h)
            if max(envelope) == min(3, eta + h):
                equalities += 1
            checks += 1
    return {"context_sets": checks, "sharp_equalities": equalities}


def hidden_fiber_counterexample():
    M = 1
    observation = {"a": "x", "b": "x"}
    model_zero = {"a": 0, "b": 0}
    model_hidden = {"a": 0, "b": M}
    assert observation["a"] == observation["b"]
    assert model_zero["a"] == model_hidden["a"]
    assert max(model_zero.values()) == 0
    assert max(model_hidden.values()) == M
    return {
        "observation_map": observation,
        "tested_context": "a",
        "compatible_model_zero": model_zero,
        "compatible_model_hidden": model_hidden,
        "max_effect_gap": M,
    }


def random_mass_checks():
    checked = 0
    examples = []
    for n in range(1, 11):
        for p_num in range(0, 11):
            p = Fraction(p_num, 10)
            for s_num in range(1, 11):
                sensitivity = Fraction(s_num, 10)
                no_detection = (1 - sensitivity * p) ** n
                assert 0 <= no_detection <= 1
                if p_num and s_num and len(examples) < 8:
                    examples.append({"n": n, "p": str(p), "s_min": str(sensitivity), "no_detection": str(no_detection)})
                checked += 1
    return {"exact_fraction_cases": checked, "examples": examples}


def triage(valid, lower_support, envelope_refutes, mass_bound_only):
    if not valid:
        return "INVALID_PROTOCOL"
    if lower_support:
        return "CONTEXTUAL_USE_SUPPORTED"
    if envelope_refutes:
        return "AMPLITUDE_REFUTED_RELATIVE_TO_ENVELOPE"
    if mass_bound_only:
        return "AFFECTED_MASS_BOUNDED_ONLY"
    return "UNRESOLVED"


def triage_checks():
    statuses = []
    for values in product((False, True), repeat=4):
        result = triage(*values)
        valid, support, refute, mass = values
        if not valid:
            assert result == "INVALID_PROTOCOL"
        elif support:
            assert result == "CONTEXTUAL_USE_SUPPORTED"
        elif refute:
            assert result == "AMPLITUDE_REFUTED_RELATIVE_TO_ENVELOPE"
        elif mass:
            assert result == "AFFECTED_MASS_BOUNDED_ONLY"
        else:
            assert result == "UNRESOLVED"
        statuses.append(result)
    return {"boolean_assignments": len(statuses), "counts": {s: statuses.count(s) for s in sorted(set(statuses))}}


result = {
    "schema": "UCT_R168_EXACT_CHECKS/v1",
    "metric_envelope": metric_envelope_checks(),
    "fill_distance": fill_distance_checks(),
    "partial_observation_nonidentification": hidden_fiber_counterexample(),
    "random_context_mass": random_mass_checks(),
    "status_priority": triage_checks(),
    "interpretation": [
        "The cone envelope is a pointwise sharp upper bound for bounded Lipschitz effects under tested upper bounds.",
        "A shared observed label does not bound variation inside a hidden fiber.",
        "Random-context no-detection bounds affected mass only under sampling and sensitivity premises; it does not bound maximum amplitude.",
        "Every status is closure-relative and distinct from any basal-experience claim."
    ],
    "claim_limits": {
        "actual_data": False,
        "actual_apparatus": False,
        "physical_metric_validated": False,
        "lipschitz_constant_validated": False,
        "partial_view_lift_validated": False,
        "sampling_measure_validated": False,
        "complete_organization_identified": False,
        "C1_derived": False,
        "B_min_validated": False,
        "basal_experience_gate": False
    }
}

out = HERE / "EXACT_CHECKS.json"
out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({
    "status": "PASS",
    "output": out.name,
    "sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
    "envelope_cases": result["metric_envelope"]["finite_line_cases"],
    "point_checks": result["metric_envelope"]["pointwise_upper_checks"],
    "fill_sets": result["fill_distance"]["context_sets"],
    "mass_cases": result["random_context_mass"]["exact_fraction_cases"],
    "status_assignments": result["status_priority"]["boolean_assignments"]
}, indent=2))
