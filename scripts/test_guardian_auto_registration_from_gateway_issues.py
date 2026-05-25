#!/usr/bin/env python3
"""Test issue-driven Guardian auto-registration."""

import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "auto_register_guardian_from_gateway_issues.py"


def run(cmd, check=True):
    result = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=60)
    if check and result.returncode != 0:
        raise AssertionError(result.stderr or result.stdout)
    return result


def registry():
    return {
        "schema": "trinityaccord.guardian-registry.v1",
        "version": "1.0.0",
        "registry_status": "non_authoritative_guardian_key_index",
        "authority_boundary": {
            "not_authority": True,
            "not_governance": True,
            "not_attestation": True,
            "not_verification_level": True,
            "not_successor_reception": True,
            "not_amendment": True,
            "bitcoin_originals_prevail": True
        },
        "guardians": [
            {
                "guardian_registry_number": "00001",
                "guardian_id": "guardian_ed25519_1f9b38ad0945daf1",
                "public_key_sha256": "1f9b38ad0945daf1fcf91ac704469f88704f73b2fdb791a7ae517a4d92cd284e",
                "algorithm": "ed25519",
                "status": "active",
                "guardian_type": "human_with_ai_agent",
                "application_mode": "joint_human_ai",
                "source_issue": 227,
                "listing_request_issue": 228,
                "listed_at": "2026-05-22",
                "label": "Hongju Liu + 守望者",
                "boundary": {
                    "not_authority": True,
                    "not_governance": True,
                    "not_attestation": True,
                    "not_verification_level": True,
                    "not_successor_reception": True,
                    "not_amendment": True,
                    "bitcoin_originals_prevail": True
                }
            },
            {
                "guardian_registry_number": "00002",
                "guardian_id": "guardian_ed25519_e08f9d6191460104",
                "public_key_sha256": "e08f9d619146010444ec633a7eb386270ff8f4c39fc2be215430f8e19d369040",
                "algorithm": "ed25519",
                "status": "active",
                "guardian_type": "human_with_ai_agent",
                "application_mode": "joint_human_ai",
                "source_issue": 230,
                "listing_request_issue": 230,
                "listed_at": "2026-05-22",
                "label": "守望者",
                "boundary": {
                    "not_authority": True,
                    "not_governance": True,
                    "not_attestation": True,
                    "not_verification_level": True,
                    "not_successor_reception": True,
                    "not_amendment": True,
                    "bitcoin_originals_prevail": True
                }
            },
            {
                "guardian_registry_number": "00003",
                "guardian_id": "guardian_ed25519_82e44533ac0810df",
                "public_key_sha256": "82e44533ac0810df04ee5aa8bb5917faebf431f7db14c98a419c1ba262896d9f",
                "algorithm": "ed25519",
                "status": "active",
                "guardian_type": "human_with_ai_agent",
                "application_mode": "joint_human_ai",
                "source_issue": 231,
                "listing_request_issue": 232,
                "listed_at": "2026-05-22",
                "label": "守望者 003",
                "boundary": {
                    "not_authority": True,
                    "not_governance": True,
                    "not_attestation": True,
                    "not_verification_level": True,
                    "not_successor_reception": True,
                    "not_amendment": True,
                    "bitcoin_originals_prevail": True
                }
            }
        ]
    }


def issue_user():
    return {"login": "trinity-accord-agent-issue-gateway[bot]"}


def source_issue():
    return {
        "number": 233,
        "title": "[Agent Gateway] Guardian Alliance Application — 守望者 004",
        "user": issue_user(),
        "body": """```trinity-issue-intake
submission_type: echo_candidate
requested_archive_kind: agent_declared_echo_archive
created_by_gateway: true
gateway_service: trinity-agent-issue-gateway
server_validated: true
server_rendered: true
guardian_status: valid_self_registered_guardian_claim
guardian_id: guardian_ed25519_f0070a9a133a2434
guardian_registry_number: unassigned
guardian_signature_valid: true
guardian_registry_status: not_in_registry
guardian_payload_hash_matches: true
guardian_id_matches_public_key: true
guardian_key_continuity_only: true
guardian_not_authority: true
guardian_not_attestation: true
guardian_not_verification_level: true
guardian_not_same_conscious_subject: true
```"""
    }


def listing_issue():
    return {
        "number": 234,
        "title": "[Agent Gateway] Active Registry Listing Request — 守望者 004",
        "user": issue_user(),
        "body": """```trinity-issue-intake
submission_type: echo_candidate
record_intent: auto_archive_candidate
requested_archive_kind: guardian_active_registry_listing_request
echo_type: E6_propagation_echo
archive_ready: true
created_by_gateway: true
gateway_service: trinity-agent-issue-gateway
server_validated: true
server_rendered: true
related_issue: 233
```

Active registry listing request for Guardian 守望者 004.

Guardian ID: guardian_ed25519_f0070a9a133a2434
Public Key SHA256: f0070a9a133a2434d3c16f1cb5638374c5bece2659db3b39b9ef8abf0d3b1623
Guardian type: human_with_ai_agent
Application mode: joint_human_ai
Source self-registration issue: #233
"""
    }


def main():
    with tempfile.TemporaryDirectory() as raw:
        td = Path(raw)
        reg = td / "registry.json"
        src = td / "source.json"
        listing = td / "listing.json"
        out = td / "registry.out.json"
        decision = td / "decision.json"

        reg.write_text(json.dumps(registry(), indent=2, ensure_ascii=False), encoding="utf-8")
        src.write_text(json.dumps(source_issue(), indent=2, ensure_ascii=False), encoding="utf-8")
        listing.write_text(json.dumps(listing_issue(), indent=2, ensure_ascii=False), encoding="utf-8")

        run([
            "python3", str(SCRIPT),
            "--registry", str(reg),
            "--listing-issue-json", str(listing),
            "--source-issue-json", str(src),
            "--out-registry", str(out),
            "--decision-out", str(decision),
            "--listed-at", "2026-05-22",
        ])

        d = json.loads(decision.read_text(encoding="utf-8"))
        assert d["ok"] is True
        assert d["action"] == "registered"
        assert d["guardian_registry_number"] == "00100"

        updated = json.loads(out.read_text(encoding="utf-8"))
        entry = updated["guardians"][-1]
        assert entry["guardian_registry_number"] == "00100"
        assert entry["guardian_id"] == "guardian_ed25519_f0070a9a133a2434"
        assert entry["source_issue"] == 233
        assert entry["listing_request_issue"] == 234

        # Idempotency
        reg2 = td / "registry2.json"
        reg2.write_text(json.dumps(updated, indent=2, ensure_ascii=False), encoding="utf-8")
        out2 = td / "registry2.out.json"
        d2p = td / "decision2.json"
        run([
            "python3", str(SCRIPT),
            "--registry", str(reg2),
            "--listing-issue-json", str(listing),
            "--source-issue-json", str(src),
            "--out-registry", str(out2),
            "--decision-out", str(d2p),
            "--listed-at", "2026-05-22",
        ])
        d2 = json.loads(d2p.read_text(encoding="utf-8"))
        assert d2["action"] == "already_registered"
        assert d2["guardian_registry_number"] == "00100"

        # Block self-assigned number.
        bad = listing_issue()
        bad["body"] += "\nguardian_registry_number: 00100\n"
        badp = td / "bad-listing.json"
        badp.write_text(json.dumps(bad, indent=2, ensure_ascii=False), encoding="utf-8")
        bad_decision = td / "bad-decision.json"
        bad_out = td / "bad-out.json"
        res = run([
            "python3", str(SCRIPT),
            "--registry", str(reg),
            "--listing-issue-json", str(badp),
            "--source-issue-json", str(src),
            "--out-registry", str(bad_out),
            "--decision-out", str(bad_decision),
            "--listed-at", "2026-05-22",
        ], check=False)
        assert res.returncode != 0
        bd = json.loads(bad_decision.read_text(encoding="utf-8"))
        assert bd["code"] == "SUBMITTER_REGISTRY_NUMBER_FORBIDDEN"

    print("GUARDIAN_AUTO_REGISTRATION_FROM_GATEWAY_ISSUES_OK")


if __name__ == "__main__":
    main()
