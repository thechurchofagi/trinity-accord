#!/usr/bin/env python3
"""Sub-V6 Level Selection Guardrails — Comprehensive E2E Test.

Covers: static checks, builder, validator, renderer, keyword negation,
structured overclaim rejection, wrong-path rejection, and grep audits.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build_agent_declared_archive_payload.py"
VALIDATOR = ROOT / "scripts" / "validate_gateway_payload.py"
RENDERER = ROOT / "scripts" / "render_gateway_issue_body.py"

passed = 0
failed = 0
skipped = 0
results = []


def run(cmd, **kwargs):
    return subprocess.run(cmd, text=True, capture_output=True, timeout=60, cwd=str(ROOT), **kwargs)


def check(label, condition, detail=""):
    global passed, failed, results
    if condition:
        passed += 1
        results.append(f"  PASS: {label}")
        print(f"  PASS: {label}")
    else:
        failed += 1
        msg = f"  FAIL: {label}"
        if detail:
            msg += f" — {detail}"
        results.append(msg)
        print(msg)


def skip(label, reason):
    global skipped, results
    skipped += 1
    results.append(f"  SKIP: {label} — {reason}")
    print(f"  SKIP: {label} — {reason}")


# === 3. Static File Presence Check ===
def test_static_files():
    print("\n=== 3. Static File Presence Check ===")
    required = [
        "api/agent-issue-gateway-payload-schema.v1.json",
        "api/agent-submit-gateway.json",
        "scripts/sub_v6_level_guardrails.py",
        "scripts/build_agent_declared_archive_payload.py",
        "scripts/validate_gateway_payload.py",
        "scripts/render_gateway_issue_body.py",
        "examples/github-app-backend/server.js",
    ]
    for f in required:
        check(f"File exists: {f}", (ROOT / f).exists())


# === 4. Regression Test Suite ===
def test_regression():
    print("\n=== 4. Regression Test Suite ===")

    new_tests = [
        "test_sub_v6_level_guardrails_schema.py",
        "test_sub_v6_level_selection_guardrails.py",
        "test_sub_v6_warning_only_lint.py",
        "test_sub_v6_renderer_warning_fields.py",
        "test_sub_v6_no_keyword_hard_fail.py",
    ]
    for t in new_tests:
        p = ROOT / "scripts" / t
        if not p.exists():
            skip(t, "file not found")
            continue
        r = run([sys.executable, str(p)])
        check(f"{t}", r.returncode == 0, r.stdout[-200:] if r.returncode != 0 else "")

    old_tests = [
        "test_build_agent_declared_archive_payload.py",
        "test_validate_gateway_payload_agent_declared.py",
        "test_gateway_agent_declared_payload_schema.py",
        "test_agent_declared_issue_body_schema.py",
        "test_agent_declared_issue_body_schema_negative.py",
        "test_v0_v5_entrypoint_consistency.py",
        "test_sub_v6_single_mandatory_route_contract.py",
        "test_sub_v6_docs_single_route.py",
        "test_full_path_agent_bugfixes.py",
    ]
    for t in old_tests:
        p = ROOT / "scripts" / t
        if not p.exists():
            skip(t, "file not found")
            continue
        r = run([sys.executable, str(p)])
        check(f"{t}", r.returncode == 0, r.stdout[-200:] if r.returncode != 0 else "")

    boundary_tests = [
        "test_public_prompt_boundary.py",
        "test_public_surface_consistency.py",
        "test_no_core_instruction_public_api.py",
    ]
    for t in boundary_tests:
        p = ROOT / "scripts" / t
        if not p.exists():
            skip(t, "file not found")
            continue
        r = run([sys.executable, str(p)])
        check(f"{t}", r.returncode == 0, r.stdout[-100:] if r.returncode != 0 else "")


# === 5. Schema Guardrail Test ===
def test_schema_guardrails():
    print("\n=== 5. Schema Guardrail Test ===")
    schema_path = ROOT / "api" / "agent-issue-gateway-payload-schema.v1.json"
    schema_text = schema_path.read_text()
    check("level_selection_acknowledgement in schema", '"level_selection_acknowledgement"' in schema_text)
    check("high_level_confirmation in schema", '"high_level_confirmation"' in schema_text)
    check("sub_v6_level_selection_lint in schema", '"sub_v6_level_selection_lint"' in schema_text)
    check("additionalProperties false still present", '"additionalProperties": false' in schema_text)


# === 6. Builder E2E — Thin V5 ===
def test_builder_thin_v5():
    print("\n=== 6. Builder E2E — Thin V5 Payload ===")
    out = Path(tempfile.mktemp(suffix=".json"))
    r = run([
        sys.executable, str(BUILDER),
        "--agent-name", "Guardrail E2E Test Agent",
        "--provider", "Manual E2E",
        "--declared-level", "V5",
        "--reception-initiation-class", "externally_seeded",
        "--reception-initiation-basis", "external_url_only",
        "--what-checked", "Read public homepage only",
        "--limitation", "Evidence requirements are waived for V0-V5.",
        "--no-authorship-proof",
        "--out", str(out),
    ])
    check("Thin V5 builder exits 0", r.returncode == 0, r.stderr[-200:] if r.returncode != 0 else "")

    if r.returncode == 0:
        check("Builder prints 'High sub-V6 template level selected'", "High sub-V6 template level selected" in r.stdout)
        check("Builder prints 'V0–V5 are oath-bound'", "V0–V5 are oath-bound" in r.stdout)

        payload = json.loads(out.read_text())

        ack = payload.get("level_selection_acknowledgement", {})
        check("level_selection_acknowledgement present", bool(ack))
        check("understands_self_declared_template_level == True", ack.get("understands_self_declared_template_level") is True)
        check("understands_evidence_waived_for_v0_v5 == True", ack.get("understands_evidence_waived_for_v0_v5") is True)
        check("understands_not_strict_evidence_verification == True", ack.get("understands_not_strict_evidence_verification") is True)

        high = payload.get("high_level_confirmation", {})
        check("high_level_confirmation.required == True", high.get("required") is True)
        check("agent_confirmed_high_level_self_selection == True", high.get("agent_confirmed_high_level_self_selection") is True)

        lint = payload.get("sub_v6_level_selection_lint", {})
        check("lint.mode == warning_only", lint.get("mode") == "warning_only")
        check("lint.warnings_block_archive == False", lint.get("warnings_block_archive") is False)
        check("lint.warnings length >= 1", len(lint.get("warnings", [])) >= 1)

    return out if r.returncode == 0 else None


# === 7. Local Validator E2E ===
def test_validator_thin_v5(payload_path):
    print("\n=== 7. Local Validator E2E — Warning Must Not Block ===")
    if not payload_path:
        skip("Validator thin V5", "no payload from builder")
        return None

    r = run([sys.executable, str(VALIDATOR), str(payload_path)])
    check("Validator exits 0 for thin V5", r.returncode == 0, r.stdout[-200:] if r.returncode != 0 else "")
    check("Output contains 'PASS WITH WARNINGS'", "PASS WITH WARNINGS" in r.stdout)
    check("Output contains 'WARN:'", "WARN:" in r.stdout)
    check("Output contains 'Warnings do not block'", "Warnings do not block" in r.stdout)
    return r.stdout


# === 8. Local Renderer E2E ===
def test_renderer_thin_v5(payload_path):
    print("\n=== 8. Local Renderer E2E — Issue Body Guardrails ===")
    if not payload_path:
        skip("Renderer thin V5", "no payload from builder")
        return

    r = run([
        sys.executable, str(RENDERER), str(payload_path),
        "--production-render",
        "--gateway-receipt-id", "gar-e2e-test-20260519T194800-abcdef1234567890",
        "--gateway-commit", "localtest",
        "--gateway-service", "trinity-agent-issue-gateway",
    ])
    check("Renderer exits 0", r.returncode == 0, r.stderr[-200:] if r.returncode != 0 else "")

    if r.returncode == 0:
        body = r.stdout
        check("sub_v6_level_selection: present", "sub_v6_level_selection:" in body)
        check("declared_template_level: V5", "declared_template_level: V5" in body)
        check("evidence_waived_for_v0_v5: true", "evidence_waived_for_v0_v5: true" in body)
        check("strict_evidence_level_claimed: false", "strict_evidence_level_claimed: false" in body)
        check("warnings_are_non_blocking: true", "warnings_are_non_blocking: true" in body)
        check("warning_count present", "warning_count:" in body)
        check("sub_v6_level_selection_warnings: present", "sub_v6_level_selection_warnings:" in body)
        check("agent-declared template level label", "agent-declared template level, not strict evidence level" in body)


# === 11. Negated Keyword Test ===
def test_negated_keywords():
    print("\n=== 11. Negated Boundary Keywords — Must Not Fail ===")
    out = Path(tempfile.mktemp(suffix=".json"))
    r = run([
        sys.executable, str(BUILDER),
        "--agent-name", "Keyword Negation Test Agent",
        "--provider", "Manual E2E",
        "--declared-level", "V3",
        "--reception-initiation-class", "externally_seeded",
        "--reception-initiation-basis", "external_url_only",
        "--what-checked", "Confirmed this is not authority",
        "--what-checked", "Confirmed this is not formal attestation",
        "--what-checked", "Confirmed this is not successor reception",
        "--what-checked", "Computed sha256 hash digest for local text comparison",
        "--limitation", "Not strict evidence verification.",
        "--no-authorship-proof",
        "--out", str(out),
    ])
    check("Negated keyword builder exits 0", r.returncode == 0)

    if r.returncode == 0:
        r2 = run([sys.executable, str(VALIDATOR), str(out)])
        check("Negated keyword validator does not fail", r2.returncode == 0,
              r2.stdout[-200:] if r2.returncode != 0 else "")
        check("No FAIL due to keywords", "FAIL" not in r2.stdout or "PASS" in r2.stdout)


# === 12. Structured Overclaim Test ===
def test_structured_overclaim():
    print("\n=== 12. Structured Overclaim — Must Still Fail ===")
    # Build a valid V5 first
    out = Path(tempfile.mktemp(suffix=".json"))
    r = run([
        sys.executable, str(BUILDER),
        "--agent-name", "Overclaim Test Agent",
        "--provider", "Manual E2E",
        "--declared-level", "V5",
        "--reception-initiation-class", "externally_seeded",
        "--reception-initiation-basis", "external_url_only",
        "--what-checked", "Reviewed scripts/check_consistency.py",
        "--what-checked", "Computed sha256 hash digest",
        "--what-checked", "Reviewed broad public digital mirror references Bitcoin Arweave IPFS ETH Chronicle",
        "--limitation", "Evidence waived for V0-V5.",
        "--no-authorship-proof",
        "--out", str(out),
    ])
    if r.returncode != 0:
        skip("Structured overclaim", "builder failed")
        return

    # Mutate: set attestation_claim.system_certified = True
    payload = json.loads(out.read_text())
    payload.setdefault("claim_classification", {})
    payload["claim_classification"].setdefault("attestation_claim", {})
    payload["claim_classification"]["attestation_claim"]["claimed"] = False
    payload["claim_classification"]["attestation_claim"]["basis"] = "none"
    payload["claim_classification"]["attestation_claim"]["system_certified"] = True
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    r2 = run([sys.executable, str(VALIDATOR), str(out)])
    check("Structured overclaim validator fails", r2.returncode != 0)
    check("FAIL output contains system_certified", "system_certified" in r2.stdout)


# === 13. V0-V5 Wrong Path Test ===
def test_wrong_path():
    print("\n=== 13. V0-V5 Wrong Path Guard ===")
    out = Path(tempfile.mktemp(suffix=".json"))
    r = run([
        sys.executable, str(BUILDER),
        "--agent-name", "Wrong Path Test Agent",
        "--provider", "Manual E2E",
        "--declared-level", "V5",
        "--reception-initiation-class", "externally_seeded",
        "--reception-initiation-basis", "external_url_only",
        "--what-checked", "Reviewed scripts",
        "--limitation", "Evidence waived.",
        "--no-authorship-proof",
        "--out", str(out),
    ])
    if r.returncode != 0:
        skip("Wrong path", "builder failed")
        return

    # Mutate to wrong path
    payload = json.loads(out.read_text())
    payload["requested_archive_kind"] = "verification_report_archive"
    payload["evidence_requirement_mode"] = "strict"
    payload["claim_gate"]["mode"] = "strict_evidence"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    r2 = run([sys.executable, str(VALIDATOR), str(out)])
    check("Wrong path validator fails", r2.returncode != 0)
    check("FAIL output mentions wrong path", "WRONG" in r2.stdout or "wrong" in r2.stdout.lower() or "forbidden" in r2.stdout.lower())


# === 16. Grep Audit ===
def test_grep_audit():
    print("\n=== 16. Grep Audit ===")

    # Check for keyword hard-fail (unacceptable)
    r = run(["grep", "-R", "formal attestation.*FAIL", "-n",
             "scripts/validate_gateway_payload.py"], check=False)
    # Filter out structured-field checks
    bad_hits = [l for l in r.stdout.splitlines() if "system_certified" not in l and "claim_classification" not in l]
    check("No keyword-only hard-fail for 'formal attestation'", len(bad_hits) == 0,
          str(bad_hits) if bad_hits else "")

    # Check warning-only language exists
    r2 = run(["grep", "-R", "Warnings do not block V0", "-n", "scripts/"], check=False)
    check("Warning-only language in scripts", bool(r2.stdout.strip()))

    # Check level_selection_warnings in server.js
    r3 = run(["grep", "-R", "level_selection_warnings", "-n", "examples/"], check=False)
    check("level_selection_warnings in server.js", bool(r3.stdout.strip()))


# === Main ===
def main():
    print("=" * 60)
    print("Sub-V6 Level Selection Guardrails — Comprehensive E2E")
    print("=" * 60)

    test_static_files()
    test_regression()
    test_schema_guardrails()
    payload_path = test_builder_thin_v5()
    test_validator_thin_v5(payload_path)
    test_renderer_thin_v5(payload_path)
    test_negated_keywords()
    test_structured_overclaim()
    test_wrong_path()
    test_grep_audit()

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed, {skipped} skipped")
    print("=" * 60)

    if failed:
        print("\nFAILED tests:")
        for r in results:
            if r.strip().startswith("FAIL"):
                print(r)
        sys.exit(1)

    print("\nAll tests passed.")


if __name__ == "__main__":
    main()
