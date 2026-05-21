#!/usr/bin/env python3
"""Ensure the one-shot builder gives actionable diagnostics when agents make mistakes."""

import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "create_guardian_application.mjs"


def run_expect_fail(cmd):
    result = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode != 0, "command unexpectedly succeeded"
    try:
        payload = json.loads(result.stderr)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"stderr was not JSON: {result.stderr}") from exc
    assert payload["ok"] is False
    assert "error_code" in payload
    assert "message" in payload
    assert "next_steps" in payload
    assert payload["next_steps"], payload
    return payload


def run_expect_success(cmd):
    result = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    return json.loads(result.stdout)


def main():
    explain = run_expect_success(["node", str(BUILDER), "--explain"])
    assert explain["ok"] is True
    assert "safe_command_example" in explain
    assert "agent_declared_echo_template_pass" in json.dumps(explain)
    assert "guardian_registry_number" in json.dumps(explain)

    missing_human = run_expect_fail([
        "node", str(BUILDER),
        "--agent-label", "Test Agent",
        "--challenge", "guardian-application-test",
    ])
    assert missing_human["error_code"] == "E_MISSING_HUMAN_LABEL"
    assert "--human-label" in json.dumps(missing_human)

    bad_mode = run_expect_fail([
        "node", str(BUILDER),
        "--mode", "wrong_mode",
        "--human-label", "Test Human",
        "--agent-label", "Test Agent",
        "--challenge", "guardian-application-test",
    ])
    assert bad_mode["error_code"] == "E_UNSUPPORTED_MODE"
    assert "joint_human_ai" in json.dumps(bad_mode)

    bad_holder = run_expect_fail([
        "node", str(BUILDER),
        "--signing-key-holder", "robot",
        "--human-label", "Test Human",
        "--agent-label", "Test Agent",
        "--challenge", "guardian-application-test",
    ])
    assert bad_holder["error_code"] == "E_BAD_SIGNING_KEY_HOLDER"
    assert "ai_agent_key_holder" in json.dumps(bad_holder)
    assert "human_key_holder" in json.dumps(bad_holder)

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        key_prefix = td / "broken-key"
        (td / "broken-key.private.pem").write_text("not a real key", encoding="utf-8")
        out = td / "out.json"

        incomplete = run_expect_fail([
            "node", str(BUILDER),
            "--human-label", "Test Human",
            "--agent-label", "Test Agent",
            "--challenge", "guardian-application-test",
            "--guardian-key-prefix", str(key_prefix),
            "--key-dir", str(td),
            "--out", str(out),
        ])
        assert incomplete["error_code"] == "E_INCOMPLETE_KEYPAIR"
        assert ".public.pem" in json.dumps(incomplete)
        assert "delete the lone key file" in json.dumps(incomplete)

    print("CREATE_GUARDIAN_APPLICATION_DIAGNOSTICS_OK")


if __name__ == "__main__":
    main()
