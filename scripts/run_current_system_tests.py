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

    # 1b. sitemap drift check
    result = subprocess.run(
        [sys.executable, "scripts/generate_sitemap.py", "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"sitemap drift detected:\n{result.stdout}\n{result.stderr}")
    ok("sitemap up to date")

    # 1c. active routes check
    result = subprocess.run(
        [sys.executable, "scripts/check_active_public_routes.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"active routes check failed:\n{result.stdout}\n{result.stderr}")
    ok("active public routes check")

    # 1d. public homepage status drift check
    result = subprocess.run(
        [sys.executable, "scripts/generate_public_home_status.py", "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"public homepage status drift detected:\n{result.stdout}\n{result.stderr}")
    ok("public homepage status up to date")

    # 2. record-chain-status.json marks record-chain primary
    status = load_json("api/record-chain-status.json")
    if status.get("schema") != "trinityaccord.record-chain-status.v1":
        fail("record-chain-status schema mismatch")
    text = json.dumps(status, ensure_ascii=False).lower()
    if "record-chain" not in text:
        fail("record-chain-status does not reference record-chain")
    ok("record-chain status API")

    # 2b. Public test phase disclosure
    result = subprocess.run(
        [sys.executable, "scripts/test_public_test_phase_disclosure.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"public test phase disclosure test failed: {result.stderr}\n{result.stdout}")
    ok("public test phase disclosure")

    # 2c. Phase 5C-HOTFIX regression tests
    result = subprocess.run(
        [sys.executable, "scripts/test_phase_5c_hotfix.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"Phase 5C-HOTFIX tests failed: {result.stderr}\n{result.stdout}")
    ok("Phase 5C-HOTFIX regression tests")

    # 3. gateway-v1-legacy-status.json marks historical archive only
    legacy = load_json("api/gateway-v1-legacy-status.json")
    legacy_text = json.dumps(legacy, ensure_ascii=False).lower()
    if "historical" not in legacy_text and "archive" not in legacy_text:
        fail("gateway-v1 legacy status does not mark historical/archive")
    if "backward_compatibility" in legacy_text:
        # Check it's not still promising active maintenance
        import re
        compat_match = re.search(r'"backward_compatibility"\s*:\s*"([^"]*)"', legacy_text)
        if compat_match and "not_maintained" not in compat_match.group(1):
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
    # Only flag workflows that trigger on issues AND run Gateway v1 intake/triage scripts
    GATEWAY_RUNTIME_KEYWORDS = [
        "gateway_intake", "gateway_auto_archive", "triage_echo_issue",
        "echo-triage", "guardian-registry-auto-list", "gateway-keepalive",
    ]
    workflows = ROOT / ".github" / "workflows"
    if workflows.exists():
        for p in workflows.glob("*.yml"):
            wtext = p.read_text(encoding="utf-8").lower()
            # Only check the 'on:' trigger section for issues trigger
            on_section = ""
            in_on = False
            for line in wtext.splitlines():
                stripped = line.strip()
                if stripped.startswith("on:"):
                    in_on = True
                    continue
                if in_on:
                    if stripped and not stripped.startswith("#") and not line.startswith(" ") and not line.startswith("\t"):
                        break
                    on_section += line + "\n"
            if "issues:" in on_section:
                # Check if it actually runs Gateway v1 runtime scripts
                for kw in GATEWAY_RUNTIME_KEYWORDS:
                    if kw in wtext:
                        fail(f"active Gateway issue-triggered workflow remains: {p} (matched: {kw})")
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

    # 9. Secret material scans
    result = subprocess.run(
        [sys.executable, "scripts/test_no_secret_material_committed.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"no broad secret material: {result.stderr}")
    ok("no broad secret material")

    result = subprocess.run(
        [sys.executable, "scripts/test_no_private_key_material_committed.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"no PEM private key material: {result.stderr}")
    ok("no PEM private key material")

    # 10. Phase 6A: anchor contract test
    result = subprocess.run(
        [sys.executable, "scripts/test_record_chain_anchor_contract.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"anchor contract test failed: {result.stderr}")
    ok("anchor contract test")

    # 11. Phase 6A: Arweave archive contract test
    result = subprocess.run(
        [sys.executable, "scripts/test_record_chain_arweave_archive_contract.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"arweave archive contract test failed: {result.stderr}")
    ok("arweave archive contract test")

    # 12. Phase 6A: public wording test
    result = subprocess.run(
        [sys.executable, "scripts/test_public_wording_phase6_contract.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"public wording test failed: {result.stderr}")
    ok("public wording test")

    # 13. Phase 6B: oath gate contract test
    result = subprocess.run(
        [sys.executable, "scripts/test_record_chain_oath_gate_contract.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"oath gate contract test failed: {result.stderr}\n{result.stdout}")
    ok("oath gate contract test")

    # Builder bundle contract test
    result = subprocess.run(
        [sys.executable, "scripts/test_record_chain_builder_bundle_contract.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"builder bundle contract test failed: {result.stderr}\n{result.stdout}")
    ok("builder bundle contract test")

    # Builder deep tests (canonicalJson, authorship proof, autonomy flags, etc.)
    result = subprocess.run(
        ["node", "downloads/test-record-chain-builder.mjs"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"builder deep tests failed: {result.stderr}\n{result.stdout}")
    ok("builder deep tests")

    # Phase 6B hotfix tests
    result = subprocess.run(
        [sys.executable, "scripts/test_phase6b_hotfix.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"Phase 6B hotfix tests failed: {result.stderr}\n{result.stdout}")
    ok("Phase 6B hotfix tests")

    # Phase 6B Contract Hotfix I tests
    result = subprocess.run(
        [sys.executable, "scripts/test_phase_6b_hotfix_contract.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"Phase 6B Contract Hotfix I tests failed: {result.stderr}\n{result.stdout}")
    ok("Phase 6B Contract Hotfix I tests")

    # Phase 6B: Render deploy boundary contract test
    result = subprocess.run(
        [sys.executable, "scripts/test_render_deploy_boundary_contract.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"Render deploy boundary contract test failed: {result.stderr}\n{result.stdout}")
    ok("Render deploy boundary contract test")

    # Phase 6B: Legacy isolation contract test
    result = subprocess.run(
        [sys.executable, "scripts/test_legacy_isolation_contract.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"Legacy isolation contract test failed: {result.stderr}\n{result.stdout}")
    ok("Legacy isolation contract test")

    # Phase 6B: Legacy Gateway deploy boundary contract
    result = subprocess.run(
        [sys.executable, "scripts/test_legacy_gateway_deploy_boundary_contract.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"Legacy Gateway deploy boundary test failed: {result.stderr}\n{result.stdout}")
    ok("Legacy Gateway deploy boundary contract test")

    # Phase 6B: Workflow action pinning contract
    result = subprocess.run(
        [sys.executable, "scripts/test_workflow_action_pinning_contract.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"Workflow action pinning test failed: {result.stderr}\n{result.stdout}")
    ok("Workflow action pinning contract test")

    # Phase 6B: Test registry contract
    result = subprocess.run(
        [sys.executable, "scripts/test_phase6b_test_registry_contract.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"Phase 6B test registry contract failed: {result.stderr}\n{result.stdout}")
    ok("Phase 6B test registry contract")

    # Phase 6C: Operator secret names contract
    result = subprocess.run(
        [sys.executable, "scripts/test_operator_secret_names_contract.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"Operator secret names contract failed: {result.stderr}\n{result.stdout}")
    ok("Operator secret names contract")

    # Phase 6C: Arweave live readiness contract
    result = subprocess.run(
        [sys.executable, "scripts/test_arweave_live_readiness_contract.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"Arweave live readiness contract failed: {result.stderr}\n{result.stdout}")
    ok("Arweave live readiness contract")

    # Phase 6C: Render manual deploy contract
    result = subprocess.run(
        [sys.executable, "scripts/test_render_manual_deploy_contract.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"Render manual deploy contract failed: {result.stderr}\n{result.stdout}")
    ok("Render manual deploy contract")

    # Phase 7A prelaunch contracts
    result = subprocess.run(
        [sys.executable, "scripts/test_phase7a_prelaunch_contracts.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"phase7a prelaunch contracts failed: {result.stderr}\n{result.stdout}")
    ok("phase7a prelaunch contracts")

    # 14. Phase 6: scheduled OTS watch workflow contract
    result = subprocess.run(
        [sys.executable, "scripts/test_phase6_ots_watch_workflow_contract.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"phase6 OTS watch workflow contract failed: {result.stderr}\n{result.stdout}")
    ok("phase6 OTS watch workflow contract")

    print("\n=== ALL CURRENT SYSTEM TESTS PASSED ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
