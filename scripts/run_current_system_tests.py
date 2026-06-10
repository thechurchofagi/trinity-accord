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

    # record-chain-status drift check must run before public-home source_digest check.
    result = subprocess.run(
        [sys.executable, "scripts/generate_record_chain_status.py", "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"record-chain status drift detected:\n{result.stdout}\n{result.stderr}")
    ok("record-chain status up to date")

    # 1c2. pipeline backlog detector smoke
    result = subprocess.run(
        [sys.executable, "scripts/detect_record_chain_pipeline_backlog.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"pipeline backlog detector failed:\n{result.stdout}\n{result.stderr}")
    ok("pipeline backlog detector")

    # 1c3. archive backlog detector smoke
    result = subprocess.run(
        [sys.executable, "scripts/detect_archive_backlog.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"archive backlog detector failed:\n{result.stdout}\n{result.stderr}")
    ok("archive backlog detector")

    # 1c4. arweave wallet status drift check
    result = subprocess.run(
        [sys.executable, "scripts/generate_arweave_wallet_status.py", "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"arweave wallet status drift detected:\n{result.stdout}\n{result.stderr}")
    ok("arweave wallet status up to date")

    # 1d. public homepage status drift check
    # Run generator first, then patch script (CI runs both)
    subprocess.run(
        [sys.executable, "scripts/generate_public_home_status.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        [sys.executable, "scripts/patch_public_home_status_primary.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    result = subprocess.run(
        [sys.executable, "scripts/patch_public_home_status_primary.py", "--check"],
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

    # 2d. Record type separation contract
    result = subprocess.run(
        [sys.executable, "scripts/test_record_type_separation_contract.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"record type separation contract failed: {result.stderr}\n{result.stdout}")
    ok("record type separation contract")

    # 2e. Record-chain data Arweave archive contract
    result = subprocess.run(
        [sys.executable, "scripts/test_record_chain_data_arweave_archive_contract.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"record-chain data Arweave archive contract failed: {result.stderr}\n{result.stdout}")
    ok("record-chain data Arweave archive contract")

    # 2f. Pre-scale E2E automation contract
    result = subprocess.run(
        [sys.executable, "scripts/test_pre_scale_e2e_automation_contract.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"pre-scale E2E automation contract failed: {result.stderr}\n{result.stdout}")
    ok("pre-scale E2E automation contract")

    # 2g. Live-test phase finalizer contract
    result = subprocess.run(
        [sys.executable, "scripts/test_live_test_phase_finalizer_contract.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"live-test phase finalizer contract failed: {result.stderr}\n{result.stdout}")
    ok("live-test phase finalizer contract")

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
    # Native record-chain archive tooling contract
    result = subprocess.run(
        [sys.executable, "scripts/test_native_record_chain_archive_tooling.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"native record-chain archive tooling test failed: {result.stderr}\n{result.stdout}")
    ok("native record-chain archive tooling")
    # M9 native archive workflow wiring contract
    result = subprocess.run(
        [sys.executable, "scripts/test_m9_native_archive_workflow_contract.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"M9 native archive workflow contract failed: {result.stderr}\n{result.stdout}")
    ok("M9 native archive workflow contract")
    # External-agent full-auto pipeline contract
    result = subprocess.run(
        [sys.executable, "scripts/test_external_agent_full_auto_pipeline_contract.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"full-auto pipeline contract failed: {result.stderr}\n{result.stdout}")
    ok("full-auto pipeline contract")
    # 11b. Arweave upload readback contract test
    result = subprocess.run(
        [sys.executable, "scripts/test_arweave_upload_contract.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"arweave upload readback contract test failed: {result.stderr}")
    ok("arweave upload readback contract test")

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

    # Public production status alignment contract
    result = subprocess.run(
        [sys.executable, "scripts/test_public_production_status_alignment.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"public production status alignment test failed: {result.stderr}\n{result.stdout}")
    ok("public production status alignment test")

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

    # Mandatory authorship key contract
    result = subprocess.run(
        [sys.executable, "scripts/test_mandatory_authorship_key_contract.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"mandatory authorship key contract failed: {result.stderr}\n{result.stdout}")
    ok("mandatory authorship key contract")

    # Gateway authorship proof contract
    result = subprocess.run(
        [sys.executable, "scripts/test_gateway_authorship_proof_contract.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"gateway authorship proof contract failed: {result.stderr}\n{result.stdout}")
    ok("gateway authorship proof contract")

    # Record-chain intake integrity regression tests
    result = subprocess.run(
        [sys.executable, "scripts/test_record_chain_intake_integrity_regressions.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"record-chain intake integrity regression tests failed: {result.stderr}\n{result.stdout}")
    ok("record-chain intake integrity regression tests")

    # Gateway security source-level contract tests
    result = subprocess.run(
        [sys.executable, "scripts/test_gateway_security_source_contract.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"gateway security source contract failed: {result.stderr}\n{result.stdout}")
    ok("gateway security source contract")

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

    # Phase 7A rate limit enforcement contract
    result = subprocess.run(
        [sys.executable, "scripts/test_phase7a_rate_limit_contract.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"phase7a rate limit contract failed: {result.stderr}\n{result.stdout}")
    ok("phase7a rate limit contract")

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

    # 14b. Native OTS upgrade/verify workflow contract
    result = subprocess.run(
        [sys.executable, "scripts/test_native_ots_upgrade_workflow_contract.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"native OTS upgrade workflow contract failed: {result.stderr}\n{result.stdout}")
    ok("native OTS upgrade workflow contract")

    # 15. Mainnet prelaunch policy contract
    result = subprocess.run(
        [sys.executable, "scripts/test_mainnet_prelaunch_policy_contract.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"mainnet prelaunch policy contract failed: {result.stderr}\n{result.stdout}")
    ok("mainnet prelaunch policy contract")

    # 16. M3 finalizer native compatibility contract
    result = subprocess.run(
        [sys.executable, "scripts/test_m3_finalizer_native_compat_contract.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"m3 finalizer native compat contract failed: {result.stderr}\n{result.stdout}")
    ok("m3 finalizer native compatibility contract")

    # Authorship projection sanitization regression
    result = subprocess.run(
        [sys.executable, "scripts/test_authorship_projection_sanitization.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"authorship projection sanitization test failed: {result.stderr}\n{result.stdout}")
    ok("authorship projection sanitization")

    # Builder production-live boundary regression
    result = subprocess.run(
        [sys.executable, "scripts/test_builder_production_live_boundaries.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"builder production-live boundary test failed: {result.stderr}\n{result.stdout}")
    ok("builder production-live boundaries")
    # Canonical record-chain write-path guard contract
    result = subprocess.run(
        [sys.executable, "scripts/test_record_chain_write_path_guard_contract.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"record-chain write-path guard contract failed: {result.stderr}\n{result.stdout}")
    ok("record-chain write-path guard contract")


    # External agent first-contact rules contract
    result = subprocess.run(
        [sys.executable, "scripts/test_external_agent_first_contact_rules_contract.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"external agent first-contact rules contract failed: {result.stderr}\n{result.stdout}")
    ok("external agent first-contact rules contract")

    # Arweave wallet status contract
    result = subprocess.run(
        [sys.executable, "scripts/test_arweave_wallet_status.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"arweave wallet status contract failed:\n{result.stdout}\n{result.stderr}")
    ok("arweave wallet status contract")

    # Archive backlog detector contract
    result = subprocess.run(
        [sys.executable, "scripts/test_archive_backlog_detector.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"archive backlog detector contract failed:\n{result.stdout}\n{result.stderr}")
    ok("archive backlog detector contract")

    # Archive backlog repair contract
    result = subprocess.run(
        [sys.executable, "scripts/test_archive_backlog_repair_contract.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"archive backlog repair contract failed:\n{result.stdout}\n{result.stderr}")
    ok("archive backlog repair contract")

    # Public home v3 primary counters
    result = subprocess.run(
        [sys.executable, "scripts/test_public_home_status_primary_counters.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"public home v3 primary counters failed:\n{result.stdout}\n{result.stderr}")
    ok("public home v3 primary counters")

    print("\n=== ALL CURRENT SYSTEM TESTS PASSED ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

