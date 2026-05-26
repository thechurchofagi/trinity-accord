#!/usr/bin/env python3
"""
Test that protocol_terms.json is the single source of truth for all enums.

Checks:
1. echo-record-schema.v3.json verification_level enum matches PROTOCOL_LEVELS
2. echo-record-schema.v3.json verification_scope_label enum matches VALID_SCOPE_LABELS
3. validate_agent_submission.py does NOT define conflicting local enums
4. claim_gate.py component levels match protocol_terms
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Load protocol terms (the authority)
sys.path.insert(0, str(ROOT / "scripts"))
from protocol_terms import (
    PROTOCOL_LEVELS, B_LEVELS, D_LEVELS, T_LEVELS, C_LEVELS, N_LEVELS, P_LEVELS,
    VALID_RECORD_KINDS, VALID_SCOPE_LABELS, VALID_ARCHIVE_STATUSES, VALID_INDEPENDENCE_CLASSES,
)

PASS_COUNT = 0
FAIL_COUNT = 0

def check(condition, label, detail=""):
    global PASS_COUNT, FAIL_COUNT
    if condition:
        print(f"  PASS: {label}")
        PASS_COUNT += 1
    else:
        print(f"  FAIL: {label}")
        if detail:
            print(f"        {detail}")
        FAIL_COUNT += 1


def test_echo_schema_verification_level():
    """echo-record-schema.v3.json verification_level enum must match PROTOCOL_LEVELS (plus 'none')."""
    print("\n--- Test: echo-record-schema.v3.json verification_level ---")
    schema = json.loads((ROOT / "api" / "echo-record-schema.v3.json").read_text())
    schema_levels = set(schema["properties"]["verification_level"]["enum"])
    expected = {"none"} | set(PROTOCOL_LEVELS)
    check(
        schema_levels == expected,
        "verification_level enum matches PROTOCOL_LEVELS + 'none'",
        f"schema has {sorted(schema_levels)}, expected {sorted(expected)}"
    )


def test_echo_schema_scope_label():
    """echo-record-schema.v3.json verification_scope_label enum must match VALID_SCOPE_LABELS."""
    print("\n--- Test: echo-record-schema.v3.json verification_scope_label ---")
    schema = json.loads((ROOT / "api" / "echo-record-schema.v3.json").read_text())
    schema_labels = set(schema["properties"]["verification_scope_label"]["enum"])
    check(
        schema_labels == VALID_SCOPE_LABELS,
        "verification_scope_label enum matches protocol_terms VALID_SCOPE_LABELS",
        f"schema has {sorted(schema_labels - VALID_SCOPE_LABELS)} extra, "
        f"protocol_terms has {sorted(VALID_SCOPE_LABELS - schema_labels)} extra"
    )


def test_echo_schema_record_kind():
    """echo-record-schema.v3.json record_kind enum must match VALID_RECORD_KINDS."""
    print("\n--- Test: echo-record-schema.v3.json record_kind ---")
    schema = json.loads((ROOT / "api" / "echo-record-schema.v3.json").read_text())
    schema_kinds = set(schema["properties"]["record_kind"]["enum"])
    check(
        schema_kinds == VALID_RECORD_KINDS,
        "record_kind enum matches protocol_terms VALID_RECORD_KINDS",
        f"schema has {sorted(schema_kinds - VALID_RECORD_KINDS)} extra, "
        f"protocol_terms has {sorted(VALID_RECORD_KINDS - schema_kinds)} extra"
    )


def test_echo_schema_archive_status():
    """echo-record-schema.v3.json archive_status enum must match VALID_ARCHIVE_STATUSES."""
    print("\n--- Test: echo-record-schema.v3.json archive_status ---")
    schema = json.loads((ROOT / "api" / "echo-record-schema.v3.json").read_text())
    schema_statuses = set(schema["properties"]["archive_status"]["enum"])
    check(
        schema_statuses == VALID_ARCHIVE_STATUSES,
        "archive_status enum matches protocol_terms VALID_ARCHIVE_STATUSES",
        f"schema has {sorted(schema_statuses - VALID_ARCHIVE_STATUSES)} extra, "
        f"protocol_terms has {sorted(VALID_ARCHIVE_STATUSES - schema_statuses)} extra"
    )


def test_echo_schema_independence_class():
    """echo-record-schema.v3.json independence_class enum must match VALID_INDEPENDENCE_CLASSES."""
    print("\n--- Test: echo-record-schema.v3.json independence_class ---")
    schema = json.loads((ROOT / "api" / "echo-record-schema.v3.json").read_text())
    schema_classes = set(schema["properties"]["independence_class"]["enum"])
    check(
        schema_classes == VALID_INDEPENDENCE_CLASSES,
        "independence_class enum matches protocol_terms VALID_INDEPENDENCE_CLASSES",
        f"schema has {sorted(schema_classes - VALID_INDEPENDENCE_CLASSES)} extra, "
        f"protocol_terms has {sorted(VALID_INDEPENDENCE_CLASSES - schema_classes)} extra"
    )


def test_validate_agent_submission_no_conflicting_locals():
    """validate_agent_submission.py must NOT define local enums that conflict with protocol_terms."""
    print("\n--- Test: validate_agent_submission.py no conflicting locals ---")
    src = (ROOT / "scripts" / "validate_agent_submission.py").read_text()

    # Check for local definitions (not imports or aliases)
    patterns = {
        "PROTOCOL_LEVELS": r'^PROTOCOL_LEVELS\s*=\s*\[',
        "VALID_RECORD_KINDS": r'^VALID_RECORD_KINDS\s*=\s*\{',
        "VALID_SCOPE_LABELS": r'^VALID_SCOPE_LABELS\s*=\s*\{',
        "B_LEVELS": r'^B_LEVELS\s*=\s*\[',
        "D_LEVELS": r'^D_LEVELS\s*=\s*\[',
        "T_LEVELS": r'^T_LEVELS\s*=\s*\[',
        "C_LEVELS": r'^C_LEVELS\s*=\s*\[',
        "N_LEVELS": r'^N_LEVELS\s*=\s*\[',
        "P_LEVELS": r'^P_LEVELS\s*=\s*\[',
    }

    for name, pattern in patterns.items():
        matches = [line for line in src.splitlines() if re.match(pattern, line.strip())]
        if matches:
            check(
                False,
                f"{name} not locally defined",
                f"found: {matches[0].strip()}"
            )
        else:
            check(True, f"{name} not locally defined (uses import)")

    # FORMAL_PROTOCOL_LEVELS is allowed as alias
    if "FORMAL_PROTOCOL_LEVELS = PROTOCOL_LEVELS" in src:
        check(True, "FORMAL_PROTOCOL_LEVELS is alias to PROTOCOL_LEVELS")


def test_claim_gate_component_levels():
    """claim_gate.py must import component levels from protocol_terms."""
    print("\n--- Test: claim_gate.py component levels ---")
    src = (ROOT / "scripts" / "claim_gate.py").read_text()

    # Check it imports from protocol_terms
    check(
        "from protocol_terms import" in src,
        "claim_gate.py imports from protocol_terms"
    )

    # Check no local level definitions
    local_defs = [
        ("PROTOCOL_LEVELS", r'^PROTOCOL_LEVELS\s*=\s*\['),
        ("B_LEVELS", r'^B_LEVELS\s*=\s*\['),
        ("D_LEVELS", r'^D_LEVELS\s*=\s*\['),
        ("T_LEVELS", r'^T_LEVELS\s*=\s*\['),
        ("C_LEVELS", r'^C_LEVELS\s*=\s*\['),
        ("N_LEVELS", r'^N_LEVELS\s*=\s*\['),
        ("P_LEVELS", r'^P_LEVELS\s*=\s*\['),
    ]

    for name, pattern in local_defs:
        matches = [line for line in src.splitlines() if re.match(pattern, line.strip())]
        if matches:
            check(False, f"claim_gate.py has no local {name}", f"found: {matches[0].strip()}")
        else:
            check(True, f"claim_gate.py has no local {name}")


def test_archive_readiness_gate():
    """archive_readiness_gate.py must import from protocol_terms."""
    print("\n--- Test: archive_readiness_gate.py ---")
    src = (ROOT / "scripts" / "archive_readiness_gate.py").read_text()

    check(
        "from protocol_terms import" in src,
        "archive_readiness_gate.py imports from protocol_terms"
    )

    local_defs = [
        ("PROTOCOL_LEVELS", r'^PROTOCOL_LEVELS\s*=\s*\['),
        ("B_LEVELS", r'^B_LEVELS\s*=\s*\['),
        ("D_LEVELS", r'^D_LEVELS\s*=\s*\['),
        ("T_LEVELS", r'^T_LEVELS\s*=\s*\['),
        ("C_LEVELS", r'^C_LEVELS\s*=\s*\['),
        ("N_LEVELS", r'^N_LEVELS\s*=\s*\['),
        ("P_LEVELS", r'^P_LEVELS\s*=\s*\['),
    ]

    for name, pattern in local_defs:
        matches = [line for line in src.splitlines() if re.match(pattern, line.strip())]
        if matches:
            check(False, f"archive_readiness_gate.py has no local {name}", f"found: {matches[0].strip()}")
        else:
            check(True, f"archive_readiness_gate.py has no local {name}")


def test_submission_intake():
    """submission_intake.py must derive VLEVELS from protocol_terms."""
    print("\n--- Test: submission_intake.py ---")
    src = (ROOT / "scripts" / "submission_intake.py").read_text()

    check(
        "from protocol_terms import" in src,
        "submission_intake.py imports from protocol_terms"
    )
    check(
        "set(PROTOCOL_LEVELS)" in src,
        "submission_intake.py derives VLEVELS from PROTOCOL_LEVELS"
    )


def test_echo_issue_intake():
    """echo_issue_intake.py must derive VALID_LEVELS from protocol_terms."""
    print("\n--- Test: echo_issue_intake.py ---")
    src = (ROOT / "scripts" / "echo_issue_intake.py").read_text()

    check(
        "from protocol_terms import" in src,
        "echo_issue_intake.py imports from protocol_terms"
    )
    check(
        "set(PROTOCOL_LEVELS)" in src,
        "echo_issue_intake.py derives VALID_LEVELS from PROTOCOL_LEVELS"
    )


def main():
    print("=" * 60)
    print("Protocol Terms Consistency Tests")
    print("Authority: api/protocol-terms.v1.json")
    print("=" * 60)

    test_echo_schema_verification_level()
    test_echo_schema_scope_label()
    test_echo_schema_record_kind()
    test_echo_schema_archive_status()
    test_echo_schema_independence_class()
    test_validate_agent_submission_no_conflicting_locals()
    test_claim_gate_component_levels()
    test_archive_readiness_gate()
    test_submission_intake()
    test_echo_issue_intake()

    print("\n" + "=" * 60)
    print(f"Results: {PASS_COUNT} passed, {FAIL_COUNT} failed")
    print("=" * 60)

    if FAIL_COUNT > 0:
        print("FAIL: Consistency check failed.")
        return 1
    print("PASS: All consistency checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
