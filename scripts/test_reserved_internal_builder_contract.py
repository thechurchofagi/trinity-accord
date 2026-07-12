#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[1]
out_path = ROOT / ".tmp-reserved-rotation.json"
cmd = [sys.executable, str(ROOT / "scripts/trinity_record_builder.py"), "guardian-key-rotation", "--guardian-id", "g", "--old-public-key-sha256", "a" * 64, "--new-public-key-sha256", "b" * 64, "--out", str(out_path)]
r = subprocess.run(cmd, capture_output=True, text=True)
out = (r.stdout + r.stderr).lower()
if r.returncode == 0:
    raise AssertionError("reserved guardian-key-rotation builder command must fail")
if "reserved" not in out or "dual-signature" not in out:
    raise AssertionError(f"missing fail-closed guidance: {out}")
if out_path.exists():
    raise AssertionError("reserved builder must not create output")
doc = (ROOT / "docs/RECORD_CHAIN_PRIMARY_PATH.md").read_text(encoding="utf-8")
if "reserved, not buildable" not in doc.lower():
    raise AssertionError("operator doc must mark rotation reserved")
print("PASS: internal builder fails closed for reserved Guardian key rotation")
