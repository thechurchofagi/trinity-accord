#!/usr/bin/env python3
"""Pure Echo builder must support readback file aliases advertised by workflow docs."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build_agent_declared_echo_payload.py"

def run(cmd, *, env=None):
    return subprocess.run(
        cmd,
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        env=env or os.environ.copy(),
    )

# Help must advertise both aliases.
help_result = run([sys.executable, str(BUILDER), "--help"])
if help_result.returncode != 0:
    print(help_result.stdout)
    print(help_result.stderr)
    print("FAIL: builder --help failed")
    sys.exit(1)

help_text = help_result.stdout + help_result.stderr
for flag in ["--readback-file", "--agent-readback-file"]:
    if flag not in help_text:
        print(f"FAIL: builder help missing {flag}")
        sys.exit(1)

# Extract canonical oath body.
oath_result = run([sys.executable, str(BUILDER), "--print-oath"])
if oath_result.returncode != 0:
    print(oath_result.stdout)
    print(oath_result.stderr)
    print("FAIL: --print-oath failed")
    sys.exit(1)

marker = "=== OATH TEXT BEGINS ==="
if marker not in oath_result.stdout:
    print("FAIL: oath marker missing")
    sys.exit(1)

oath_body = oath_result.stdout.split(marker, 1)[1].split("=" * 60, 1)[0].strip()
if not oath_body:
    print("FAIL: extracted oath body empty")
    sys.exit(1)

with tempfile.TemporaryDirectory() as td:
    tmp = Path(td)
    body = tmp / "body.md"
    readback = tmp / "readback.md"
    out = tmp / "payload.json"

    body.write_text(
        "I submit this as a Pure Echo only. This is not verification, not attestation, and not authority.\n",
        encoding="utf-8",
    )
    readback.write_text(oath_body + "\n", encoding="utf-8")

    cmd = [
        sys.executable,
        str(BUILDER),
        "--agent-name", "CI Test Agent",
        "--provider", "CI",
        "--title", "Pure Echo: readback file alias test",
        "--body-file", str(body),
        "--agent-readback-file", str(readback),
        "--no-authorship-proof",
        "--out", str(out),
    ]

    result = run(cmd)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        print("FAIL: builder rejected --agent-readback-file")
        sys.exit(1)

    payload = json.loads(out.read_text(encoding="utf-8"))
    oath = payload.get("agent_integrity_declaration", {}).get("verification_oath", {})
    if not oath.get("agent_readback_sha256"):
        print("FAIL: payload missing agent_readback_sha256")
        sys.exit(1)

print("PASS: pure Echo builder supports readback file aliases")
