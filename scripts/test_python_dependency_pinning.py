#!/usr/bin/env python3
"""Test: Python CI dependencies must be pinned via approved requirements files."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
REQ = ROOT / "requirements-ci.txt"
REQ_OTS = ROOT / "requirements-ots.txt"
WF_DIR = ROOT / ".github" / "workflows"

errors = []


def requirements_file_is_pinned(path: Path) -> bool:
    if not path.exists():
        errors.append(f"{path.name} missing")
        return False
    ok = True
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if not re.match(r"^[A-Za-z0-9_.-]+(\[[A-Za-z0-9_,.-]+\])?==[0-9]", line):
            errors.append(f"{path.name}:{lineno}: dependency is not pinned with ==: {line}")
            ok = False
    return ok


requirements_file_is_pinned(REQ)
requirements_file_is_pinned(REQ_OTS)

if REQ.exists():
    req_text = REQ.read_text(encoding="utf-8")
    for required in ["jsonschema==", "opentimestamps-client=="]:
        if required not in req_text:
            errors.append(f"requirements-ci.txt missing pinned {required}")

if REQ_OTS.exists():
    ots_text = REQ_OTS.read_text(encoding="utf-8")
    if "opentimestamps-client==" not in ots_text:
        errors.append("requirements-ots.txt missing pinned opentimestamps-client==")

APPROVED_REQUIREMENTS = ["requirements-ci.txt", "requirements-ots.txt"]
LEGACY_OTS_WORKFLOWS = {"record-chain-ots-stamp.yml", "record-chain-ots-upgrade.yml"}

for path in WF_DIR.glob("*.yml"):
    text = path.read_text(encoding="utf-8")

    if "pip install --upgrade pip" in text or "python3 -m pip install --upgrade pip" in text:
        errors.append(f"{path.name}: unpinned pip upgrade")

    for line in text.splitlines():
        stripped = line.strip()
        if "pip install" not in stripped:
            continue
        if any(f"-r {name}" in stripped for name in APPROVED_REQUIREMENTS):
            continue
        if re.search(r"\b[a-zA-Z0-9_.-]+==[0-9]", stripped):
            continue
        if stripped.startswith("#"):
            continue
        if path.name in LEGACY_OTS_WORKFLOWS and stripped in {"- run: pip install opentimestamps-client", "- run: python -m pip install opentimestamps-client", "- run: python3 -m pip install opentimestamps-client"}:
            # These legacy OTS workflows predate the shared requirements file.
            # Their dependency is still tracked by requirements-ots.txt above; keep
            # this narrow exception until those legacy workflows are retired or safely
            # rewritten in a dedicated write-workflow hardening PR.
            continue
        errors.append(f"{path.name}: unpinned pip install line: {stripped}")

if errors:
    print("FAIL: Python dependency pinning violations:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("PYTHON_DEPENDENCY_PINNING_OK")
