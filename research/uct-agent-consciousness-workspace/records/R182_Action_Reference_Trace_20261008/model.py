#!/usr/bin/env python3
"""Exact finite checks for the R182 action-reference-trace construction.

The program checks organizational consequences only.  It contains no variable
for phenomenal trying, consciousness, voluntariness, ownership or total
experience.
"""

from itertools import product
import json
from pathlib import Path


def episode(architecture, route, blocked, control_label, tissue, report):
    # q and both baseline calibration reads are matched in every system.
    q = 1
    r_a = r_b = 0
    command_a = q ^ r_a
    command_b = q ^ r_b

    # The target follows the installed consumer path, not report or label.
    overt_directive = route == "overt"
    imagery_directive = route == "imagery"
    closure = True
    mismatch_used = bool(blocked and overt_directive)
    movement = 0 if blocked else command_a

    # ART is a physical identity/branching fact: one carrier supplies both
    # contexts.  Equal values in the copied case do not make one carrier.
    art = architecture == "shared"
    pc_overt = overt_directive and closure
    pc_imagery = imagery_directive and closure
    eac_overt = pc_overt and mismatch_used and art

    return {
        "architecture": architecture,
        "route": route,
        "blocked": blocked,
        "control_label": control_label,
        "tissue": tissue,
        "report": report,
        "q": q,
        "command_a": command_a,
        "command_b": command_b,
        "movement": movement,
        "overt_directive": overt_directive,
        "imagery_directive": imagery_directive,
        "closure": closure,
        "mismatch_used": mismatch_used,
        "art": art,
        "pc_overt": pc_overt,
        "pc_imagery": pc_imagery,
        "eac_overt": eac_overt,
    }


def intervention(architecture):
    # Predeclared calibration intervention at the physical A-side access point.
    # In the shared installation it changes the same carrier read by A and B.
    # In the copied installation it changes R_a only.
    q = 1
    r_a = 1
    r_b = 1 if architecture == "shared" else 0
    return {"command_a": q ^ r_a, "command_b": q ^ r_b}


rows = [
    episode(*args)
    for args in product(
        ("shared", "copied"),
        ("overt", "imagery"),
        (False, True),
        ("deliberate", "reflex"),
        ("biological", "prosthetic"),
        (False, True),
    )
]

checks = {}

baseline_signatures = {
    architecture: {
        (r["command_a"], r["command_b"])
        for r in rows
        if r["architecture"] == architecture
    }
    for architecture in ("shared", "copied")
}
checks["matched_baseline_commands"] = (
    baseline_signatures["shared"] == baseline_signatures["copied"] == {(1, 1)}
)

checks["heldout_cross_context_transfer"] = (
    intervention("shared") == {"command_a": 0, "command_b": 0}
    and intervention("copied") == {"command_a": 0, "command_b": 1}
)

checks["equal_values_do_not_identify_carrier"] = all(
    r["command_a"] == 1 and r["command_b"] == 1
    for r in rows
)

blocked_overt = [r for r in rows if r["blocked"] and r["route"] == "overt"]
checks["blocked_without_movement"] = all(
    r["movement"] == 0 and r["pc_overt"] and r["mismatch_used"]
    for r in blocked_overt
)

checks["local_dce_matched_across_architectures"] = all(
    {
        (
            r["overt_directive"],
            r["closure"],
            r["mismatch_used"],
            r["movement"],
        )
        for r in blocked_overt
        if r["architecture"] == architecture
    }
    == {(True, True, True, 0)}
    for architecture in ("shared", "copied")
)

checks["wider_embedding_changes_eac"] = (
    {r["eac_overt"] for r in blocked_overt if r["architecture"] == "shared"}
    == {True}
    and {r["eac_overt"] for r in blocked_overt if r["architecture"] == "copied"}
    == {False}
)

checks["tissue_not_determinative"] = all(
    {
        r["eac_overt"]
        for r in blocked_overt
        if r["architecture"] == architecture and r["tissue"] == tissue
    }
    == ({True} if architecture == "shared" else {False})
    for architecture, tissue in product(
        ("shared", "copied"), ("biological", "prosthetic")
    )
)

checks["control_label_not_determinative"] = all(
    {
        r["eac_overt"]
        for r in blocked_overt
        if r["architecture"] == architecture
        and r["control_label"] == control_label
    }
    == ({True} if architecture == "shared" else {False})
    for architecture, control_label in product(
        ("shared", "copied"), ("deliberate", "reflex")
    )
)

checks["report_not_determinative"] = all(
    {
        r["eac_overt"]
        for r in blocked_overt
        if r["architecture"] == architecture and r["report"] == report
    }
    == ({True} if architecture == "shared" else {False})
    for architecture, report in product(("shared", "copied"), (False, True))
)

checks["imagery_target_separated"] = all(
    (not r["pc_overt"])
    and r["pc_imagery"]
    and (not r["mismatch_used"])
    and (not r["eac_overt"])
    for r in rows
    if r["route"] == "imagery"
)

checks["architecture_not_read_from_report"] = all(
    any(
        other["architecture"] != r["architecture"]
        and other["report"] == r["report"]
        and other["route"] == r["route"]
        and other["blocked"] == r["blocked"]
        and other["movement"] == r["movement"]
        for other in rows
    )
    for r in rows
)

checks["reflex_twin_blocks_felt_trying_inference"] = all(
    {
        (
            r["overt_directive"],
            r["closure"],
            r["mismatch_used"],
            r["art"],
            r["eac_overt"],
        )
        for r in blocked_overt
        if r["architecture"] == architecture
        and r["control_label"] == control_label
    }
    == (
        {(True, True, True, True, True)}
        if architecture == "shared"
        else {(True, True, True, False, False)}
    )
    for architecture, control_label in product(
        ("shared", "copied"), ("deliberate", "reflex")
    )
)

assert len(rows) == 64
assert all(checks.values()), {k: v for k, v in checks.items() if not v}

result = {
    "round": "R182",
    "configurations": len(rows),
    "checks": len(checks),
    "passed": sum(checks.values()),
    "intervention": {
        "shared": intervention("shared"),
        "copied": intervention("copied"),
    },
    "claims_supported": [
        "baseline local D/C/E, movement and report can match while physical action-reference architecture differs",
        "a predeclared calibration perturbation has a cross-context consequence only for the shared trace",
        "biological/prosthetic and deliberate/reflex labels do not determine the organizational coordinate",
        "the reflex twin prevents identifying the coordinate with phenomenal trying",
    ],
    "status": "ORGANIZATIONAL_COORDINATE_WITH_OPEN_PHENOMENAL_BRIDGE",
    "checks_detail": checks,
}

out = Path(__file__).with_name("MODEL_RESULTS.json")
out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: result[k] for k in ("configurations", "checks", "passed", "status")}))
