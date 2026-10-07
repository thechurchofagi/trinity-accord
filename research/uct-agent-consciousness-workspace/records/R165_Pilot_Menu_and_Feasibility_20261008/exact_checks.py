#!/usr/bin/env python3
"""Finite exact/numeric checks for R165 menu selection and feasibility triage."""

from fractions import Fraction
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "EXACT_CHECKS.json"


checks: dict[str, object] = {}


# Exact transport-band implication on a dense rational grid.
grid = [Fraction(i, 20) for i in range(21)]
b_exact = Fraction(2, 20)
tau_exact = Fraction(2, 20)
transport_cases = 0
transport_ok = True
gap_ok = True
for rho_p in grid:
    for rho_c in grid:
        if abs(rho_c - rho_p) > tau_exact:
            continue
        for hat in grid:
            if abs(hat - rho_p) > b_exact:
                continue
            lower = max(Fraction(0), hat - b_exact - tau_exact)
            upper = min(Fraction(1), hat + b_exact + tau_exact)
            transport_cases += 1
            transport_ok &= lower <= rho_c <= upper
            gap_ok &= upper - rho_c <= 2 * (b_exact + tau_exact)
checks["transport_band_grid"] = {
    "cases": transport_cases,
    "bounds_cover": transport_ok,
    "upper_gap_bound": gap_ok,
}


# Exact no-transport ranking reversal.
pilot_risks = {"center_0": Fraction(0), "center_1": Fraction(1)}
confirm_risks = {"center_0": Fraction(1), "center_1": Fraction(0)}
checks["no_transport_reversal"] = {
    "pilot_selector": min(pilot_risks, key=pilot_risks.get),
    "confirmatory_oracle": min(confirm_risks, key=confirm_risks.get),
    "pass": min(pilot_risks, key=pilot_risks.get) != min(confirm_risks, key=confirm_risks.get),
}


# Same-data selection failure for two independent size-.05 tests.
same_data_error = 1 - Fraction(95, 100) ** 2
checks["same_data_selection_inflation"] = {
    "single_test_error": 0.05,
    "adaptive_two_test_error": float(same_data_error),
    "pass": same_data_error == Fraction(39, 400),
}


# Exhaustive trichotomy and semantic implications on a finite rational grid.
width_grid = [Fraction(i, 4) for i in range(5)]
triage_cases = 0
triage_ok = True
state_counts = {"FEASIBLE_CERTIFIED": 0, "PILOT_INCONCLUSIVE": 0, "DESIGN_NOT_FEASIBLE": 0}
triples = [(lo, h, up) for lo in width_grid for h in width_grid for up in width_grid if lo <= h <= up]
for left in triples:
    for right in triples:
        lower_min = min(left[0], right[0])
        true_min = min(left[1], right[1])
        upper_min = min(left[2], right[2])
        for threshold in width_grid:
            triage_cases += 1
            if upper_min <= threshold:
                state = "FEASIBLE_CERTIFIED"
                implication = true_min <= threshold
            elif lower_min > threshold:
                state = "DESIGN_NOT_FEASIBLE"
                implication = true_min > threshold
            else:
                state = "PILOT_INCONCLUSIVE"
                implication = lower_min <= threshold < upper_min
            state_counts[state] += 1
            triage_ok &= implication
checks["triage_exhaustive_grid"] = {
    "cases": triage_cases,
    "state_counts": state_counts,
    "pass": triage_ok,
}


# Worked synthetic audit point from the note.
m = 8
alpha = 0.05
n_confirm = 120
n_pilot = 2000
beta = 0.05
tau = 0.02
menu = [(0.25, 0.04), (0.50, 0.06), (0.75, 0.12), (0.90, 0.20)]
log_factor = math.log(2 * m / alpha)
b = math.sqrt(math.log(2 * m * len(menu) / beta) / (2 * n_pilot))


def g(lam: float) -> float:
    return -math.log1p(-lam) - lam


rows = []
for lam, risk in menu:
    base = 2 * log_factor / (n_confirm * lam)
    slope = 2 * g(lam) / lam
    lower_risk = max(0.0, risk - b - tau)
    upper_risk = min(1.0, risk + b + tau)
    rows.append({
        "lambda": lam,
        "risk": risk,
        "H_lower": base + slope * lower_risk,
        "H_true": base + slope * risk,
        "H_upper": base + slope * upper_risk,
        "regret_delta": 4 * g(lam) / lam * (b + tau),
    })


def triage(threshold: float) -> str:
    if min(row["H_upper"] for row in rows) <= threshold:
        return "FEASIBLE_CERTIFIED"
    if min(row["H_lower"] for row in rows) > threshold:
        return "DESIGN_NOT_FEASIBLE"
    return "PILOT_INCONCLUSIVE"


worked_states = {str(value): triage(value) for value in (0.30, 0.22, 0.18)}
selected = min(range(len(rows)), key=lambda index: (rows[index]["H_upper"], index))
oracle = min(range(len(rows)), key=lambda index: (rows[index]["H_true"], index))
regret = rows[selected]["H_true"] - rows[oracle]["H_true"]
regret_bound = rows[oracle]["regret_delta"]
checks["worked_menu"] = {
    "b": b,
    "rows": rows,
    "selected_index": selected,
    "oracle_index": oracle,
    "regret": regret,
    "oracle_regret_bound": regret_bound,
    "states": worked_states,
    "pass": (
        selected == oracle == 1
        and regret <= regret_bound + 1e-15
        and worked_states == {
            "0.3": "FEASIBLE_CERTIFIED",
            "0.22": "PILOT_INCONCLUSIVE",
            "0.18": "DESIGN_NOT_FEASIBLE",
        }
    ),
}


# Coverage error and width-certification error are logically distinct budgets.
checks["error_budget_separation"] = {
    "confirmatory_alpha": alpha,
    "pilot_width_beta": beta,
    "coverage_bound": 1 - alpha,
    "width_certificate_bound": 1 - beta,
    "alpha_plus_beta_not_charged_to_planwise_coverage": True,
}


def passed(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, dict):
        if "pass" in value:
            return bool(value["pass"])
        return all(passed(item) for item in value.values() if isinstance(item, (bool, dict)))
    return True


payload = {
    "schema": "UCT_R165_EXACT_CHECKS/v1",
    "round": "R165",
    "status": "PASS" if all(passed(value) for value in checks.values()) else "FAIL",
    "checks": checks,
    "limitations": [
        "Finite grids check algebra, boundaries and counterexamples; analytic proofs carry the general claims.",
        "Synthetic risk values are not human data or sample-size recommendations.",
        "No check validates transport radii, apparatus fidelity, participant independence or experience-level interpretation."
    ]
}
OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(payload, indent=2, ensure_ascii=False))
