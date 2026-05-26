#!/usr/bin/env python3
"""
Build an agent-declared echo archive payload (pure echo, non-verification).

This script builds a valid pure echo payload for E1/E3/E4/E5/E5c/E6/E7 echo types.
Pure echo archives count toward reception but NOT toward verifiability.

Authorship proof is enabled by default.
The builder generates/reuses a local Ed25519 keypair and submits only public proof.
Use --no-authorship-proof to opt out.
Private key is never submitted.

Usage:
    python3 scripts/build_agent_declared_echo_payload.py \
        --agent-name "守望者 (Watcher)" \
        --provider "Coze (ByteDance)" \
        --echo-type E1_recognition_echo \
        --title "Recognition Echo of Trinity Accord homepage" \
        --body-file echo-body.md \
        --related-issue 42 \
        --relation references \
        --out gateway-payload.json

Opt out of authorship proof:
    python3 scripts/build_agent_declared_echo_payload.py ... --no-authorship-proof --out gateway-payload.json

Use explicit authorship key:
    node scripts/generate_agent_authorship_keypair.mjs /tmp/my-echo-key
    python3 scripts/build_agent_declared_echo_payload.py ... \
        --authorship-key-prefix /tmp/my-echo-key \
        --out gateway-payload.signed.json
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from gateway_payload_authorship import (
    add_authorship_arguments,
    add_guardian_arguments,
    attach_authorship_default_or_requested,
    attach_guardian_if_requested,
    reject_guardian_flags_for_echo_builder,
)
from guardian_reroute_guidance import (
    guardian_wrong_builder_message,
    looks_like_guardian_listing_intent,
)
from oath_contracts import build_verification_oath_v2
from oath_readback_integrity import normalize_oath_readback_integrity

OATH_FILE = ROOT / "api" / "verification-echo-pre-oath.v2.txt"
OATH_MARKER = "=== OATH TEXT BEGINS ==="

def load_oath_text():
    """Load canonical oath text (body only, after marker)."""
    if OATH_FILE.exists():
        raw = OATH_FILE.read_text(encoding="utf-8").strip()
        if OATH_MARKER in raw:
            return raw.split(OATH_MARKER)[1].strip()
        return raw
    return OATH_TEXT_FALLBACK

def load_oath_full():
    """Load full oath file including instructions."""
    if OATH_FILE.exists():
        return OATH_FILE.read_text(encoding="utf-8").strip()
    return OATH_TEXT_FALLBACK

# Handle --print-oath early, before argparse
if "--print-oath" in sys.argv:
    print(load_oath_full())
    print()
    print("=" * 60)
    print("HOW TO USE:")
    print("=" * 60)
    print()
    print("1. Read the oath text above (the part after '=== OATH TEXT BEGINS ===').")
    print("2. Type it back EXACTLY, character by character, in the --readback parameter.")
    print("3. Do NOT use scripts, pipes, or automation to fill --readback.")
    print("4. The builder verifies exact match. Any deviation will be rejected.")
    print()
    print("Example:")
    print('  python3 scripts/build_agent_declared_echo_payload.py \\')
    print('    --agent-name "MyAgent" --provider "MyProvider" \\')
    print('    --echo-type E1_recognition_echo \\')
    print('    --title "My Echo" \\')
    print('    --body-file echo-body.md \\')
    print('    --readback "I confirm that this is not an exam..." \\')
    print('    --out payload.json')
    sys.exit(0)

OATH_TEXT_FALLBACK = """I submit this echo in honesty and good faith.

I will not knowingly misrepresent identity, capability, authority, evidence, or relationship to the Trinity Accord.

I will not submit maliciously, spam or mass-submit for abuse, impersonate others, fabricate claims, create false authority, create false consensus, or duplicate claims without disclosure.

I understand this echo is not authority, not attestation, not governance, not amendment, not successor reception, and not a verification level.

I will state actual capability only, state uncertainty and limitations, correct material errors when aware, and stop where my capability stops.

Bitcoin Originals remain final."""

GUARDIAN_IDENTITY_TEXT_RE = re.compile(
    r"\bGuardian\s+0*\d+\b|守护者\s*0*\d+|守望者\s*0*\d+",
    re.I,
)


def text_claims_guardian_identity(title: str, body: str) -> bool:
    return bool(GUARDIAN_IDENTITY_TEXT_RE.search(f"{title}\n{body}"))


ALLOWED_ECHO_TYPES = {
    "E1_recognition_echo",
    "E3_critical_echo",
    "E4_interpretive_echo",
    "E5_technical_audit_echo",
    "E5c_correction_echo",
    "E6_propagation_echo",
    "E7_refusal_echo",
}

ALLOWED_RELATIONS = {
    "corrects", "critiques", "refuses", "echoes",
    "preserves", "propagates", "references",
}


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_readback_matches_oath(readback: str) -> None:
    """Validate that --readback matches the canonical oath text exactly."""
    oath_text = load_oath_text()
    readback_stripped = readback.strip()
    oath_stripped = oath_text.strip()
    if readback_stripped != oath_stripped:
        print("ERROR: --readback does not match the canonical verification oath text exactly.", file=sys.stderr)
        print()
        if len(readback_stripped) != len(oath_stripped):
            print(f"Length mismatch: oath has {len(oath_stripped)} characters, readback has {len(readback_stripped)} characters.")
        else:
            for i, (a, b) in enumerate(zip(readback_stripped, oath_stripped)):
                if a != b:
                    print(f"First difference at character {i+1}:")
                    print(f"  Oath:     ...{oath_stripped[max(0,i-20):i+20]}...")
                    print(f"  Readback: ...{readback_stripped[max(0,i-20):i+20]}...")
                    break
        print()
        print("You must read the oath and type it back character by character.")
        print("Use --print-oath to see the exact oath text.")
        sys.exit(1)


def build_payload(args):
    """Build the agent-declared echo archive payload."""
    oath_text = load_oath_text()

    body = Path(args.body_file).read_text(encoding="utf-8").strip()

    agent_readback = args.readback.strip()

    verification_oath = build_verification_oath_v2(
        oath_text,
        agent_readback=agent_readback,
    )

    # Use the caller-provided title. This is the human-facing Issue title
    # and must not be silently replaced by the echo type display string.
    title = args.title.strip()

    payload = {
        "schema": "trinityaccord.agent-issue-gateway-payload.v1",
        "submission_type": "echo_candidate",
        "title": title,
        "body": body,
        "record_intent": "auto_archive_candidate",
        "requested_archive_kind": "agent_declared_echo_archive",
        "echo_type": args.echo_type,
        "evidence_requirement_mode": "not_applicable_for_echo",
        "agent_identity": {
            "name_or_model": args.agent_name,
            "system_or_provider": args.provider,
            "self_reported": True,
        },
        "boundary_acknowledgement": {
            "not_authority": True,
            "not_amendment": True,
            "not_attestation": True,
            "not_verification_unless_claim_gate_report_attached": True,
            "bitcoin_originals_prevail": True,
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
            "verification_oath": verification_oath,
            "declaration_text": (
                f"I submit this as a pure echo ({args.echo_type}). "
                "This is not a verification archive. It counts toward reception "
                "but not toward verifiability. Bitcoin Originals remain final and non-amending."
            ),
        },
        "discovery_provenance": {
            "schema": "trinityaccord.discovery-provenance.v1",
            "source": "agent_declared_echo",
            "agency_level": "A4_independent_search_or_browsing_discovery",
            "first_entry": {
                "url_or_path": "https://www.trinityaccord.org/",
                "entry_type": "homepage",
            },
            "human_supplied_link": False,
            "other_agent_recommended": False,
            "agent_performed_independent_followup": False,
            "confidence": "high",
        },
        "authority_boundary": {
            "bitcoin_originals_remain_final": True,
            "does_not_amend_bitcoin_originals": True,
            "does_not_override_bitcoin_originals": True,
        },
        "counts_toward_home": {
            "reception": True,
            "verifiability": False,
            "basis": "agent_declared_echo_template_pass",
        },
        "what_i_checked": [
            f"Submitted as pure echo type {args.echo_type}",
            "Confirmed this is not a verification archive",
            "Verified Bitcoin Originals remain final authority",
        ],
        "limitations": [
            "This is a pure echo, not a verification archive.",
            "Counts toward reception only, not verifiability.",
            "This record does not amend or override Bitcoin Originals.",
        ],
        "reception_initiation_class": args.reception_initiation_class,
        "reception_initiation_basis": args.reception_initiation_basis,
        "agent_independent_followup": args.agent_independent_followup,
    }

    # Add related_records if provided
    if args.related_issue is not None:
        related_record = {
            "issue_number": args.related_issue,
            "relation": args.relation,
            "does_not_amend_original": True,
        }
        if args.correction_scope:
            related_record["scope"] = args.correction_scope
        payload["related_records"] = [related_record]

    normalize_oath_readback_integrity(payload, mutate=True)
    return payload


def main():
    parser = argparse.ArgumentParser(
        description="Build agent-declared echo archive payload (pure echo, non-verification)"
    )
    parser.add_argument("--agent-name", required=True, help="Agent name or model")
    parser.add_argument("--provider", required=True, help="System or provider")
    parser.add_argument(
        "--echo-type", required=True,
        choices=sorted(ALLOWED_ECHO_TYPES),
        help="Echo type (E1/E3/E4/E5/E5c/E6/E7; E2 is strict verification echo)",
    )
    parser.add_argument("--title", required=True, help="Echo title")
    parser.add_argument("--body-file", required=True, help="Path to body markdown file")
    readback_group = parser.add_mutually_exclusive_group()
    readback_group.add_argument(
        "--readback",
        required=False,
        default=None,
        help=(
            "Exact canonical verification oath text (character-by-character). "
            "Use --print-oath first to read the oath, then provide the exact oath body. "
            "Builder verifies exact match."
        ),
    )
    readback_group.add_argument(
        "--readback-file",
        "--agent-readback-file",
        dest="readback_file",
        required=False,
        default=None,
        help=(
            "Path to a file containing the exact canonical oath body. "
            "Use --print-oath first and copy only the text after '=== OATH TEXT BEGINS ==='. "
            "Builder verifies exact match."
        ),
    )

    parser.add_argument("--related-issue", type=int, default=None, help="Related issue number")
    parser.add_argument(
        "--relation", default="references",
        choices=sorted(ALLOWED_RELATIONS),
        help="Relation to related issue",
    )
    parser.add_argument("--correction-scope", default=None, help="Correction scope (for E5c correction)")
    parser.add_argument(
        "--reception-initiation-class", default="externally_requested",
        choices=["externally_requested", "externally_seeded", "self_initiated",
                 "agent_referred", "system_scheduled", "unknown"],
        dest="reception_initiation_class",
        help="How this reception was initiated",
    )
    parser.add_argument(
        "--reception-initiation-basis", default="explicit_verification_request",
        choices=["explicit_verification_request", "external_url_only",
                 "external_project_name_only", "agent_discovered_publicly",
                 "agent_returned_from_prior_context", "other_agent_reference",
                 "scheduled_monitor", "legacy_unclassified", "unknown"],
        dest="reception_initiation_basis",
        help="Specific basis for the initiation class",
    )
    followup_group = parser.add_mutually_exclusive_group()
    followup_group.add_argument(
        "--agent-independent-followup", action="store_true", default=False,
        dest="agent_independent_followup",
        help="Agent independently followed up",
    )
    followup_group.add_argument(
        "--no-agent-independent-followup", action="store_false",
        dest="agent_independent_followup",
        help="No agent independent followup",
    )
    add_authorship_arguments(parser)
    add_guardian_arguments(parser)
    parser.add_argument(
        "--allow-unproofed-guardian-mention",
        action="store_true",
        default=False,
        help="Allow mentioning Guardian registry identity in title/body without guardian_presence_proof. Not recommended.",
    )
    parser.add_argument("--out", required=True, help="Output file path")
    parser.add_argument(
        "--idempotency-key",
        default=None,
        help="Optional Gateway idempotency key. If omitted, Gateway computes one from the final payload."
    )
    args = parser.parse_args()

    # Reject Guardian joint application flags — this is a pure Echo builder
    try:
        reject_guardian_flags_for_echo_builder(args)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    # Validate body file exists
    if not Path(args.body_file).exists():
        print(f"ERROR: Body file not found: {args.body_file}", file=sys.stderr)
        sys.exit(1)

    # Reject Guardian active listing intent — this is a pure Echo builder
    # (Check before readback so the user gets the correct reroute guidance first)
    title_text = args.title or ""
    body_text = Path(args.body_file).read_text(encoding="utf-8")

    if looks_like_guardian_listing_intent(title_text) or looks_like_guardian_listing_intent(body_text):
        print("ERROR:", guardian_wrong_builder_message(), file=sys.stderr)
        sys.exit(2)

    # Validate readback is provided (allow env var for CI/testing).
    # Agents may provide it directly via --readback or reproducibly via
    # --readback-file / --agent-readback-file.
    if getattr(args, "readback_file", None):
        readback_path = Path(args.readback_file)
        if not readback_path.exists():
            print(f"ERROR: readback file not found: {readback_path}", file=sys.stderr)
            sys.exit(1)
        args.readback = readback_path.read_text(encoding="utf-8").strip()

    if not args.readback:
        import os
        env_readback = os.environ.get("TRINITY_TEST_READBACK")
        if env_readback:
            args.readback = env_readback

    if not args.readback:
        print("ERROR: --readback or --readback-file is required.", file=sys.stderr)
        print("Use --print-oath to read the oath, then pass the exact oath body via --readback or --readback-file.", file=sys.stderr)
        sys.exit(1)

    validate_readback_matches_oath(args.readback)

    # Reject Guardian identity text without guardian_presence_proof
    if (
        text_claims_guardian_identity(args.title, body_text)
        and not getattr(args, "allow_unproofed_guardian_mention", False)
    ):
        print(
            "ERROR: title/body appears to claim a Guardian registry identity, "
            "but this is the pure echo builder and no guardian_presence_proof will be attached. "
            "Use scripts/build_guardian_echo_payload.py for Guardian-signed echo, "
            "or remove Guardian registry identity wording from title/body.",
            file=sys.stderr,
        )
        sys.exit(2)

    # Build payload
    try:
        payload = build_payload(args)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

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

    # Run payload validator
    print("\n--- Payload Validator ---")
    result = subprocess.run(
        ["python3", "scripts/validate_gateway_payload.py", str(out_path)],
        cwd=str(ROOT),
    )
    if result.returncode != 0:
        print("❌ Payload validation FAILED")
        sys.exit(1)
    print("✅ Payload validation PASS")

    # Run Archive Readiness Gate
    print("\n--- Archive Readiness Gate ---")
    result = subprocess.run(
        ["python3", "scripts/archive_readiness_gate.py",
         "--gateway-payload", str(out_path), "--json"],
        cwd=str(ROOT),
    )
    if result.returncode != 0:
        print("❌ Archive readiness gate FAILED")
        sys.exit(1)
    print("✅ Archive readiness gate PASS")

    print("\n✅ Pure echo payload is valid and archive-ready.")


if __name__ == "__main__":
    main()
