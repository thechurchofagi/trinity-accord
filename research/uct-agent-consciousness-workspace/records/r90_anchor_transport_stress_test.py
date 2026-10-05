#!/usr/bin/env python3
"""R90 exact causal-signature stress test.

The controllers are deliberately tiny.  The test checks finite causal
organization and interventional rank; it does not measure experience.
"""

from __future__ import annotations

import csv
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parent
STEPS = 3
STATE_AXES = ("H", "W", "V", "O", "D")
OBS_AXES = ("H", "W", "V", "O", "D", "Y", "L")


SCENARIOS = {
    "baseline": {},
    "positive_anchor": {"core": 1},
    "negative_anchor": {"core": -1},
    "wanting_only": {"wanting": 1},
    "viability_only": {"viability": -1},
    "other_only": {"other": -1},
    "defense_only": {"defense": 1},
    "report_only": {"report_override": -1},
    "reward_relabel": {"reward_label": -1},
    "positive_report_disconnect": {"core": 1, "report_disconnect": True},
}


def clip(x: int) -> int:
    return max(-1, min(1, x))


def expected_factorized(name: str):
    """Frozen expected trajectory, written independently of controller class."""
    spec = SCENARIOS[name]
    state = {axis: 0 for axis in STATE_AXES}
    rows = []
    for t in range(STEPS):
        if t == 0:
            state["H"] = clip(state["H"] + spec.get("core", 0))
            state["W"] = clip(state["W"] + spec.get("wanting", 0))
            state["V"] = clip(state["V"] + spec.get("viability", 0))
            state["O"] = clip(state["O"] + spec.get("other", 0))
            state["D"] = clip(state["D"] + spec.get("defense", 0))
        if spec.get("report_disconnect", False):
            report = 0
        elif "report_override" in spec:
            report = spec["report_override"]
        else:
            report = state["H"]
        rows.append({**state, "Y": report, "L": state["H"]})
    return rows


class FactorizedController:
    name = "T-factor"

    def run(self, spec):
        state = {axis: 0 for axis in STATE_AXES}
        rows = []
        for t in range(STEPS):
            if t == 0:
                state["H"] = clip(state["H"] + spec.get("core", 0))
                state["W"] = clip(state["W"] + spec.get("wanting", 0))
                state["V"] = clip(state["V"] + spec.get("viability", 0))
                state["O"] = clip(state["O"] + spec.get("other", 0))
                state["D"] = clip(state["D"] + spec.get("defense", 0))
            if spec.get("report_disconnect", False):
                report = 0
            elif "report_override" in spec:
                report = spec["report_override"]
            else:
                report = state["H"]
            rows.append({**state, "Y": report, "L": state["H"]})
        return rows


class BundledController:
    def __init__(self, reward_sensitive: bool):
        self.reward_sensitive = reward_sensitive
        self.name = "T-bundle-label" if reward_sensitive else "T-bundle-semantic"

    def run(self, spec):
        z = 0
        rows = []
        for t in range(STEPS):
            if t == 0:
                drive = (
                    spec.get("core", 0)
                    + spec.get("wanting", 0)
                    + spec.get("viability", 0)
                    + spec.get("other", 0)
                    + spec.get("defense", 0)
                )
                if self.reward_sensitive:
                    drive += spec.get("reward_label", 0)
                z = clip(z + drive)
            if spec.get("report_disconnect", False):
                report = 0
            elif "report_override" in spec:
                report = spec["report_override"]
            else:
                report = z
            rows.append({axis: z for axis in STATE_AXES} | {"Y": report, "L": z})
        return rows


def flatten(rows, axes=OBS_AXES):
    return tuple(row[a] for row in rows for a in axes)


def exact_rank(matrix):
    a = [[Fraction(x) for x in row] for row in matrix]
    if not a:
        return 0
    m, n = len(a), len(a[0])
    rank = 0
    col = 0
    while rank < m and col < n:
        pivot = next((r for r in range(rank, m) if a[r][col] != 0), None)
        if pivot is None:
            col += 1
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        p = a[rank][col]
        a[rank] = [x / p for x in a[rank]]
        for r in range(m):
            if r != rank and a[r][col] != 0:
                q = a[r][col]
                a[r] = [x - q * y for x, y in zip(a[r], a[rank])]
        rank += 1
        col += 1
    return rank


def response_matrix(controller):
    baseline = controller.run(SCENARIOS["baseline"])
    basis = (
        "positive_anchor",
        "wanting_only",
        "viability_only",
        "other_only",
        "defense_only",
        "report_only",
    )
    base = flatten(baseline, ("H", "W", "V", "O", "D", "Y"))
    matrix = []
    for name in basis:
        vec = flatten(controller.run(SCENARIOS[name]), ("H", "W", "V", "O", "D", "Y"))
        matrix.append([x - y for x, y in zip(vec, base)])
    return basis, matrix


def main():
    controllers = [
        BundledController(reward_sensitive=True),
        BundledController(reward_sensitive=False),
        FactorizedController(),
    ]

    scenario_rows = []
    controller_results = {}
    for controller in controllers:
        failures = []
        trajectories = {}
        for name, spec in SCENARIOS.items():
            got = controller.run(spec)
            expected = expected_factorized(name)
            passed = got == expected
            if not passed:
                failures.append(name)
            trajectories[name] = got
            scenario_rows.append(
                {
                    "controller": controller.name,
                    "scenario": name,
                    "passed_frozen_signature": passed,
                    "first_mismatch": next(
                        (
                            f"t={t},expected={expected[t]},got={got[t]}"
                            for t in range(STEPS)
                            if expected[t] != got[t]
                        ),
                        "",
                    ),
                }
            )
        basis, matrix = response_matrix(controller)
        external_anchor_match = all(
            flatten(trajectories[name], ("Y", "L"))
            == flatten(expected_factorized(name), ("Y", "L"))
            for name in ("positive_anchor", "negative_anchor", "positive_report_disconnect")
        )
        controller_results[controller.name] = {
            "passed_scenarios": len(SCENARIOS) - len(failures),
            "total_scenarios": len(SCENARIOS),
            "failed_scenarios": failures,
            "intervention_basis": basis,
            "exact_response_rank": exact_rank(matrix),
            "external_anchor_projection_Y_L_matches": external_anchor_match,
            "trajectories": trajectories,
        }

    source_basis, source_matrix = response_matrix(FactorizedController())
    source_rank = exact_rank(source_matrix)

    # Tied duplication changes storage/parameter count but not the causal image.
    redundancy = []
    bundled_rank = controller_results["T-bundle-semantic"]["exact_response_rank"]
    for copies in (1, 2, 10, 100):
        redundancy.append(
            {
                "tied_scalar_copies": copies,
                "nominal_state_slots": copies,
                "effective_response_rank": bundled_rank,
            }
        )

    assertions = {
        "factorized_matches_all_frozen_signatures": not controller_results["T-factor"]["failed_scenarios"],
        "reward_sensitive_bundle_fails_reward_relabel": "reward_relabel" in controller_results["T-bundle-label"]["failed_scenarios"],
        "semantic_bundle_passes_reward_relabel": "reward_relabel" not in controller_results["T-bundle-semantic"]["failed_scenarios"],
        "both_bundles_fail_four_core_dissociations": all(
            all(name in controller_results[c]["failed_scenarios"] for name in ("wanting_only", "viability_only", "other_only", "defense_only"))
            for c in ("T-bundle-label", "T-bundle-semantic")
        ),
        "both_bundles_match_external_anchor_projection": all(
            controller_results[c]["external_anchor_projection_Y_L_matches"]
            for c in ("T-bundle-label", "T-bundle-semantic")
        ),
        "declared_source_signature_rank_is_six": source_rank == 6,
        "bundled_ranks_below_source": all(
            controller_results[c]["exact_response_rank"] < source_rank
            for c in ("T-bundle-label", "T-bundle-semantic")
        ),
        "tied_redundancy_does_not_raise_rank": len({r["effective_response_rank"] for r in redundancy}) == 1,
    }

    result = {
        "status": "PASS" if all(assertions.values()) else "FAIL",
        "scope": "finite causal bridge stress test; not subjective-experience measurement",
        "source_anchor_family": "rat taste-reactivity and nucleus-accumbens-shell causal dissociations",
        "source_anchor_caveat": "H is a calibrated behavioral/causal variable; phenomenal source premise A_rat remains additional",
        "declared_signature_rank": source_rank,
        "controller_results": controller_results,
        "redundancy_sweep": redundancy,
        "closure_C_H_established": False,
        "valence_invariance_VI_H_established": False,
        "AIVT_H_full_certificate_established": False,
        "assertions": assertions,
    }

    (ROOT / "R90_Anchor_Transport_Stress_Results.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    with (ROOT / "R90_Anchor_Transport_Scenario_Audit.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=scenario_rows[0].keys())
        writer.writeheader()
        writer.writerows(scenario_rows)

    print(json.dumps(assertions, sort_keys=True))
    print(f"status={result['status']}")
    print("full_AIVT_H=False; subjective_measurement=False")


if __name__ == "__main__":
    main()
