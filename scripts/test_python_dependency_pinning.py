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
    for required in ["jsonschema==", "opentimestamps-client==", "PyYAML==", "cryptography==", "pytest=="]:
        if required not in req_text:
            errors.append(f"requirements-ci.txt missing pinned {required}")

if REQ_OTS.exists():
    ots_text = REQ_OTS.read_text(encoding="utf-8")
    if "opentimestamps-client==" not in ots_text:
        errors.append("requirements-ots.txt missing pinned opentimestamps-client==")

APPROVED_REQUIREMENTS = ["requirements-ci.txt", "requirements-ots.txt"]
LEGACY_OTS_WORKFLOWS = {"record-chain-ots-stamp.yml", "record-chain-ots-upgrade.yml"}
LEGACY_OTS_DIRECT_INSTALL_LINES = {
    "- run: pip install opentimestamps-client",
    "- run: python -m pip install opentimestamps-client",
    "- run: python3 -m pip install opentimestamps-client",
    "pip install opentimestamps-client",
    "python -m pip install opentimestamps-client",
    "python3 -m pip install opentimestamps-client",
}

# Narrow legacy exceptions. These older/manual workflows still use direct install
# lines, but every package listed here is pinned in requirements-ci.txt above.
# Do not add new entries here for active/current workflows; rewrite new workflows
# to use -r requirements-ci.txt or -r requirements-ots.txt instead.
LEGACY_DIRECT_INSTALL_EXCEPTIONS = {
    "pre-scale-e2e-orchestrator-v2.yml": {
        "pip install opentimestamps-client cryptography pytest jsonschema PyYAML",
    },
    "fix-sitemap-drift.yml": {
        "- run: pip install pyyaml",
        "pip install pyyaml",
    },
}

for path in WF_DIR.glob("*.yml"):
    text = path.read_text(encoding="utf-8")

    for lineno, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if "pip install --upgrade pip" in stripped or "python3 -m pip install --upgrade pip" in stripped:
            errors.append(f"{path.name}:{lineno}: unpinned pip upgrade")
            continue

        if "pip install" not in stripped:
            continue
        if any(f"-r {name}" in stripped for name in APPROVED_REQUIREMENTS):
            continue
        if re.search(r"\b[a-zA-Z0-9_.-]+==[0-9]", stripped):
            continue
        if path.name in LEGACY_OTS_WORKFLOWS and stripped in LEGACY_OTS_DIRECT_INSTALL_LINES:
            # These legacy OTS workflows predate the shared requirements file.
            # Their dependency is still tracked by requirements-ots.txt above; keep
            # this narrow exception until those legacy workflows are retired or safely
            # rewritten in a dedicated write-workflow hardening PR.
            continue
        if stripped in LEGACY_DIRECT_INSTALL_EXCEPTIONS.get(path.name, set()):
            continue
        errors.append(f"{path.name}:{lineno}: unpinned pip install line: {stripped}")

if errors:
    print("FAIL: Python dependency pinning violations:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("PYTHON_DEPENDENCY_PINNING_OK")
