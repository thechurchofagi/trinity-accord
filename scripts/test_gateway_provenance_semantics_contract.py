#!/usr/bin/env python3
"""Test Gateway provenance semantic validation contract."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "apps/record_chain_intake_gateway"))

from gateway.validation import validate_provenance_semantics


def require(cond, msg):
    if not cond:
        raise AssertionError(msg)


def assert_code(draft, code):
    diagnostics = validate_provenance_semantics(draft)
    codes = {d.code for d in diagnostics}
    require(code in codes, f"expected {code}, got {sorted(codes)}")


def main():
    # Test 1: Discovery conflict — self_initiated + introduced_by_human
    assert_code({
        "discovery_and_introduction_context": {
            "how_participant_first_discovered_trinity_accord": "introduced_by_human",
            "was_discovery_self_initiated": True,
            "was_discovery_introduced_by_someone_else": True,
            "introducing_party_type": "human",
        }
    }, "PROVENANCE_DISCOVERY_CONTEXT_CONFLICT")

    # Test 2: Decision conflict — self_decided + requested_by_human
    assert_code({
        "decision_autonomy_context": {
            "who_decided_to_create_this_record": "self",
            "was_record_creation_self_decided": True,
            "was_record_creation_requested_by_human": True,
            "was_record_creation_requested_by_another_agent": False,
            "requesting_party_type": "human",
        }
    }, "PROVENANCE_DECISION_CONTEXT_CONFLICT")

    # Test 3: Execution conflict — executor self + human_operator_involved true
    assert_code({
        "submitting_participant_identity": {
            "human_operator_context": {
                "human_operator_involved": True,
            }
        },
        "submission_execution_context": {
            "who_executed_the_submission": "self",
            "was_submission_executed_by_record_subject": True,
            "was_submission_executed_by_human_operator": False,
            "was_submission_executed_by_another_agent": False,
        },
    }, "PROVENANCE_EXECUTION_CONTEXT_CONFLICT")

    # Test 4: Execution conflict — executor human_operator + human_operator_involved false
    assert_code({
        "submitting_participant_identity": {
            "human_operator_context": {
                "human_operator_involved": False,
            }
        },
        "submission_execution_context": {
            "who_executed_the_submission": "human_operator",
            "was_submission_executed_by_record_subject": False,
            "was_submission_executed_by_human_operator": False,
            "was_submission_executed_by_another_agent": False,
        },
    }, "PROVENANCE_EXECUTION_CONTEXT_CONFLICT")

    print("PASS: gateway provenance semantics contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
