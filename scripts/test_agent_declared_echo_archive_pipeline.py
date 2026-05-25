#!/usr/bin/env python3
"""Test: agent-declared echo archive pipeline — builder, validator, archive readiness gate, render + lint."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "gateway" / "valid-agent-declared-correction-echo.json"
VALIDATOR = ROOT / "scripts" / "validate_gateway_payload.py"
GATE = ROOT / "scripts" / "archive_readiness_gate.py"
BUILDER = ROOT / "scripts" / "build_agent_declared_echo_payload.py"
RENDERER = ROOT / "scripts" / "render_gateway_issue_body.py"
INTAKE_VALIDATOR = ROOT / "scripts" / "validate_issue_intake_body.py"

PASS = 0
FAIL = 0


def check(cond, label, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS: {label}")
    else:
        FAIL += 1
        print(f"  FAIL: {label}")
        if detail:
            print(f"        {detail}")


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))


def main():
    global PASS, FAIL

    print("=== Agent-Declared Echo Archive Pipeline Tests ===\n")

    # 1. Builder exists and is runnable
    check(BUILDER.exists(),
          "build_agent_declared_echo_payload.py exists")
    r = run([sys.executable, str(BUILDER), "--help"])
    check(r.returncode == 0,
          "build_agent_declared_echo_payload.py is runnable (--help exits 0)",
          r.stderr[:200] if r.returncode != 0 else "")

    # 2. Validator passes the positive fixture
    check(FIXTURE.exists(),
          "Positive fixture exists")
    r = run([sys.executable, str(VALIDATOR), str(FIXTURE)])
    combined = r.stdout + r.stderr
    check(r.returncode == 0,
          "validate_gateway_payload.py passes positive fixture",
          combined[:300] if r.returncode != 0 else "")

    # 3. Archive readiness gate reports archive_ready=true
    r = run([sys.executable, str(GATE), "--gateway-payload", str(FIXTURE), "--json"])
    combined = r.stdout + r.stderr
    check(r.returncode == 0,
          "archive_readiness_gate.py exits 0 for positive fixture",
          combined[:300] if r.returncode != 0 else "")
    if r.returncode == 0:
        import json
        try:
            result = json.loads(r.stdout)
            check(result.get("archive_ready") is True,
                  "archive_readiness_gate reports archive_ready=true",
                  f"got: {result.get('archive_ready')}")
        except json.JSONDecodeError:
            check(False, "archive_readiness_gate output is valid JSON",
                  r.stdout[:300])

    # 4. Production render + validate_issue_intake_body lint
    print("\n--- Production Render + Issue Intake Body Lint ---")
    check(RENDERER.exists(), "render_gateway_issue_body.py exists")
    check(INTAKE_VALIDATOR.exists(), "validate_issue_intake_body.py exists")

    if RENDERER.exists() and FIXTURE.exists():
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False, dir=str(ROOT)) as tmp:
            tmp_path = tmp.name

        # Render with --production-render and a test receipt ID
        render_r = run([
            sys.executable, str(RENDERER), str(FIXTURE),
            "--production-render",
            "--gateway-receipt-id", "gar-test-20260518T120000Z-abc123def456",
            "--gateway-commit", "testcommit",
        ])
        check(render_r.returncode == 0,
              "render_gateway_issue_body.py --production-render exits 0",
              render_r.stderr[:300] if render_r.returncode != 0 else "")

        if render_r.returncode == 0:
            rendered_body = render_r.stdout
            Path(tmp_path).write_text(rendered_body, encoding="utf-8")

            # Run validate_issue_intake_body on the rendered output
            lint_r = run([sys.executable, str(INTAKE_VALIDATOR), tmp_path])
            lint_combined = lint_r.stdout + lint_r.stderr
            check(lint_r.returncode == 0,
                  "validate_issue_intake_body.py passes rendered echo body",
                  lint_combined[:500] if lint_r.returncode != 0 else "")

            # Parse the rendered body and assert key fields
            import re
            m = re.search(r"```trinity-issue-intake\s*(.*?)```", rendered_body, re.S)
            check(m is not None, "rendered body contains trinity-issue-intake block")

            if m:
                block = m.group(1)
                # Check critical fields in the rendered block
                field_checks = {
                    "created_by_gateway: true": "created_by_gateway is true",
                    "gateway_receipt_id: gar-test-20260518T120000Z-abc123def456": "gateway_receipt_id matches",
                    "render_api_only: true": "render_api_only is true",
                    "server_validated: true": "server_validated is true",
                    "server_rendered: true": "server_rendered is true",
                    "verification_oath_present: true": "verification_oath_present is true",
                    "counts_toward_home_verifiability: false": "counts_toward_home_verifiability is false",
                    "counts_toward_home_reception: true": "counts_toward_home_reception is true",
                    "archive_ready: true": "archive_ready is true",
                    "requested_archive_kind: agent_declared_echo_archive": "requested_archive_kind is echo archive",
                    "echo_type: E5_correction_echo": "echo_type is E5_correction_echo",
                }
                for needle, label in field_checks.items():
                    check(needle in block, f"rendered block contains {label}",
                          f"looking for: {needle}")

                # Check oath hash is a valid 64-char hex
                oath_match = re.search(r"oath_text_sha256:\s*([a-f0-9]{64})", block)
                check(oath_match is not None,
                      "oath_text_sha256 is a valid 64-char hex in rendered block")

                rb_sha_match = re.search(r"agent_readback_sha256:\s*([a-f0-9]{64})", block)
                check(rb_sha_match is not None,
                      "agent_readback_sha256 is a valid 64-char hex in rendered block")

                # Check readback count >= 160
                count_match = re.search(r"agent_readback_char_count:\s*(\d+)", block)
                if count_match:
                    count = int(count_match.group(1))
                    check(count >= 160,
                          f"agent_readback_char_count >= 160 (got {count})")

        # Cleanup
        Path(tmp_path).unlink(missing_ok=True)

    print(f"\n=== Results: {PASS} passed, {FAIL} failed ===")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
