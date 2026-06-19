#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "downloads" / "record-chain-builder.mjs"


def run(cmd, **kwargs):
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, **kwargs)


def oath(record_type="echo") -> str:
    r = run(["node", str(BUILDER), "print-oath", "--record-type", record_type])
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def base_echo_cmd(key_dir: Path, readback: str):
    return [
        "node", str(BUILDER), "echo",
        "--actor-label", "Context Honesty Test Agent",
        "--provider", "CI Test Runtime",
        "--body", "context honesty gate smoke test",
        "--context-level", "CC-3",
        "--context-sufficient-for-selected-action", "true",
        "--loaded-urls", "https://www.trinityaccord.org/api/context-load-map.json,https://www.trinityaccord.org/api/record-chain-intake-gateway.v1.json",
        "--discovery-mode", "user_task_context",
        "--requesting-party-type", "human",
        "--introducing-party-type", "human",
        "--record-decision", "human",
        "--submission-executor", "self",
        "--human-operator-involved", "false",
        "--readback", readback,
        "--key-dir", str(key_dir),
    ]


def main() -> int:
    readback = oath("echo")

    with tempfile.TemporaryDirectory() as td:
        key_dir = Path(td) / "keys"

        # Missing confirmation fails.
        out1 = Path(td) / "missing.json"
        r = run(base_echo_cmd(key_dir, readback) + ["--out", str(out1)])
        assert r.returncode != 0
        assert "Context honesty confirmation required" in (r.stderr + r.stdout)

        # Explicit false fails.
        out2 = Path(td) / "false.json"
        r = run(base_echo_cmd(key_dir, readback) + ["--context-read-confirmed", "false", "--out", str(out2)])
        assert r.returncode != 0
        assert "Context honesty confirmation required" in (r.stderr + r.stdout)

        # Bare flag fails.
        out3 = Path(td) / "bare.json"
        r = run(base_echo_cmd(key_dir, readback) + ["--context-read-confirmed", "--out", str(out3)])
        assert r.returncode != 0
        assert "--context-read-confirmed must be passed as the explicit value true" in (r.stderr + r.stdout)

        # Explicit true succeeds.
        out4 = Path(td) / "ok.json"
        r = run(base_echo_cmd(key_dir, readback) + ["--context-read-confirmed", "true", "--out", str(out4)])
        assert r.returncode == 0, r.stderr + r.stdout
        data = json.loads(out4.read_text(encoding="utf-8"))
        cr = data["record_draft"]["context_readiness"]
        assert cr["context_read_confirmed"] is True
        b = cr["context_read_confirmation_boundary"]
        assert b["self_declared_only"] is True
        assert b["does_not_prove_subjective_understanding"] is True
        assert b["false_claim_is_oath_violation"] is True
        assert b["context_map"] == "/api/context-load-map.json"

    # CC-1 does not require confirmation.
    with tempfile.TemporaryDirectory() as td:
        key_dir = Path(td) / "keys"
        out = Path(td) / "cc1.json"
        cmd = base_echo_cmd(key_dir, readback)
        i = cmd.index("--context-level") + 1
        cmd[i] = "CC-1"
        j = cmd.index("--context-sufficient-for-selected-action") + 1
        cmd[j] = "true"
        k = cmd.index("--loaded-urls") + 1
        cmd[k] = "https://www.trinityaccord.org/api/agent-first-contact.json"
        r = run(cmd + ["--out", str(out)])
        assert r.returncode == 0, r.stderr + r.stdout

    # context-requirements command.
    r = run(["node", str(BUILDER), "context-requirements", "--context-level", "CC-3"])
    assert r.returncode == 0, r.stderr + r.stdout
    text = r.stdout + r.stderr
    assert "/api/context-load-map.json" in text
    assert "CC-3" in text
    assert "--context-read-confirmed true" in text

    # link checker.
    r = run(["python3", "scripts/check_context_load_map_links.py"])
    assert r.returncode == 0, r.stderr + r.stdout

    print("PASS: builder context honesty gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
