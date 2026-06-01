#!/usr/bin/env python3
"""Current system test runner for Trinity Accord post-Gateway-v1 retirement.

Runs checks that verify the record-chain is the active primary system
and Gateway v1 is properly archived as historical-only.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)


def ok(msg: str) -> None:
    print(f"PASS: {msg}")


def load_json(path: str):
    p = ROOT / path
    if not p.exists():
        fail(f"missing {path}")
    return json.loads(p.read_text(encoding="utf-8"))


def require_text(path: str, needles: list[str]):
    p = ROOT / path
    if not p.exists():
        fail(f"missing {path}")
    text = p.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in text:
            fail(f"{path} missing text: {needle}")
    ok(f"{path} contains required text")


def verify_manifest():
    manifest_path = ROOT / "legacy/gateway-v1/MANIFEST.sha256.json"
    if not manifest_path.exists():
        fail("missing legacy/gateway-v1/MANIFEST.sha256.json")
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    for item in data.get("files", []):
        rel = item["path"]
        expected = item["sha256"]
        if rel.endswith("MANIFEST.sha256.json"):
            continue
        p = ROOT / rel
        if not p.exists():
            fail(f"manifest listed missing file: {rel}")
        actual = hashlib.sha256(p.read_bytes()).hexdigest()
        if actual != expected:
            fail(f"manifest hash mismatch: {rel}")
    ok("legacy gateway manifest verifies")


def main() -> int:
    # 1. record-chain verify
    result = subprocess.run(
        [sys.executable, "scripts/trinity_record_chain.py", "verify"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"record-chain verify failed: {result.stderr}")
    ok("record-chain verify")

    # 2. record-chain-status.json marks record-chain primary
    status = load_json("api/record-chain-status.json")
    if status.get("schema") != "trinityaccord.record-chain-status.v1":
        fail("record-chain-status schema mismatch")
    text = json.dumps(status, ensure_ascii=False).lower()
    if "record-chain" not in text:
        fail("record-chain-status does not reference record-chain")
    ok("record-chain status API")

    # 3. gateway-v1-legacy-status.json marks historical archive only
    legacy = load_json("api/gateway-v1-legacy-status.json")
    legacy_text = json.dumps(legacy, ensure_ascii=False).lower()
    if "historical" not in legacy_text and "archive" not in legacy_text:
        fail("gateway-v1 legacy status does not mark historical/archive")
    if "backward_compatibility" in legacy_text and "maintained" in legacy_text:
        fail("gateway-v1 status still promises backward compatibility")
    ok("gateway v1 historical status API")

    # 4. Homepage points to record-chain
    require_text("index.md", ["record-chain", "trinity_record_builder.py", "trinity_record_chain.py"])

    # 5. Agent entry pages point to record-chain
    for candidate in ["agent-first-contact.md", "agent-first-contact/index.md"]:
        if (ROOT / candidate).exists():
            require_text(candidate, ["record-chain"])
            break

    for candidate in ["agent-start.md", "agent-start/index.md"]:
        if (ROOT / candidate).exists():
            require_text(candidate, ["record-chain"])
            break

    # 6. No active Gateway issue-triggered workflows
    workflows = ROOT / ".github" / "workflows"
    if workflows.exists():
        for p in workflows.glob("*.yml"):
            wtext = p.read_text(encoding="utf-8").lower()
            if "issues:" in wtext and (
                "gateway" in wtext
                or "triage" in wtext
                or "guardian-registry-auto-list" in p.name
            ):
                fail(f"active Gateway issue-triggered workflow remains: {p}")
    ok("no active Gateway issue-triggered workflows")

    # 7. legacy/gateway-v1/MANIFEST.sha256.json exists
    verify_manifest()

    # 8. record-chain-copy-paste-examples exist and JSON examples are valid
    examples = ROOT / "record-chain-copy-paste-examples"
    if not examples.exists():
        fail("missing record-chain-copy-paste-examples")
    json_examples = list(examples.glob("*.json"))
    if not json_examples:
        fail("no record-chain JSON examples")
    for p in json_examples:
        json.loads(p.read_text(encoding="utf-8"))
    ok("record-chain examples JSON-valid")

    # 9. No private keys or tokens
    result = subprocess.run(
        [sys.executable, "scripts/test_no_private_key_or_token_leakage.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"no-secrets check failed: {result.stderr}")
    ok("no private keys or tokens")

    print("\n=== ALL CURRENT SYSTEM TESTS PASSED ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
