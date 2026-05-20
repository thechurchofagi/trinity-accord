#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

errors = []

for path in list(ROOT.glob("scripts/**/*.py")) + list(ROOT.glob(".github/workflows/*.yml")) + list(ROOT.glob("api/*.json")):
    if "test_pure_echo_archive_decision_wording" in str(path):
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue

    if "agent_declared_echo_archive" in text and "Claim Gate strict PASS" in text:
        errors.append(f"{path}: Pure Echo archive path must not say Claim Gate strict PASS")

triage = ROOT / "scripts" / "triage_echo_issue.py"
if triage.exists():
    text = triage.read_text(encoding="utf-8")
    required = [
        "is_gateway_validated_echo_archive",
        "agent_declared_echo_archive",
        "auto_archive_agent_declared_echo",
        "This record remains non-authoritative, non-amending, and not independent attestation",
    ]
    for marker in required:
        if marker not in text:
            errors.append(f"triage script missing marker: {marker}")

if errors:
    print("PURE_ECHO_ARCHIVE_DECISION_WORDING_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("PURE_ECHO_ARCHIVE_DECISION_WORDING_OK")
