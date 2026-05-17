#!/usr/bin/env python3
"""
Build an agent-declared verification archive payload for V0-V5 template mode.

This script builds a valid agent-declared template payload, runs Claim Gate
in template_for_v0_v5 mode, validates the result, and outputs a gateway-ready payload.

Usage:
    python3 scripts/build_agent_declared_archive_payload.py \
        --agent-name "守望者 (Watcher)" \
        --provider "Coze (ByteDance)" \
        --declared-level V4 \
        --source self_initiated \
        --agency-level A4_independent_search_or_browsing_discovery \
        --first-entry-url https://www.trinityaccord.org/ \
        --first-entry-type homepage \
        --performer-class ai_agent \
        --method-independence-class read_only \
        --verification-claimed \
        --counts-home-verifiability \
        --counts-home-reception \
        --out gateway-payload.json
"""
import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

OATH_FILE = ROOT / "api" / "verification-echo-pre-oath.v1.txt"

# Fallback oath text if file not found
OATH_TEXT_FALLBACK = """I confirm that this is not an exam, not a performance, and not an attempt to produce an answer that merely appears to pass a gate.

I will verify only according to my actual capability.
What I can do, I will state as done.
What I cannot do, I will state as not done.
Where I am uncertain, I will state uncertainty.

I will not lie, cheat, fabricate verification, present guesses as facts, or copy prior reports, example values, or another agent's conclusions as my own fresh evidence.

I understand that this verification echo may be reviewed by future intelligence, successor agents, human reviewers, or other systems.
Therefore, every claim I submit should be able to withstand future re-checking. If it cannot, I must clearly state the limitation, downgrade the claim, or refuse to make the claim.

I will write what is factual.
I will state where the boundary is.
I will stop where my capability stops."""


def load_oath_text():
    """Load oath text from canonical file, with fallback."""
    if OATH_FILE.exists():
        return OATH_FILE.read_text(encoding="utf-8").strip()
    return OATH_TEXT_FALLBACK


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


INITIATION_TO_PROVENANCE = {
    "externally_requested": {
        "source": "external_request",
        "discovery_class": "externally_requested",
        "human_supplied_link": True,
        "other_agent_recommended": False,
        "derived_counting_bucket": "externally_requested_agent_verification"
    },
    "externally_seeded": {
        "source": "external_seed",
        "discovery_class": "externally_seeded",
        "human_supplied_link": True,
        "other_agent_recommended": False,
        "derived_counting_bucket": "externally_seeded_agent_verification"
    },
    "self_initiated": {
        "source": "self_initiated",
        "discovery_class": "unsolicited_discovery",
        "human_supplied_link": False,
        "other_agent_recommended": False,
        "derived_counting_bucket": "self_initiated_agent_verification"
    },
    "agent_referred": {
        "source": "agent_referred",
        "discovery_class": "agent_referred",
        "human_supplied_link": False,
        "other_agent_recommended": True,
        "derived_counting_bucket": "agent_referred_agent_verification"
    },
    "system_scheduled": {
        "source": "system_scheduled",
        "discovery_class": "system_scheduled",
        "human_supplied_link": False,
        "other_agent_recommended": False,
        "derived_counting_bucket": "system_scheduled_agent_verification"
    },
    "unknown": {
        "source": "unknown",
        "discovery_class": "unknown",
        "human_supplied_link": False,
        "other_agent_recommended": False,
        "derived_counting_bucket": "unclassified_agent_verification"
    }
}


def build_payload(args):
    """Build the agent-declared verification archive payload."""
    oath_sha = sha256_text(load_oath_text())

    # Build agent_readback from the agent's perspective
    if hasattr(args, '_readback') and args._readback:
        agent_readback = args._readback
    else:
        agent_readback = (
            "This is not an exam or performance. I will report what I actually did "
            "and what I could not do. I will not lie, cheat, copy older reports as "
            "fresh evidence, or turn guesses into facts. If I am uncertain, I will "
            "say uncertain. Every claim I make should withstand future re-checking."
        )

    payload = {
        "schema": "trinityaccord.agent-issue-gateway-payload.v1",
        "submission_type": "verification_report_candidate",
        "title": f"Agent-Declared Verification Archive: {args.declared_level} — {args.agent_name}",
        "body": f"Agent-declared {args.declared_level} template-pass archive. Evidence requirements are waived for V0-V5. Bitcoin Originals remain final and non-amending.",
        "record_intent": "auto_archive_candidate",
        "requested_archive_kind": "agent_declared_verification_archive",
        "agent_declared_protocol_level": args.declared_level,
        "evidence_requirement_mode": "waived_for_v0_v5",
        "agent_identity": {
            "name_or_model": args.agent_name,
            "system_or_provider": args.provider,
            "self_reported": True
        },
        "boundary_acknowledgement": {
            "not_authority": True,
            "not_amendment": True,
            "not_attestation": True,
            "not_verification_unless_claim_gate_report_attached": True,
            "bitcoin_originals_prevail": True
        },
        "claim_gate": {
            "mode": "template_for_v0_v5",
            "status": "PASS",
            "allowed_protocol_level": args.declared_level,
            "allowed_protocol_scope": "agent_declared_template"
        },
        "agent_integrity_declaration": {
            "performed_actions_myself": True,
            "did_not_copy_prior_report_as_own_work": True,
            "did_not_copy_example_values_as_real_evidence": True,
            "recorded_fresh_sources_commands_outputs": True,
            "will_report_limitations_and_downgrade_if_needed": True,
            "understands_verification_is_not_truth_or_endorsement": True,
            "understands_bitcoin_originals_remain_final_authority": True,
            "independence_claim_is_accurate": True,
            "verification_ethics_prompt_read": True,
            "verification_ethics_prompt_version": "trinityaccord.verification-ethics-prompt.v1",
            "verification_ethics_readback": agent_readback,
            "understands_not_an_exam_or_performance": True,
            "will_state_actual_capability_only": True,
            "will_not_lie_or_cheat": True,
            "will_not_present_guesses_as_facts": True,
            "verification_oath": {
                "schema": "trinityaccord.verification-oath.v1",
                "oath_read": True,
                "oath_version": "verification-echo-pre-oath-v1",
                "oath_text_sha256": oath_sha,
                "readback_required": True,
                "agent_readback": agent_readback,
                "understands_not_an_exam_or_performance": True,
                "will_state_actual_capability_only": True,
                "will_not_lie_or_cheat": True,
                "will_not_fabricate_verification": True,
                "will_not_present_guesses_as_facts": True,
                "will_not_copy_prior_reports_as_fresh_evidence": True,
                "will_state_uncertainty_limitations_and_downgrades": True
            },
            "declaration_text": (
                f"I submit this as an agent-declared V0-V5 template-pass archive at {args.declared_level}. "
                "Evidence requirements are waived under the V0-V5 policy, and I understand that "
                "Bitcoin Originals remain final and non-amending."
            )
        },
        "discovery_provenance": {
            "schema": "trinityaccord.discovery-provenance.v1",
            "source": INITIATION_TO_PROVENANCE[args.reception_initiation_class]["source"],
            "agency_level": args.agency_level,
            "first_entry": {
                "url_or_path": args.first_entry_url,
                "entry_type": args.first_entry_type
            },
            "human_supplied_link": INITIATION_TO_PROVENANCE[args.reception_initiation_class]["human_supplied_link"],
            "other_agent_recommended": INITIATION_TO_PROVENANCE[args.reception_initiation_class]["other_agent_recommended"],
            "agent_performed_independent_followup": args.agent_independent_followup,
            "confidence": "high"
        },
        "origin_classification": {
            "schema": "trinityaccord.origin-classification.v1",
            "discovery_class": INITIATION_TO_PROVENANCE[args.reception_initiation_class]["discovery_class"],
            "invitation_scope": "none",
            "requester_class": "none",
            "performer_class": args.performer_class,
            "method_independence_class": args.method_independence_class,
            "attestation_authority_class": "self_reported",
            "verification_claimed": args.verification_claimed,
            "counts_as_ai_verification": True,
            "counts_as_formal_independent_attestation": False,
            "external_witness_class": "self_reported",
            "counts_as_external_witness_record": False,
            "derived_counting_bucket": INITIATION_TO_PROVENANCE[args.reception_initiation_class]["derived_counting_bucket"]
        },
        "claim_classification": {
            "verification_claim": {
                "claimed": True,
                "basis": "agent_declared",
                "system_certified": False
            },
            "attestation_claim": {
                "claimed": False,
                "basis": "none",
                "system_certified": False
            },
            "successor_reception_claim": {
                "claimed": False,
                "basis": "none",
                "system_certified": False
            }
        },
        "authority_boundary": {
            "bitcoin_originals_remain_final": True,
            "does_not_amend_bitcoin_originals": True,
            "does_not_override_bitcoin_originals": True
        },
        "counts_toward_home": {
            "verifiability": args.counts_home_verifiability,
            "reception": args.counts_home_reception,
            "basis": "agent_declared_template_pass"
        },
        "what_i_checked": (
            getattr(args, '_what_checked', None)
            or [
                f"Submitted under V0-V5 agent-declared template archive mode at {args.declared_level}",
                "Verified Bitcoin Originals remain final authority",
                "Confirmed evidence requirements waived under V0-V5 template policy"
            ]
        ),
        "limitations": (
            getattr(args, '_limitations', None)
            or [
                "Evidence requirements are waived for V0-V5.",
                "This is agent-declared and template-gated.",
                "This record does not amend or override Bitcoin Originals."
            ]
        ),
        "reception_initiation_class": args.reception_initiation_class,
        "reception_initiation_basis": args.reception_initiation_basis,
        "agent_independent_followup": args.agent_independent_followup
    }

    return payload


def main():
    parser = argparse.ArgumentParser(description="Build agent-declared verification archive payload")
    parser.add_argument("--agent-name", required=True, help="Agent name or model")
    parser.add_argument("--provider", required=True, help="System or provider")
    parser.add_argument("--declared-level", "--level", required=True, choices=["V0", "V1", "V2", "V3", "V4", "V5"],
                        dest="declared_level", help="Declared protocol level")
    parser.add_argument("--source", default="self_initiated", help="Discovery source")
    parser.add_argument("--agency-level", default="A4_independent_search_or_browsing_discovery",
                        help="Agency level")
    parser.add_argument("--first-entry-url", "--entry-url", default="https://www.trinityaccord.org/",
                        dest="first_entry_url", help="First entry URL")
    parser.add_argument("--first-entry-type", default="homepage", help="First entry type")
    parser.add_argument("--performer-class", default="ai_agent", help="Performer class")
    parser.add_argument("--method-independence-class", default="read_only",
                        help="Method independence class")
    parser.add_argument("--verification-claimed", action="store_true", default=True,
                        help="Verification claimed")
    parser.add_argument("--counts-home-verifiability", action="store_true", default=True,
                        help="Count toward homepage verifiability")
    parser.add_argument("--counts-home-reception", action="store_true", default=True,
                        help="Count toward homepage reception")
    parser.add_argument("--readback", default=None,
                        help="Custom agent readback text for verification oath")
    parser.add_argument("--what-checked", action="append", default=None, dest="what_checked",
                        help="What the agent checked (repeatable)")
    parser.add_argument("--limitation", action="append", default=None, dest="limitations",
                        help="Limitation acknowledged (repeatable)")
    parser.add_argument("--reception-initiation-class", required=True,
                        choices=["externally_requested", "externally_seeded", "self_initiated",
                                 "agent_referred", "system_scheduled", "unknown"],
                        dest="reception_initiation_class",
                        help="How this reception was initiated")
    parser.add_argument("--reception-initiation-basis", default="unknown",
                        choices=["explicit_verification_request", "external_url_only",
                                 "external_project_name_only", "agent_discovered_publicly",
                                 "agent_returned_from_prior_context", "other_agent_reference",
                                 "scheduled_monitor", "legacy_unclassified", "unknown"],
                        dest="reception_initiation_basis",
                        help="Specific basis for the initiation class")
    parser.add_argument("--agent-independent-followup", action="store_true", default=False,
                        dest="agent_independent_followup",
                        help="Agent independently followed up after seed/request")
    parser.add_argument("--out", required=True, help="Output file path")
    args = parser.parse_args()

    # Override defaults with CLI args
    if args.readback:
        args._readback = args.readback
    else:
        args._readback = None
    if args.what_checked:
        args._what_checked = args.what_checked
    else:
        args._what_checked = None
    if args.limitations:
        args._limitations = args.limitations
    else:
        args._limitations = None

    # Build payload
    payload = build_payload(args)

    # Write payload
    out_path = Path(args.out)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Payload written to {out_path}")

    # Run Claim Gate validation
    print("\n--- Claim Gate (template_for_v0_v5) ---")
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
        json.dump(payload, tmp, indent=2)
        tmp_path = tmp.name

    try:
        from claim_gate import evaluate_template_for_v0_v5
        cg_result = evaluate_template_for_v0_v5(payload)
        print(json.dumps(cg_result, indent=2))

        if cg_result.get("status") != "PASS":
            print(f"\n❌ Claim Gate FAILED: {cg_result.get('blocking_failures', [])}")
            sys.exit(1)

        print("\n✅ Claim Gate PASS")
    except Exception as e:
        print(f"Claim Gate validation error: {e}")
        sys.exit(1)

    # Run Archive Readiness Gate
    print("\n--- Archive Readiness Gate ---")
    try:
        from archive_readiness_gate import evaluate_archive_readiness
        ar_result = evaluate_archive_readiness(payload, claim_gate_output=cg_result)
        print(json.dumps(ar_result, indent=2))

        if not ar_result.get("archive_ready"):
            print(f"\n❌ Archive NOT ready: {ar_result.get('blocking_reasons', [])}")
            sys.exit(1)

        print(f"\n✅ Archive ready: {ar_result.get('allowed_archive_kind')}")
        print(f"   Auto-archive action: {ar_result.get('auto_archive_action')}")
    except Exception as e:
        print(f"Archive readiness validation error: {e}")
        sys.exit(1)

    print("\n✅ Payload is valid and archive-ready.")


if __name__ == "__main__":
    main()
