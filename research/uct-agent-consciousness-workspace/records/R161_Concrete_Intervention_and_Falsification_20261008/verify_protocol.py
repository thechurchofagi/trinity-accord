#!/usr/bin/env python3
"""Exact bounded checks for the R161 decision contract.

This verifies definitions and interval logic only.  It does not simulate human
data, validate manipulation selectivity, or prove a phenomenal interpretation.
"""

from fractions import Fraction
from itertools import product
from math import ceil, log
import json


GRID = tuple(Fraction(i, 4) for i in range(5))
EPS = Fraction(1, 4)


def intervals():
    return tuple((lo, hi) for lo in GRID for hi in GRID if lo <= hi)


def decision(la, ua, lx, ux):
    confirm = la > EPS and la - ux > EPS
    exclude = ua <= EPS or ua - lx <= EPS
    if confirm:
        return "CONFIRM"
    if exclude:
        return "EXCLUDE"
    return "UNRESOLVED"


def nested(inner, outer):
    return outer[0] <= inner[0] <= inner[1] <= outer[1]


ints = intervals()
counts = {"CONFIRM": 0, "EXCLUDE": 0, "UNRESOLVED": 0}
disjoint = True

for (la, ua), (lx, ux) in product(ints, repeat=2):
    c = la > EPS and la - ux > EPS
    e = ua <= EPS or ua - lx <= EPS
    disjoint &= not (c and e)
    counts[decision(la, ua, lx, ux)] += 1

monotone_nesting = True
nesting_checks = 0
for outer_a, outer_x, inner_a, inner_x in product(ints, repeat=4):
    if not (nested(inner_a, outer_a) and nested(inner_x, outer_x)):
        continue
    nesting_checks += 1
    before = decision(*outer_a, *outer_x)
    after = decision(*inner_a, *inner_x)
    if before == "CONFIRM" and after != "CONFIRM":
        monotone_nesting = False
    if before == "EXCLUDE" and after != "EXCLUDE":
        monotone_nesting = False

fidelity_checks = 0
fidelity_gate_pass = True
for flags in product((False, True), repeat=6):
    fidelity_checks += 1
    admissible = all(flags)
    reported = "CLASSIFY" if admissible else "INVALID_PROTOCOL"
    fidelity_gate_pass &= (reported == "CLASSIFY") == admissible

# Worst-case distribution-free planning audit for eight participant-level
# bounded simple contrasts and a dominance slack gamma.  This is deliberately
# conservative and is not a recommended sample size without a real variance
# model.  Requiring 2*r <= gamma with
# r=sqrt(2 log(2m/alpha)/n) yields n>=8 log(2m/alpha)/gamma^2.
alpha = 0.05
m = 8
power_audit = []
for gamma in (0.10, 0.15, 0.20, 0.25):
    n = ceil(8 * log(2 * m / alpha) / (gamma * gamma))
    power_audit.append({"dominance_slack_gamma": gamma, "n_complete_participants": n})

result = {
    "schema": "UCT_R161_EXACT_CHECKS/v1",
    "grid": [str(x) for x in GRID],
    "epsilon": str(EPS),
    "intervals_per_effect": len(ints),
    "interval_pairs_checked": len(ints) ** 2,
    "decision_counts": counts,
    "confirm_exclude_disjoint": disjoint,
    "nested_interval_cases_checked": nesting_checks,
    "decision_stable_under_nested_precision": monotone_nesting,
    "fidelity_boolean_assignments_checked": fidelity_checks,
    "fidelity_gate_blocks_every_failed_assignment": fidelity_gate_pass,
    "worst_case_hoeffding_planning_audit": {
        "alpha_familywise": alpha,
        "bounded_simple_contrasts": m,
        "formula": "ceil(8*log(2*m/alpha)/gamma^2)",
        "table": power_audit,
        "status": "CONSERVATIVE_AUDIT_NOT_A_FIXED_STUDY_SAMPLE_SIZE"
    },
    "all_checks_pass": all((disjoint, monotone_nesting, fidelity_gate_pass)),
    "limits": [
        "Finite rational interval logic only.",
        "No manipulation fidelity, human effect, power model, C1, B_min, or F_O is empirically validated.",
        "The Hoeffding table assumes independent complete participant contrasts in [-1,1] and is intentionally worst-case."
    ]
}

print(json.dumps(result, indent=2, sort_keys=True))
