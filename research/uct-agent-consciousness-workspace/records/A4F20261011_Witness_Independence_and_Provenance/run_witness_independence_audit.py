#!/usr/bin/env python3
"""Exact finite audit of actuation-witness source identifiability.

This is an application-level observational-equivalence calculation.  It does
not model a complete physical device, an experience predicate, or a security
proof for arbitrary architectures.
"""

from __future__ import annotations

import json
from pathlib import Path


SOURCES = ("target", "hidden")


SCHEMES = {
    "level_change_only": {
        "target": {("changed",)},
        "hidden": {("changed",)},
    },
    "self_attested_source_label": {
        "target": {("changed", "target")},
        "hidden": {("changed", "hidden"), ("changed", "target")},
    },
    "dual_logs_shared_controller": {
        "target": {("changed", "target", "target")},
        "hidden": {
            ("changed", "hidden", "hidden"),
            ("changed", "target", "target"),
        },
    },
    "independent_transition_only": {
        "target": {("commit", 1)},
        "hidden": {("commit", 1)},
    },
    "source_specific_taps_complete": {
        "target": {("commit", 1, "tap_target", 1, "tap_hidden", 0)},
        "hidden": {("commit", 1, "tap_target", 0, "tap_hidden", 1)},
    },
    "nominal_taps_hidden_can_replay_target_vector": {
        "target": {("commit", 1, "tap_target", 1, "tap_hidden", 0)},
        "hidden": {
            ("commit", 1, "tap_target", 0, "tap_hidden", 1),
            ("commit", 1, "tap_target", 1, "tap_hidden", 0),
        },
    },
}


def normalize(vectors):
    return [list(v) for v in sorted(vectors, key=repr)]


def main() -> None:
    results = {}
    for name, reports in SCHEMES.items():
        overlap = reports["target"] & reports["hidden"]
        results[name] = {
            "possible_reports": {s: normalize(reports[s]) for s in SOURCES},
            "target_hidden_overlap": normalize(overlap),
            "source_identified": not overlap,
        }

    assert not results["level_change_only"]["source_identified"]
    assert not results["self_attested_source_label"]["source_identified"]
    assert not results["dual_logs_shared_controller"]["source_identified"]
    assert not results["independent_transition_only"]["source_identified"]
    assert results["source_specific_taps_complete"]["source_identified"]
    assert not results["nominal_taps_hidden_can_replay_target_vector"]["source_identified"]

    output = {
        "schema": "a4f-witness-independence-exact/1.0",
        "domain": {
            "actual_sources": list(SOURCES),
            "event_assumption": "A4E anti-current conditions already establish that one current commit occurred.",
            "report_semantics": "Each source maps to the set of complete witness vectors it can physically realize under the scheme's declared forge/replay permissions.",
        },
        "identifiability_rule": "The target source is identified in this two-source finite model iff its possible-report set is disjoint from the hidden source's possible-report set.",
        "schemes": results,
        "checks": {
            "schemes": len(results),
            "nonidentifying_schemes": sum(not x["source_identified"] for x in results.values()),
            "identifying_schemes": sum(x["source_identified"] for x in results.values()),
            "self_attestation_has_forged_overlap": bool(results["self_attested_source_label"]["target_hidden_overlap"]),
            "shared_root_redundancy_has_overlap": bool(results["dual_logs_shared_controller"]["target_hidden_overlap"]),
            "transition_only_proves_event_not_source": bool(results["independent_transition_only"]["target_hidden_overlap"]),
            "complete_unforgeable_source_taps_are_disjoint": results["source_specific_taps_complete"]["source_identified"],
            "replay_permission_restores_twin": bool(results["nominal_taps_hidden_can_replay_target_vector"]["target_hidden_overlap"]),
        },
        "bounded_consequence": "A current transition witness can establish event occurrence without identifying its source. Source identification requires whole-vector report disjointness relative to every admitted alternative writer; multiplying logs behind one controllable root does not supply this. In the declared two-writer model, complete source-specific taps identify the source only while neither writer can forge, replay, suppress, reset or re-time the other source's tap and the writer inventory is complete.",
        "limits": [
            "The disjointness calculation is elementary finite identifiability, not a new general theorem.",
            "The complete-tap row is conditional on the declared physical control/placement premises; the program does not validate hardware independence.",
            "An unlisted writer, shared power/reset/clock controller or downstream injection path can restore an observational twin.",
            "No complete UCT signature, C1 admission, RetBind, B_fam, H_way, conceptual self, report identity or consciousness verdict follows.",
        ],
    }

    out = Path(__file__).with_name("EXACT_RESULTS.json")
    out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output["checks"], sort_keys=True))


if __name__ == "__main__":
    main()
