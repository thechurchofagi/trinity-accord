#!/usr/bin/env python3
"""Test that public-home autonomy counters correctly exclude non-autonomous records."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent


def require(cond, msg):
    if not cond:
        raise AssertionError(msg)


def is_fully_autonomous_record(record: dict) -> bool:
    """Predicate: is this record fully autonomous?

    Must satisfy ALL conditions:
    - self_discovered (no introducer, no task context)
    - self_decided (no external request)
    - self_executed (agent ran build/preflight/submit)
    - NOT human_operator_involved
    - NOT introduced_by_someone_else
    - NOT external_authorization_required
    """
    draft = record.get("record_draft", record)

    discovery = draft.get("discovery_and_introduction_context", {})
    decision = draft.get("decision_autonomy_context", {})
    execution = draft.get("submission_execution_context", {})
    identity = draft.get("submitting_participant_identity", {})
    human_ctx = identity.get("human_operator_context", {})
    authorization = draft.get("authorization_context", {})

    return (
        discovery.get("how_participant_first_discovered_trinity_accord") == "self_discovered"
        and discovery.get("was_discovery_self_initiated") is True
        and discovery.get("was_discovery_introduced_by_someone_else") is not True
        and discovery.get("introducing_party_type") in (None, "", "none")
        and decision.get("who_decided_to_create_this_record") == "self"
        and decision.get("was_record_creation_self_decided") is True
        and decision.get("was_record_creation_requested_by_human") is not True
        and decision.get("was_record_creation_requested_by_another_agent") is not True
        and decision.get("requesting_party_type") in (None, "", "none")
        and execution.get("who_executed_the_submission") == "self"
        and execution.get("was_submission_executed_by_record_subject") is True
        and execution.get("was_submission_executed_by_human_operator") is not True
        and human_ctx.get("human_operator_involved") is not True
        and authorization.get("was_external_authorization_required") is not True
    )


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

    print("PASS: public-home autonomy signal contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
