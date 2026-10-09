#!/usr/bin/env python3
"""Exact finite witness for R190.

The enumerator demonstrates independence inside the declared model only.  It does
not infer consciousness, ownership, agency, or phenomenal character.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path


MODES = {
    # q route, closure route, selected endpoint -> bearer path, external drive
    "enacted": ("overt", "overt", 1, 0),
    "remote_action": ("overt", "overt", 0, 0),
    "active_imagery": ("imagery", "imagery", 0, 0),
    "passive_impact": ("none", "none", 1, 1),
    "detached_observation": ("none", "none", 0, 0),
}


def make_row(mode: str, source: str, substrate: str, report: int,
             spillover: int, yoke: int) -> dict:
    directive_route, closure_route, impact_path, external_drive = MODES[mode]
    pc_overt = int(directive_route == "overt" and closure_route == "overt")
    pc_imagery = int(directive_route == "imagery" and closure_route == "imagery")
    bdcc_overt = impact_path
    # A baseline visible movement can be matched by an external yoke.  It does
    # not create either the policy route or the endpoint-to-bearer path.
    movement = int(pc_overt or external_drive or yoke)
    generic_body_effect = int(bdcc_overt or spillover)
    # The test result is derived from the declared actual path.  It is not used
    # to set that path, preserving actual-use/test-evidence direction.
    intervention_test_positive = int(impact_path == 1)
    return {
        "mode": mode,
        "source": source,
        "substrate": substrate,
        "report": report,
        "spillover": spillover,
        "yoke": yoke,
        "directive_route": directive_route,
        "closure_route": closure_route,
        "selected_impact_path": impact_path,
        "external_drive": external_drive,
        "pc_overt": pc_overt,
        "pc_imagery": pc_imagery,
        "bdcc_overt": bdcc_overt,
        "movement": movement,
        "generic_body_effect": generic_body_effect,
        "intervention_test_positive": intervention_test_positive,
    }


def main() -> None:
    rows = [
        make_row(*args)
        for args in itertools.product(
            MODES,
            ("deliberate", "reflex"),
            ("biological", "prosthetic"),
            (0, 1),
            (0, 1),
            (0, 1),
        )
    ]
    checks: dict[str, bool] = {}
    checks["row_count_160"] = len(rows) == 160
    profiles = {(r["pc_overt"], r["bdcc_overt"]) for r in rows}
    checks["all_four_pc_bdcc_profiles_realized"] = profiles == {
        (0, 0), (0, 1), (1, 0), (1, 1)
    }
    checks["enacted_is_11"] = all(
        (r["pc_overt"], r["bdcc_overt"]) == (1, 1)
        for r in rows if r["mode"] == "enacted"
    )
    checks["imagery_is_overt_00_and_imagery_pc"] = all(
        (r["pc_overt"], r["bdcc_overt"], r["pc_imagery"]) == (0, 0, 1)
        for r in rows if r["mode"] == "active_imagery"
    )
    checks["passive_impact_is_01"] = all(
        (r["pc_overt"], r["bdcc_overt"]) == (0, 1)
        for r in rows if r["mode"] == "passive_impact"
    )
    checks["observation_is_00"] = all(
        (r["pc_overt"], r["bdcc_overt"]) == (0, 0)
        for r in rows if r["mode"] == "detached_observation"
    )
    checks["imagery_spillover_not_selected_bdcc"] = any(
        r["mode"] == "active_imagery"
        and r["generic_body_effect"] == 1
        and r["bdcc_overt"] == 0
        for r in rows
    )
    checks["reflex_deliberate_twins_exist"] = all(
        any(
            s["mode"] == r["mode"]
            and s["source"] != r["source"]
            and all(s[k] == r[k] for k in (
                "substrate", "report", "spillover", "yoke",
                "pc_overt", "pc_imagery", "bdcc_overt", "movement",
                "generic_body_effect",
            ))
            for s in rows
        )
        for r in rows
    )
    checks["report_neither_necessary_nor_sufficient_for_11"] = (
        any(r["report"] == 0 and (r["pc_overt"], r["bdcc_overt"]) == (1, 1) for r in rows)
        and any(r["report"] == 1 and (r["pc_overt"], r["bdcc_overt"]) != (1, 1) for r in rows)
    )
    checks["substrate_label_does_not_determine_profile"] = all(
        {(r["pc_overt"], r["bdcc_overt"]) for r in rows if r["substrate"] == s}
        == profiles for s in ("biological", "prosthetic")
    )
    checks["matched_visible_movement_crosses_profiles"] = len({
        (r["pc_overt"], r["bdcc_overt"])
        for r in rows if r["movement"] == 1
    }) == 4
    checks["test_follows_path_not_reverse"] = all(
        r["intervention_test_positive"] == r["selected_impact_path"] for r in rows
    )
    checks["reflex_survives_enacted_filter"] = {
        r["source"] for r in rows
        if r["mode"] == "enacted" and r["pc_overt"] and r["bdcc_overt"]
    } == {"deliberate", "reflex"}

    assert all(checks.values()), checks
    payload = {
        "result_id": "R190-PCBC-RESULT-v0.1.0",
        "scope": "declared finite construction only",
        "row_count": len(rows),
        "profiles": sorted([list(p) for p in profiles]),
        "checks": checks,
        "checks_passed": sum(checks.values()),
        "rows_sha256": hashlib.sha256(
            json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "selected_witnesses": [
            next(r for r in rows if r["mode"] == mode and r["source"] == "deliberate"
                 and r["substrate"] == "biological" and r["report"] == 0
                 and r["spillover"] == 0 and r["yoke"] == 0)
            for mode in MODES
        ],
        "non_entailments": [
            "no consciousness verdict",
            "no felt agency or familiar-mineness identification",
            "no unique owner",
            "no universal independence claim about real systems",
            "no inference from diagnostic success to actual installed use",
        ],
    }
    out = Path(__file__).with_name("EXACT_RESULTS.json")
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({
        "rows": len(rows),
        "checks_passed": sum(checks.values()),
        "profiles": sorted([list(p) for p in profiles]),
        "rows_sha256": payload["rows_sha256"],
    }, indent=2))


if __name__ == "__main__":
    main()
