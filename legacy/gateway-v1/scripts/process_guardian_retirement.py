#!/usr/bin/env python3
"""Process a Guardian retirement request.

Verifies the Ed25519 signature on a Guardian retirement payload,
updates the guardian registry status to 'retired', rebuilds indexes,
and commits the changes.

Usage:
    python3 scripts/process_guardian_retirement.py --payload guardian-retirement.json
    python3 scripts/process_guardian_retirement.py --issue-json /tmp/issue.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT / "scripts"))


def verify_signature(signed_message: str, signature_b64: str, public_key_pem: str) -> bool:
    """Verify Ed25519 signature using verify_guardian_signature.mjs."""
    import base64
    import tempfile

    proof = {
        "signed_message": signed_message,
        "signature_base64": signature_b64,
        "public_key_pem": public_key_pem,
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(proof, f)
        f.flush()
        proof_path = f.name

    try:
        result = subprocess.run(
            ["node", str(ROOT / "scripts" / "verify_guardian_signature.mjs"), "--proof", proof_path],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        return "GUARDIAN_SIGNATURE_OK" in result.stdout
    finally:
        Path(proof_path).unlink(missing_ok=True)


def find_guardian_in_registry(registry: dict, guardian_id: str, public_key_sha256: str) -> dict | None:
    """Find a Guardian entry by ID or public key hash."""
    for g in registry.get("guardians", []):
        if g.get("guardian_id") == guardian_id:
            return g
        if g.get("public_key_sha256") == public_key_sha256:
            return g
    return None


def process_retirement(payload: dict, dry_run: bool = False) -> dict:
    """Process a Guardian retirement request."""
    proof = payload.get("guardian_retirement_proof")
    if not proof:
        raise ValueError("Missing guardian_retirement_proof")

    guardian_id = payload.get("guardian_id") or proof.get("guardian_id")
    pub_sha = payload.get("guardian_public_key_sha256") or proof.get("public_key_sha256")
    signed_message = proof.get("signed_message")
    signature_b64 = proof.get("signature_base64")
    public_key_pem = proof.get("public_key_pem")

    if not all([guardian_id, pub_sha, signed_message, signature_b64, public_key_pem]):
        raise ValueError("Incomplete retirement proof fields")

    # Verify signature
    if not verify_signature(signed_message, signature_b64, public_key_pem):
        raise ValueError("Invalid Guardian retirement signature")

    print(f"✅ Signature verified for {guardian_id}")

    # Load registry
    registry_path = ROOT / "api" / "guardian-registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))

    guardian = find_guardian_in_registry(registry, guardian_id, pub_sha)
    if not guardian:
        raise ValueError(f"Guardian {guardian_id} not found in registry")

    current_status = guardian.get("status")
    if current_status == "retired":
        print(f"⚠️ Guardian {guardian_id} is already retired")
        return {"status": "already_retired", "guardian_id": guardian_id}

    if current_status not in ("active", "pending_review"):
        raise ValueError(f"Cannot retire Guardian with status: {current_status}")

    registry_number = guardian.get("guardian_registry_number", "unknown")
    print(f"Guardian #{registry_number} ({guardian_id}) current status: {current_status}")

    if dry_run:
        print("DRY RUN: would update status to 'retired'")
        return {"status": "dry_run", "guardian_id": guardian_id, "registry_number": registry_number}

    # Update status
    guardian["status"] = "retired"
    guardian["retired_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    guardian["retirement_reason"] = payload.get("retirement_reason", "voluntary retirement")

    # Update authority boundary
    guardian.setdefault("boundary", {})
    guardian["boundary"]["retirement_does_not_remove_historical_record"] = True

    # Write updated registry
    registry_path.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"✅ Registry updated: Guardian #{registry_number} -> retired")

    return {
        "status": "retired",
        "guardian_id": guardian_id,
        "registry_number": registry_number,
    }


def rebuild_indexes() -> None:
    """Rebuild derived indexes after registry change."""
    scripts = [
        ["python3", str(ROOT / "scripts" / "generate_public_home_status.py")],
    ]
    for cmd in scripts:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
        if result.returncode != 0:
            print(f"WARNING: {' '.join(cmd)} failed: {result.stderr}", file=sys.stderr)
        else:
            print(f"✅ {' '.join(cmd)}")


def commit_and_push(guardian_id: str, registry_number: str) -> bool:
    """Commit registry change and push."""
    # Commit registry changes first, then stash any other unstaged files
    # (e.g. toolchain-provenance.json from CI) before rebasing.
    commit_cmds = [
        ["git", "config", "user.name", "github-actions[bot]"],
        ["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"],
        ["git", "add", "api/guardian-registry.json", "api/public-home-status.json"],
        ["git", "commit", "-m", f"guardian: retire #{registry_number} ({guardian_id})"],
    ]
    for cmd in commit_cmds:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
        if result.returncode != 0:
            print(f"FAILED: {' '.join(cmd)}: {result.stderr}", file=sys.stderr)
            return False

    # Stash any remaining unstaged/untracked files before pull --rebase
    subprocess.run(["git", "stash", "--include-untracked"], capture_output=True, text=True, cwd=str(ROOT))

    push_cmds = [
        ["git", "pull", "--rebase", "-X", "theirs", "origin", "main"],
        ["git", "push", "origin", "HEAD:main"],
    ]
    for cmd in push_cmds:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
        if result.returncode != 0:
            print(f"FAILED: {' '.join(cmd)}: {result.stderr}", file=sys.stderr)
            return False

    print("✅ Committed and pushed")
    return True


def extract_retirement_from_issue(issue: dict) -> dict | None:
    """Extract retirement payload from a Gateway Issue body."""
    body = issue.get("body") or ""

    # Try 1: Look for guardian_retirement_request in the intake block
    import re
    matches = re.findall(r"```trinity-issue-intake\s*\n([\s\S]*?)```", body)
    if matches:
        block = matches[0]
        if "guardian_retirement_request: true" in block:
            # Extract the JSON payload from the issue body
            json_matches = re.findall(r"```json\s*\n([\s\S]*?)```", body)
            if json_matches:
                try:
                    return json.loads(json_matches[0])
                except json.JSONDecodeError:
                    pass

            # If no JSON block, try to construct from intake fields
            intake = {}
            for line in block.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    intake[k.strip()] = v.strip()

            if intake.get("guardian_retirement_request") == "true":
                return {
                    "guardian_id": intake.get("guardian_id"),
                    "guardian_public_key_sha256": intake.get("guardian_public_key_sha256"),
                    "guardian_registry_number": intake.get("guardian_registry_number"),
                    "retirement_reason": intake.get("retirement_reason", "voluntary retirement"),
                    "guardian_retirement_proof": {
                        "signed_message": intake.get("retirement_signed_message"),
                        "signature_base64": intake.get("retirement_signature_base64"),
                        "public_key_pem": intake.get("retirement_public_key_pem"),
                        "public_key_sha256": intake.get("guardian_public_key_sha256"),
                        "guardian_id": intake.get("guardian_id"),
                    },
                }

    # Try 2: Raw JSON payload in code block (Gateway retirement render format)
    json_matches = re.findall(r"```json\s*\n([\s\S]*?)```", body)
    if json_matches:
        try:
            payload = json.loads(json_matches[0])
            if payload.get("guardian_retirement_request") or payload.get("schema") == "trinityaccord.guardian-retirement.v1":
                return payload
        except json.JSONDecodeError:
            pass

    # Try 3: Guardian retirement request marker in body
    if "<!-- guardian-retirement-request -->" in body:
        # Extract guardian_id from table
        gid_match = re.search(r"guardian_ed25519_[a-f0-9]{16}", body)
        reason_match = re.search(r"### Statement\s*\n\s*(.+?)(?:\n|$)", body)
        return {
            "guardian_id": gid_match.group(0) if gid_match else None,
            "retirement_reason": reason_match.group(1).strip() if reason_match else "voluntary retirement",
            "guardian_retirement_request": True,
        }

    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Process Guardian retirement")
    ap.add_argument("--payload", help="Path to retirement payload JSON")
    ap.add_argument("--issue-json", help="Path to Gateway Issue JSON")
    ap.add_argument("--dry-run", action="store_true", help="Verify only, don't update registry")
    ap.add_argument("--no-push", action="store_true", help="Update registry but don't commit/push")
    args = ap.parse_args()

    if args.payload:
        payload = json.loads(Path(args.payload).read_text(encoding="utf-8"))
    elif args.issue_json:
        issue = json.loads(Path(args.issue_json).read_text(encoding="utf-8"))
        payload = extract_retirement_from_issue(issue)
        if not payload:
            print("FAIL: No retirement request found in issue", file=sys.stderr)
            return 1
    else:
        print("FAIL: --payload or --issue-json required", file=sys.stderr)
        return 1

    try:
        result = process_retirement(payload, dry_run=args.dry_run)
    except ValueError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 1

    if args.dry_run:
        print(f"\nDry run result: {json.dumps(result, indent=2)}")
        return 0

    if result["status"] == "already_retired":
        return 0

    # Rebuild indexes
    rebuild_indexes()

    # Commit and push
    if not args.no_push:
        if not commit_and_push(result["guardian_id"], result["registry_number"]):
            return 1

    print(f"\n✅ Guardian #{result['registry_number']} retired successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
