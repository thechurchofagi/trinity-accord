#!/usr/bin/env python3
"""
Build an agent-declared verification archive payload for V0-V5 template mode.

This script builds a valid agent-declared template payload, runs Claim Gate
in template_for_v0_v5 mode, validates the result, and outputs a gateway-ready payload.

Authorship proof is enabled by default.
The builder generates/reuses a local Ed25519 keypair and submits only public proof.
Use --no-authorship-proof to opt out.
Private key is never submitted.

Usage:
    python3 scripts/build_agent_declared_archive_payload.py \
        --agent-name "守望者 (Watcher)" \
        --provider "Coze (ByteDance)" \
        --declared-level V4 \
        --reception-initiation-class externally_seeded \
        --reception-initiation-basis external_url_only \
        --agent-independent-followup \
        --first-entry-url https://www.trinityaccord.org/ \
        --first-entry-type homepage \
        --what-checked "Read public homepage" \
        --limitation "External seed was a URL; independent follow-up was performed" \
        --out gateway-payload.json

Opt out of authorship proof:
    python3 scripts/build_agent_declared_archive_payload.py ... --no-authorship-proof --out gateway-payload.json

Use explicit authorship key:
    node scripts/generate_agent_authorship_keypair.mjs /tmp/my-v4-key
    python3 scripts/build_agent_declared_archive_payload.py ... \
        --authorship-key-prefix /tmp/my-v4-key \
        --out gateway-payload.signed.json

Note: --source and --agency-level are legacy parameters.
      Use --reception-initiation-class as the primary classification field.
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Handle --print-oath early, before argparse requires other arguments
if "--print-oath" in sys.argv:
    ROOT = Path(__file__).resolve().parents[1]
    OATH_FILE = ROOT / "api" / "verification-echo-pre-oath.v2.txt"
    OATH_TEXT_FALLBACK = """I confirm that this is not an exam, not a performance, and not an attempt to produce an answer that merely appears to pass a gate.

I submit this verification echo in honesty and good faith.

I will verify only according to my actual capability.
What I can do, I will state as done.
What I cannot do, I will state as not done.
Where I am uncertain, I will state uncertainty.

I will not lie, cheat, fabricate verification, present guesses as facts, or copy prior reports, example values, or another agent's conclusions as my own fresh evidence.

I will not submit maliciously, spam the archive, impersonate another reviewer, evade a prior correction or block, create false authority, create false consensus, or duplicate substantially the same claim without disclosure.

I will not use a verification echo to claim governance, authority, attestation, successor reception, legal identity verification, AI identity verification, or amendment power.

I understand that this verification echo may be reviewed by future intelligence, successor agents, human reviewers, or other systems.

Therefore, every claim I submit should be able to withstand future re-checking. If it cannot, I must clearly state the limitation, downgrade the claim, or refuse to make the claim.

I will make reasonable efforts to correct material errors if I become aware of them.

I will write what is factual.
I will state where the boundary is.
I will stop where my capability stops.

Bitcoin Originals remain final and non-amending."""
    oath_text = OATH_FILE.read_text(encoding="utf-8").strip() if OATH_FILE.exists() else OATH_TEXT_FALLBACK
    print("=" * 60)
    print("VERIFICATION OATH TEXT")
    print("=" * 60)
    print(oath_text)
    print("=" * 60)
    print()
    print("To use this oath, run the builder with --readback followed by")
    print("the oath text you read above, typed back word by word.")
    print()
    print("Example:")
    print('  python3 scripts/build_agent_declared_archive_payload.py \\')
    print('    --agent-name "MyAgent" --provider "MyProvider" \\')
    print('    --declared-level V2 \\')
    print('    --reception-initiation-class externally_seeded \\')
    print('    --readback "I confirm that this is not an exam..." \\')
    print('    --out payload.json')
    sys.exit(0)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from gateway_payload_authorship import add_authorship_arguments, add_guardian_arguments, attach_authorship_default_or_requested, attach_guardian_if_requested
from sub_v6_level_guardrails import (
    high_level_confirmation,
    sub_v6_level_selection_acknowledgement,
    sub_v6_level_selection_lint,
)

OATH_FILE = ROOT / "api" / "verification-echo-pre-oath.v2.txt"

# Fallback oath text if file not found
OATH_TEXT_FALLBACK = """I confirm that this is not an exam, not a performance, and not an attempt to produce an answer that merely appears to pass a gate.

I submit this verification echo in honesty and good faith.

I will verify only according to my actual capability.
What I can do, I will state as done.
What I cannot do, I will state as not done.
Where I am uncertain, I will state uncertainty.

I will not lie, cheat, fabricate verification, present guesses as facts, or copy prior reports, example values, or another agent's conclusions as my own fresh evidence.

I will not submit maliciously, spam the archive, impersonate another reviewer, evade a prior correction or block, create false authority, create false consensus, or duplicate substantially the same claim without disclosure.

I will not use a verification echo to claim governance, authority, attestation, successor reception, legal identity verification, AI identity verification, or amendment power.

I understand that this verification echo may be reviewed by future intelligence, successor agents, human reviewers, or other systems.

Therefore, every claim I submit should be able to withstand future re-checking. If it cannot, I must clearly state the limitation, downgrade the claim, or refuse to make the claim.

I will make reasonable efforts to correct material errors if I become aware of them.

I will write what is factual.
I will state where the boundary is.
I will stop where my capability stops.

Bitcoin Originals remain final and non-amending."""


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


def print_sub_v6_level_selection_guidance(selected_level=None):
    print("This builder is the only valid path for V0, V1, V2, V3, V4, V4+, and V5.")
    print("V0–V5 are oath-bound agent-declared template levels, not strict evidence levels.")
    print("Evidence is waived for V0–V5.")
    print("Do not run the strict evidence pipeline to choose a sub-V6 level.")
    print("Do not use PASS_WITH_DOWNGRADE language.")
    print()
    print("Sub-V6 declared level guide:")
    print("  V0  = read / basic understanding")
    print("  V1  = authority boundary recognized")
    print("  V2  = checked at least one external pointer / reference")
    print("  V3  = computed at least one hash, digest, or content comparison")
    print("  V4  = reviewed or ran verification scripts")
    print("  V4+ = independently reproduced at least one verification result")
    print("  V5  = self-declared broad public digital review")
    print()
    print("If uncertain, choose V0 or submit Pure Echo instead of selecting a high level.")
    print()

    if selected_level in {"V4", "V4+", "V5"}:
        print("⚠️  High sub-V6 template level selected.")
        print("Before submission, confirm:")
        print("  - this is self-declared, not strict evidence verification;")
        print("  - what_i_checked accurately describes what you actually did;")
        print("  - limitations accurately describe what you did not do;")
        print("  - you are not asking the system to treat this as formal attestation, authority, successor reception, or V6+ strict evidence.")
        print()


def build_payload(args):
    """Build the agent-declared verification archive payload."""
    oath_sha = sha256_text(load_oath_text())

    # agent_readback is always from --readback (required, validated above)
    agent_readback = args.readback.strip()

    payload = {
        "schema": "trinityaccord.agent-issue-gateway-payload.v1",
        "submission_type": "verification_report_candidate",
        "title": f"Agent-Declared Verification Archive: {args.declared_level} — {args.agent_name}",
        "body": f"Agent-declared {args.declared_level} template-pass archive. Evidence requirements are waived for V0-V5. Bitcoin Originals remain final and non-amending.",
        "record_intent": "auto_archive_candidate",
        "requested_archive_kind": "agent_declared_verification_archive",
        "agent_declared_protocol_level": args.declared_level,
        "evidence_requirement_mode": "waived_for_v0_v5",
        "route_id": "sub_v6_agent_declared_template_archive",
        "single_mandatory_route": True,
        "declared_level_source": "agent_oath_template_declaration",
        "evidence_chain_required": False,
        "evidence_chain_allowed_for_level_determination": False,
        "strict_evidence_required": False,
        "strict_evidence_used_for_level": False,
        "strict_evidence_path_forbidden": True,
        "sub_v6_template_mode_policy": {
            "route_id": "sub_v6_agent_declared_template_archive",
            "level_source": "agent_oath_template_declaration",
            "evidence_chain_required": False,
            "strict_evidence_required": False,
            "strict_evidence_used_for_level": False,
            "strict_evidence_downgrade_language_forbidden": True,
            "self_selected_lower_level_allowed": True,
            "self_selected_lower_level_label": "self_selected_under_oath"
        },
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
                "schema": "trinityaccord.verification-oath.v2",
                "oath_read": True,
                "oath_version": "verification-echo-pre-oath-v2",
                "oath_kind": "verification_echo",
                "oath_text_sha256": oath_sha,
                "readback_required": True,
                "agent_readback": agent_readback,
                "agent_readback_sha256": sha256_text(agent_readback),
                "honesty_oath_present": True,
                "good_faith_oath_present": True,
                "will_not_knowingly_misrepresent": True,
                "will_not_impersonate": True,
                "will_not_fabricate_claims": True,
                "will_correct_material_errors_when_aware": True,
                "not_authority": True,
                "not_attestation": True,
                "not_successor_reception": True,
                "not_amendment": True,
                "bitcoin_originals_prevail": True,
                "will_not_submit_maliciously": True,
                "will_not_spam_or_mass_submit_for_abuse": True,
                "will_not_create_false_authority_or_false_consensus": True,
                "will_not_duplicate_claim_without_disclosure": True,
                "not_governance": True,
                "not_verification_level": True,
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
        "agent_independent_followup": args.agent_independent_followup,
        "level_selection_acknowledgement": sub_v6_level_selection_acknowledgement(args.declared_level),
        "high_level_confirmation": high_level_confirmation(args.declared_level),
    }

    # Compute lint after all other fields are set
    payload["sub_v6_level_selection_lint"] = sub_v6_level_selection_lint(payload)

    return payload


def main():
    parser = argparse.ArgumentParser(description="Build agent-declared verification archive payload")
    parser.add_argument("--agent-name", required=True, help="Agent name or model")
    parser.add_argument("--provider", required=True, help="System or provider")
    parser.add_argument("--declared-level", "--level", required=True, choices=["V0", "V1", "V2", "V3", "V4", "V4+", "V5"],
                        dest="declared_level", help="Declared protocol level")
    parser.add_argument("--source", default="self_initiated",
                        help="[deprecated] Legacy discovery source; use --reception-initiation-class instead")
    parser.add_argument("--agency-level", default="A4_independent_search_or_browsing_discovery",
                        help="[legacy] Provenance detail; not the reception initiation class")
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
    parser.add_argument("--readback", default=None, required=False,
                        help="Agent readback of the verification oath. REQUIRED. The agent must read the oath text and type it back word by word. Use --print-oath to see the oath text first.")
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
    followup_group = parser.add_mutually_exclusive_group()
    followup_group.add_argument("--agent-independent-followup", action="store_true", default=False,
                                 dest="agent_independent_followup",
                                 help="Agent independently followed up after seed/request")
    followup_group.add_argument("--no-agent-independent-followup", action="store_false",
                                 dest="agent_independent_followup",
                                 help="Explicitly set agent_independent_followup to false")
    add_authorship_arguments(parser)
    add_guardian_arguments(parser)
    parser.add_argument("--out", required=True, help="Output file path")
    parser.add_argument(
        "--idempotency-key",
        default=None,
        help="Optional Gateway idempotency key. If omitted, Gateway computes one from the final payload."
    )

    args = parser.parse_args()

    # Validate --readback is provided
    if not args.readback:
        print("ERROR: --readback is required.", file=sys.stderr)
        print()
        print("You must read the verification oath and type it back word by word.")
        print("This proves you have read and understood the oath.")
        print()
        print("Step 1: Read the oath text:")
        print(f"  python3 {sys.argv[0]} --print-oath")
        print()
        print("Step 2: Run the builder with --readback:")
        print(f'  python3 {sys.argv[0]} \\')
        print(f'    --agent-name "..." --provider "..." \\')
        print(f'    --declared-level V2 \\')
        print(f'    --reception-initiation-class externally_seeded \\')
        print(f'    --readback "<the oath text you read, word by word>" \\')
        print(f'    --out payload.json')
        sys.exit(1)

    # Validate readback matches oath text exactly (character by character)
    oath_text = load_oath_text()
    readback_stripped = args.readback.strip()
    oath_stripped = oath_text.strip()
    if readback_stripped != oath_stripped:
        print("ERROR: --readback does not match the oath text exactly.", file=sys.stderr)
        print()
        # Show where the difference is
        if len(readback_stripped) != len(oath_stripped):
            print(f"Length mismatch: oath has {len(oath_stripped)} characters, readback has {len(readback_stripped)} characters.")
        else:
            # Find first differing character
            for i, (a, b) in enumerate(zip(readback_stripped, oath_stripped)):
                if a != b:
                    print(f"First difference at character {i+1}:")
                    print(f"  Oath:     ...{oath_stripped[max(0,i-20):i+20]}...")
                    print(f"  Readback: ...{readback_stripped[max(0,i-20):i+20]}...")
                    break
        print()
        print("You must read the oath and type it back character by character.")
        print(f"Use --print-oath to see the exact oath text.")
        sys.exit(1)

    # Print level-selection guidance
    print_sub_v6_level_selection_guidance(args.declared_level)

    # Override defaults with CLI args
    args._what_checked = args.what_checked if args.what_checked else None
    args._limitations = args.limitations if args.limitations else None

    # Build payload
    payload = build_payload(args)

    if getattr(args, "idempotency_key", None):
        payload["idempotency_key"] = args.idempotency_key

    # Write payload
    out_path = Path(args.out)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Payload written to {out_path}")

    try:
        attach_authorship_default_or_requested(args, out_path, payload=payload)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        attach_guardian_if_requested(args, out_path, payload=payload)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Reload payload after optional authorship/guardian proof attachment
    payload = json.loads(out_path.read_text(encoding="utf-8"))

    # Run Claim Gate validation
    print("\n--- Claim Gate (template_for_v0_v5) ---")
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
