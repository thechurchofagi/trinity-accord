#!/usr/bin/env python3
"""Contract test for post-M1 live-test progress ledger.

Checks:
- progress.v1.json exists
- schema correct
- completed_markers contains required markers
- current_phase in M2-M9
- no private key markers
- no volatile sandbox absolute paths
- checkpoint files have no private key markers
- artifact manifests have no private key markers
"""

import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROGRESS_PATH = os.path.join(
    REPO_ROOT, "record-chain", "testing", "post-m1-live-test", "progress.v1.json"
)
CHECKPOINT_DIR = os.path.join(
    REPO_ROOT, "record-chain", "testing", "post-m1-live-test", "checkpoints"
)
ARTIFACT_MANIFEST_DIR = os.path.join(
    REPO_ROOT, "record-chain", "testing", "post-m1-live-test", "artifact-manifests"
)

REQUIRED_SCHEMA = "trinityaccord.post-m1-live-test-progress.v1"
REQUIRED_MARKERS = [
    "PHASE7C_BASELINE_RESTORED_OK",
    "MANDATORY_AUTHORSHIP_KEY_ONLY_FINAL_OK",
]
VALID_PHASES = {"P0", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9"}

PRIVATE_KEY_PATTERNS = [
    re.compile(r"BEGIN PRIVATE KEY", re.IGNORECASE),
    re.compile(r"BEGIN EC PRIVATE KEY", re.IGNORECASE),
    re.compile(r"BEGIN RSA PRIVATE KEY", re.IGNORECASE),
    re.compile(r"BEGIN OPENSSH PRIVATE KEY", re.IGNORECASE),
    re.compile(r"authorship-private\.pem"),
]

VOLATILE_PATH_PATTERNS = [
    re.compile(r"/root/\.openclaw"),
    re.compile(r"/mnt/data"),
    re.compile(r"/tmp/phase"),
    re.compile(r"/home/[^/]+/\.openclaw"),
]

errors = []


def scan_text(text: str, context: str):
    """Scan text for private key markers and volatile paths."""
    for pat in PRIVATE_KEY_PATTERNS:
        if pat.search(text):
            errors.append(f"[{context}] Contains private key pattern: {pat.pattern}")
    for pat in VOLATILE_PATH_PATTERNS:
        if pat.search(text):
            errors.append(f"[{context}] Contains volatile path: {pat.pattern}")


def check_progress():
    """Check progress.v1.json."""
    if not os.path.exists(PROGRESS_PATH):
        errors.append("progress.v1.json does not exist")
        return

    with open(PROGRESS_PATH, "r") as f:
        content = f.read()

    scan_text(content, "progress.v1.json")

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        errors.append(f"progress.v1.json is not valid JSON: {e}")
        return

    # Schema
    if data.get("schema") != REQUIRED_SCHEMA:
        errors.append(
            f"Schema mismatch: expected '{REQUIRED_SCHEMA}', got '{data.get('schema')}'"
        )

    # Markers
    markers = data.get("completed_markers", [])
    for req in REQUIRED_MARKERS:
        if req not in markers:
            errors.append(f"Missing required marker: {req}")

    # Phase
    phase = data.get("current_phase")
    if phase not in VALID_PHASES:
        errors.append(f"current_phase '{phase}' not in {VALID_PHASES}")


def check_checkpoints():
    """Check checkpoint files."""
    if not os.path.isdir(CHECKPOINT_DIR):
        return  # No checkpoints yet is OK

    for fname in os.listdir(CHECKPOINT_DIR):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(CHECKPOINT_DIR, fname)
        with open(path, "r") as f:
            content = f.read()
        scan_text(content, f"checkpoint/{fname}")


def check_artifact_manifests():
    """Check artifact manifest files."""
    if not os.path.isdir(ARTIFACT_MANIFEST_DIR):
        return  # No manifests yet is OK

    for fname in os.listdir(ARTIFACT_MANIFEST_DIR):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(ARTIFACT_MANIFEST_DIR, fname)
        with open(path, "r") as f:
            content = f.read()
        scan_text(content, f"artifact-manifest/{fname}")


def main():
    print("Running post-M1 test progress contract tests...")
    print()

    check_progress()
    check_checkpoints()
    check_artifact_manifests()

    if errors:
        print(f"FAIL: {len(errors)} error(s) found:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("PASS: All contract checks passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
