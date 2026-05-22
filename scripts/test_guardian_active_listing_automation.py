#!/usr/bin/env python3
"""Test Guardian active listing automation and anti-abuse checks."""

import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "create_guardian_application.mjs"
PREPARE = ROOT / "scripts" / "prepare_guardian_active_listing.py"
VERIFY = ROOT / "scripts" / "verify_guardian_status.py"


def run(cmd, check=True):
    result = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=60)
    if check and result.returncode != 0:
        raise AssertionError(result.stderr or result.stdout)
    return result


def base_registry():
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
        "guardians": []
    }


def policy(max_per_day=3):
    return {
        "schema": "trinityaccord.guardian-active-listing-policy.v1",
        "version": "1.0.0",
        "automation_mode": "create_pr_only",
        "max_new_active_listings_per_run": 1,
        "max_new_active_listings_per_utc_day": max_per_day,
        "require_valid_self_registered_claim": True,
        "require_unique_guardian_id": True,
        "require_unique_public_key_sha256": True,
        "require_unique_source_issue": True,
        "require_unique_listing_request_issue": True
    }


def make_payload(workdir, suffix):
    out = workdir / f"guardian-application-{suffix}.final.json"
    key_dir = workdir / f"keys-{suffix}"
    run([
        "node", str(BUILDER),
        "--mode", "joint_human_ai",
        "--signing-key-holder", "ai_agent_key_holder",
        "--human-label", "Test Human",
        "--agent-label", f"Test Agent {suffix}",
        "--agent-provider", "Test Runtime",
        "--title", "Guardian Alliance Joint Human-AI Application Test",
        "--challenge", f"guardian-application-test-{suffix}",
        "--created-at", "2026-05-22T00:00:00.000Z",
        "--key-dir", str(key_dir),
        "--out", str(out),
    ])
    return out


def main():
    with tempfile.TemporaryDirectory() as raw:
        td = Path(raw)
        payload = make_payload(td, "one")

        registry = td / "guardian-registry.json"
        registry.write_text(json.dumps(base_registry(), indent=2), encoding="utf-8")

        policy_path = td / "policy.json"
        policy_path.write_text(json.dumps(policy(max_per_day=3), indent=2), encoding="utf-8")

        out_registry = td / "guardian-registry.updated.json"

        result = run([
            "python3", str(PREPARE),
            "--payload", str(payload),
            "--registry", str(registry),
            "--policy", str(policy_path),
            "--source-issue", "227",
            "--listing-request-issue", "228",
            "--label", "Test Human + Test Agent",
            "--listed-at", "2026-05-22",
            "--out-registry", str(out_registry),
            "--json",
        ])

        summary = json.loads(result.stdout)
        assert summary["ok"] is True
        assert summary["changed"] is True
        assert summary["guardian_registry_number"] == "00001"

        updated = json.loads(out_registry.read_text(encoding="utf-8"))
        assert len(updated["guardians"]) == 1
        entry = updated["guardians"][0]
        assert entry["guardian_registry_number"] == "00001"
        assert entry["status"] == "active"
        assert entry["source_issue"] == 227
        assert entry["listing_request_issue"] == 228

        verify = run([
            "python3", str(VERIFY),
            "--payload", str(payload),
            "--registry", str(out_registry),
            "--json",
        ])
        verification = json.loads(verify.stdout)
        assert verification["guardian_status"] == "active_registered_guardian"
        assert verification["guardian_registry_number"] == "00001"

        duplicate = run([
            "python3", str(PREPARE),
            "--payload", str(payload),
            "--registry", str(out_registry),
            "--policy", str(policy_path),
            "--source-issue", "227",
            "--listing-request-issue", "228",
            "--label", "Duplicate",
            "--listed-at", "2026-05-22",
            "--out-registry", str(td / "duplicate.json"),
            "--json",
        ], check=False)
        assert duplicate.returncode == 0
        assert "already_active" in duplicate.stdout

        limited_policy = td / "limited-policy.json"
        limited_policy.write_text(json.dumps(policy(max_per_day=1), indent=2), encoding="utf-8")

        payload2 = make_payload(td, "two")
        rate_limited = run([
            "python3", str(PREPARE),
            "--payload", str(payload2),
            "--registry", str(out_registry),
            "--policy", str(limited_policy),
            "--source-issue", "229",
            "--listing-request-issue", "230",
            "--label", "Second Guardian",
            "--listed-at", "2026-05-22",
            "--out-registry", str(td / "rate-limited.json"),
            "--json",
        ], check=False)
        assert rate_limited.returncode != 0
        assert "E_DAILY_LISTING_LIMIT" in rate_limited.stderr

    print("GUARDIAN_ACTIVE_LISTING_AUTOMATION_OK")


if __name__ == "__main__":
    main()
