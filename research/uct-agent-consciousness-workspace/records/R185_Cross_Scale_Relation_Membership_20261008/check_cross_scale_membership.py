#!/usr/bin/env python3
"""Exact finite checks for R185 cross-scale occurrence membership.

No phenomenal variable is represented.  The program checks only the declared
finite incidence/value models.
"""

from itertools import product
import json


TOKENS = ("L", "E", "W")


def shared_world(target: int):
    return {
        "occurrences": {"rho": target},
        "membership": {
            "rho": frozenset(TOKENS),
        },
        "local_occurrence": {"L": "rho", "E": "rho"},
        "synchronizer": False,
    }


def copied_world(target: int, synchronizer: bool):
    return {
        "occurrences": {"rho_L": target, "rho_E": target},
        "membership": {
            "rho_L": frozenset(("L", "W")),
            "rho_E": frozenset(("E", "W")),
        },
        "local_occurrence": {"L": "rho_L", "E": "rho_E"},
        "synchronizer": synchronizer,
    }


def view(world, token: str) -> int:
    return world["occurrences"][world["local_occurrence"][token]]


def whole_output(world) -> int:
    # The finite comparison fixes the effector-side target as the resumed one.
    return view(world, "E")


def report(world, positive_report: int) -> int:
    # Report is deliberately crossed and dynamically inert.
    return positive_report


def intervene(world, occurrence: str, value: int, clamp_sync: bool):
    result = {
        "occurrences": dict(world["occurrences"]),
        "membership": dict(world["membership"]),
        "local_occurrence": dict(world["local_occurrence"]),
        "synchronizer": world["synchronizer"],
    }
    result["occurrences"][occurrence] = value
    if result["synchronizer"] and not clamp_sync and occurrence == "rho_L":
        # A directed copied-register synchronizer is an additional whole relation.
        result["occurrences"]["rho_E"] = value
    return result


def profile(world, occurrence: str):
    members = world["membership"][occurrence]
    return tuple(int(t in members) for t in TOKENS)


def main():
    checks = []
    rows = []

    for target, positive_report, deliberate, biological in product((0, 1), repeat=4):
        s = shared_world(target)
        c0 = copied_world(target, synchronizer=False)
        c1 = copied_world(target, synchronizer=True)
        row = {
            "target": target,
            "report": positive_report,
            "deliberate_label": deliberate,
            "biological_label": biological,
            "shared_views": (view(s, "L"), view(s, "E")),
            "copied_views": (view(c0, "L"), view(c0, "E")),
            "shared_output": whole_output(s),
            "copied_output": whole_output(c0),
        }
        assert row["shared_views"] == row["copied_views"] == (target, target)
        assert row["shared_output"] == row["copied_output"] == target
        assert report(s, positive_report) == report(c0, positive_report)
        rows.append(row)

    checks.append("16 crossed baseline rows preserve local values, whole output and report")

    for target in (0, 1):
        s = shared_world(target)
        c = copied_world(target, synchronizer=False)
        assert set(s["occurrences"]) == {"rho"}
        assert set(c["occurrences"]) == {"rho_L", "rho_E"}
        assert profile(s, "rho") == (1, 1, 1)
        assert profile(c, "rho_L") == (1, 0, 1)
        assert profile(c, "rho_E") == (0, 1, 1)
        assert sum(profile(s, "rho")) == 3
        assert sum(sum(profile(c, r)) for r in c["occurrences"]) == 4
        assert len(s["occurrences"]) == 1
        assert len(c["occurrences"]) == 2

        flipped = 1 - target
        s2 = intervene(s, "rho", flipped, clamp_sync=True)
        assert (view(s2, "L"), view(s2, "E")) == (flipped, flipped)

        c2 = intervene(c, "rho_L", flipped, clamp_sync=True)
        assert (view(c2, "L"), view(c2, "E")) == (flipped, target)

        cs = copied_world(target, synchronizer=True)
        cs2 = intervene(cs, "rho_L", flipped, clamp_sync=False)
        assert (view(cs2, "L"), view(cs2, "E")) == (flipped, flipped)
        assert cs2["synchronizer"] is True

        cs3 = intervene(cs, "rho_L", flipped, clamp_sync=True)
        assert (view(cs3, "L"), view(cs3, "E")) == (flipped, target)

    checks.extend([
        "shared architecture has one occurrence class",
        "copied architecture has two occurrence classes despite equal values",
        "shared incidence profile is (1,1,1)",
        "copied profiles are (1,0,1) and (0,1,1)",
        "occurrence count differs from membership-incidence count",
        "shared occurrence intervention changes both local projections",
        "clamped copied occurrence intervention changes only one local projection",
        "an active synchronizer can propagate a copied change",
        "clamping the synchronizer exposes distinct copies",
        "synchronizer presence is an additional whole-organization fact",
        "deliberate/reflex labels do not select occurrence identity",
        "biological/prosthetic labels do not select occurrence identity",
        "report labels do not select occurrence identity",
        "matched baseline output does not identify membership profile",
    ])

    result = {
        "round": "R185",
        "baseline_configurations": len(rows),
        "target_values": 2,
        "assertion_groups": len(checks),
        "checks": checks,
        "status": "PASS",
        "scope": "finite occurrence/incidence model only; no phenomenal variable or actual human/AI instance",
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

