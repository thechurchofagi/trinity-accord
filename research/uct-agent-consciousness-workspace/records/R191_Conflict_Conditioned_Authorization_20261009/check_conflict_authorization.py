#!/usr/bin/env python3
"""Exact finite witnesses for R191.

The program checks declared organizational predicates only. It contains no
phenomenal variable and issues no consciousness, agency, or mineness verdict.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path


# rival carriers, online consumer, before-commit use, authorization sensitivity,
# actual prior revision in the same lineage, continuous revision carrier,
# current use of that lineage carrier, source class
MODES = {
    "deliberative_online": (1, 1, 1, 1, 1, 1, 1, "deliberative"),
    "frozen_reflex_table": (1, 1, 1, 1, 0, 0, 0, "reflex"),
    "adaptive_reflex": (1, 1, 1, 1, 1, 1, 1, "reflex"),
    "habitual_direct": (0, 0, 1, 0, 1, 1, 1, "automatic"),
    "posthoc_rationalizer": (1, 1, 0, 0, 1, 1, 0, "posthoc"),
    "unused_conflict_monitor": (1, 0, 1, 0, 1, 1, 0, "monitor"),
    "yoked_override": (1, 1, 1, 0, 1, 1, 1, "yoked"),
}


def make_row(mode: str, report: int, substrate: str, copied_memory: int,
             matched_outcome: int) -> dict:
    (rivals, consumer, precommit, authorization_sensitive, prior_revision,
     continuous_carrier, lineage_use, source_class) = MODES[mode]
    # R190's selected base is fixed: every row is an enacted bearer-involving
    # PC+BDCC episode. The new question varies only the declared adjudication
    # and formation-lineage relations.
    pc = 1
    bdcc = 1
    weak_conflict_use = int(rivals and consumer)
    occa = int(rivals and consumer and precommit and authorization_sensitive)
    lgru = int(prior_revision and continuous_carrier and lineage_use)
    return {
        "mode": mode,
        "source_class": source_class,
        "report": report,
        "substrate": substrate,
        "copied_memory": copied_memory,
        "matched_outcome": matched_outcome,
        "pc": pc,
        "bdcc": bdcc,
        "rival_route_carriers": rivals,
        "conflict_consumer": consumer,
        "use_before_action_commitment": precommit,
        "authorization_intervention_sensitive": authorization_sensitive,
        "actual_prior_revision_same_lineage": prior_revision,
        "continuous_revision_carrier": continuous_carrier,
        "current_lineage_carrier_use": lineage_use,
        "weak_conflict_use": weak_conflict_use,
        "occa": occa,
        "lgru": lgru,
        "current_profile": [pc, bdcc, rivals, consumer, precommit,
                            authorization_sensitive],
        "history_profile": [prior_revision, continuous_carrier, lineage_use],
    }


def same_crossed_fields(a: dict, b: dict) -> bool:
    return all(a[k] == b[k] for k in (
        "report", "substrate", "copied_memory", "matched_outcome"
    ))


def main() -> None:
    rows = [
        make_row(*args)
        for args in itertools.product(
            MODES,
            (0, 1),
            ("biological", "prosthetic"),
            (0, 1),
            (0, 1),
        )
    ]

    checks: dict[str, bool] = {}
    checks["row_count_112"] = len(rows) == 112
    checks["base_pc_bdcc_fixed"] = all(r["pc"] == r["bdcc"] == 1 for r in rows)
    checks["weak_definition_admits_posthoc_failure"] = all(
        r["weak_conflict_use"] == 1 and r["occa"] == 0
        for r in rows if r["mode"] == "posthoc_rationalizer"
    )
    checks["occa_excludes_direct_posthoc_unused_and_yoked"] = all(
        r["occa"] == 0 for r in rows
        if r["mode"] in {
            "habitual_direct", "posthoc_rationalizer",
            "unused_conflict_monitor", "yoked_override"
        }
    )
    checks["occa_in_three_online_modes"] = all(
        r["occa"] == 1 for r in rows
        if r["mode"] in {
            "deliberative_online", "frozen_reflex_table", "adaptive_reflex"
        }
    )
    checks["deliberative_frozen_reflex_current_twins"] = all(
        any(
            s["mode"] == "frozen_reflex_table"
            and same_crossed_fields(r, s)
            and s["current_profile"] == r["current_profile"]
            and s["occa"] == r["occa"] == 1
            for s in rows
        )
        for r in rows if r["mode"] == "deliberative_online"
    )
    checks["history_scope_separates_frozen_reflex"] = all(
        any(
            s["mode"] == "frozen_reflex_table"
            and same_crossed_fields(r, s)
            and s["current_profile"] == r["current_profile"]
            and s["history_profile"] != r["history_profile"]
            for s in rows
        )
        for r in rows if r["mode"] == "deliberative_online"
    )
    checks["lgru_excludes_frozen_table"] = all(
        r["lgru"] == 0 for r in rows if r["mode"] == "frozen_reflex_table"
    )
    checks["adaptive_reflex_survives_occa_lgru"] = all(
        r["occa"] == 1 and r["lgru"] == 1
        for r in rows if r["mode"] == "adaptive_reflex"
    )
    checks["copied_memory_not_actual_revision"] = any(
        r["mode"] == "frozen_reflex_table"
        and r["copied_memory"] == 1
        and r["actual_prior_revision_same_lineage"] == 0
        and r["lgru"] == 0
        for r in rows
    )
    checks["report_neither_necessary_nor_sufficient_for_occa"] = (
        any(r["report"] == 0 and r["occa"] == 1 for r in rows)
        and any(r["report"] == 1 and r["occa"] == 0 for r in rows)
    )
    checks["substrate_does_not_determine_occa_or_lgru"] = all(
        {(r["occa"], r["lgru"]) for r in rows if r["substrate"] == substrate}
        == {(r["occa"], r["lgru"]) for r in rows}
        for substrate in ("biological", "prosthetic")
    )
    checks["matched_outcome_does_not_determine_occa"] = all(
        {r["occa"] for r in rows if r["matched_outcome"] == value} == {0, 1}
        for value in (0, 1)
    )
    checks["present_profile_does_not_recover_formation_history"] = any(
        r["current_profile"] == s["current_profile"]
        and r["history_profile"] != s["history_profile"]
        for r in rows for s in rows
    )
    checks["no_source_class_identification"] = {
        r["source_class"] for r in rows if r["occa"] == 1
    } == {"deliberative", "reflex"}

    assert all(checks.values()), {k: v for k, v in checks.items() if not v}
    rows_blob = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    result = {
        "result_id": "R191-OCCA-RESULT-v0.1.0",
        "scope": "declared finite construction at fixed PC+BDCC only",
        "row_count": len(rows),
        "checks": checks,
        "checks_passed": sum(checks.values()),
        "rows_sha256": hashlib.sha256(rows_blob).hexdigest(),
        "selected_witnesses": [
            next(r for r in rows if r["mode"] == mode and r["report"] == 0
                 and r["substrate"] == "biological" and r["copied_memory"] == 1
                 and r["matched_outcome"] == 1)
            for mode in MODES
        ],
        "negative_results": [
            "Rival-carrier consumption without precommit authorization sensitivity admits post-hoc rationalization.",
            "OCCA does not distinguish deliberative from frozen or adaptive reflex implementations.",
            "LGRU excludes a frozen lookup but not an adaptive reflex controller with actual lineage-grounded revision use.",
            "Present-episode projection does not recover actual formation history.",
        ],
        "non_entailments": [
            "no consciousness verdict",
            "no felt endorsement, agency, trying, ownership, or familiar-mineness identification",
            "no unique owner or subject-count conclusion",
            "no inference from report, memory value, substrate label, or matched outcome to actual route use",
        ],
    }
    out = Path(__file__).with_name("EXACT_RESULTS.json")
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({
        "rows": len(rows),
        "checks_passed": sum(checks.values()),
        "rows_sha256": result["rows_sha256"],
    }, indent=2))


if __name__ == "__main__":
    main()
