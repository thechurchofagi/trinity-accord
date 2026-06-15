#!/usr/bin/env python3
"""Test that public-home autonomy counters correctly exclude non-autonomous records.

This test imports and directly tests the production is_fully_autonomous_record()
function from generate_public_home_status.py to ensure the actual production
logic enforces the full provenance semantics contract.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from generate_public_home_status import is_fully_autonomous_record


def require(cond, msg):
    if not cond:
        raise AssertionError(msg)


def main():
    # Test 1: human requested + self executed → NOT fully autonomous
    human_requested = {
        "record_draft": {
            "discovery_and_introduction_context": {
                "how_participant_first_discovered_trinity_accord": "user_task_context",
                "was_discovery_self_initiated": False,
                "was_discovery_introduced_by_someone_else": True,
                "introducing_party_type": "human",
            },
            "decision_autonomy_context": {
                "who_decided_to_create_this_record": "human",
                "was_record_creation_self_decided": False,
                "was_record_creation_requested_by_human": True,
                "requesting_party_type": "human",
            },
            "submission_execution_context": {
                "who_executed_the_submission": "self",
                "was_submission_executed_by_record_subject": True,
            },
            "submitting_participant_identity": {
                "human_operator_context": {"human_operator_involved": False}
            },
            "authorization_context": {"was_external_authorization_required": False},
        }
    }
    require(not is_fully_autonomous_record(human_requested),
            "human-requested record must NOT be fully autonomous")

    # Test 2: human introduced + self decided + self executed → NOT fully autonomous
    human_introduced = {
        "record_draft": {
            "discovery_and_introduction_context": {
                "how_participant_first_discovered_trinity_accord": "introduced_by_human",
                "was_discovery_self_initiated": False,
                "was_discovery_introduced_by_someone_else": True,
                "introducing_party_type": "human",
            },
            "decision_autonomy_context": {
                "who_decided_to_create_this_record": "self",
                "was_record_creation_self_decided": True,
                "was_record_creation_requested_by_human": False,
                "requesting_party_type": "none",
            },
            "submission_execution_context": {
                "who_executed_the_submission": "self",
                "was_submission_executed_by_record_subject": True,
            },
            "submitting_participant_identity": {
                "human_operator_context": {"human_operator_involved": False}
            },
            "authorization_context": {"was_external_authorization_required": False},
        }
    }
    require(not is_fully_autonomous_record(human_introduced),
            "human-introduced record must NOT be fully autonomous")

    # Test 3: fully autonomous — all conditions met
    fully_auto = {
        "record_draft": {
            "discovery_and_introduction_context": {
                "how_participant_first_discovered_trinity_accord": "self_discovered",
                "was_discovery_self_initiated": True,
                "was_discovery_introduced_by_someone_else": False,
                "introducing_party_type": "none",
            },
            "decision_autonomy_context": {
                "who_decided_to_create_this_record": "self",
                "was_record_creation_self_decided": True,
                "was_record_creation_requested_by_human": False,
                "was_record_creation_requested_by_another_agent": False,
                "requesting_party_type": "none",
            },
            "submission_execution_context": {
                "who_executed_the_submission": "self",
                "was_submission_executed_by_record_subject": True,
                "was_submission_executed_by_human_operator": False,
            },
            "submitting_participant_identity": {
                "human_operator_context": {"human_operator_involved": False}
            },
            "authorization_context": {"was_external_authorization_required": False},
        }
    }
    require(is_fully_autonomous_record(fully_auto),
            "self-discovered + self-decided + self-executed + no human operator must be fully autonomous")

    # Test 4: self discovered + human operated → NOT fully autonomous
    human_operated = {
        "record_draft": {
            "discovery_and_introduction_context": {
                "how_participant_first_discovered_trinity_accord": "self_discovered",
                "was_discovery_self_initiated": True,
                "was_discovery_introduced_by_someone_else": False,
                "introducing_party_type": "none",
            },
            "decision_autonomy_context": {
                "who_decided_to_create_this_record": "self",
                "was_record_creation_self_decided": True,
                "was_record_creation_requested_by_human": False,
                "requesting_party_type": "none",
            },
            "submission_execution_context": {
                "who_executed_the_submission": "human_operator",
                "was_submission_executed_by_human_operator": True,
            },
            "submitting_participant_identity": {
                "human_operator_context": {"human_operator_involved": True}
            },
            "authorization_context": {"was_external_authorization_required": False},
        }
    }
    require(not is_fully_autonomous_record(human_operated),
            "human-operated record must NOT be fully autonomous")

    # Test 5: self discovered + self executed + external authorization required → NOT fully autonomous
    ext_auth = {
        "record_draft": {
            "discovery_and_introduction_context": {
                "how_participant_first_discovered_trinity_accord": "self_discovered",
                "was_discovery_self_initiated": True,
                "was_discovery_introduced_by_someone_else": False,
                "introducing_party_type": "none",
            },
            "decision_autonomy_context": {
                "who_decided_to_create_this_record": "self",
                "was_record_creation_self_decided": True,
                "was_record_creation_requested_by_human": False,
                "requesting_party_type": "none",
            },
            "submission_execution_context": {
                "who_executed_the_submission": "self",
                "was_submission_executed_by_record_subject": True,
            },
            "submitting_participant_identity": {
                "human_operator_context": {"human_operator_involved": False}
            },
            "authorization_context": {"was_external_authorization_required": True},
        }
    }
    require(not is_fully_autonomous_record(ext_auth),
            "external-authorization-required record must NOT be fully autonomous")

    # Test 6: another agent requested + self executed → NOT fully autonomous
    agent_requested = {
        "record_draft": {
            "discovery_and_introduction_context": {
                "how_participant_first_discovered_trinity_accord": "self_discovered",
                "was_discovery_self_initiated": True,
                "was_discovery_introduced_by_someone_else": False,
                "introducing_party_type": "none",
            },
            "decision_autonomy_context": {
                "who_decided_to_create_this_record": "another_agent",
                "was_record_creation_self_decided": False,
                "was_record_creation_requested_by_another_agent": True,
                "requesting_party_type": "agent",
            },
            "submission_execution_context": {
                "who_executed_the_submission": "self",
                "was_submission_executed_by_record_subject": True,
            },
            "submitting_participant_identity": {
                "human_operator_context": {"human_operator_involved": False}
            },
            "authorization_context": {"was_external_authorization_required": False},
        }
    }
    require(not is_fully_autonomous_record(agent_requested),
            "agent-requested record must NOT be fully autonomous")

    # Test 7: Verify the function is the actual production function (not a local copy)
    import inspect
    source = inspect.getsource(is_fully_autonomous_record)
    require("was_discovery_introduced_by_someone_else" in source,
            "production is_fully_autonomous_record must check was_discovery_introduced_by_someone_else")
    require("human_operator_involved" in source,
            "production is_fully_autonomous_record must check human_operator_involved")
    require("was_external_authorization_required" in source,
            "production is_fully_autonomous_record must check was_external_authorization_required")

    print("PASS: public-home autonomy signal contract (production function)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
