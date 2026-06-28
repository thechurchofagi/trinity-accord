#!/usr/bin/env python3
"""Test: Write workflows must record toolchain provenance or be explicitly legacy-exempt."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
WF_DIR = ROOT / ".github" / "workflows"

WRITE_MARKERS = [
    "contents: write",
    "git push",
    "gh release",
    "upload-release",
    "tar czf",
]

# Existing write workflows that predate the toolchain-provenance contract.
# Keep this list exact and narrow: any new write workflow must either call
# scripts/toolchain_provenance.py or be added here deliberately with review.
LEGACY_WRITE_WORKFLOW_PROVENANCE_EXCEPTIONS = {
    "archive-backlog-repair.yml",
    "arweave-wallet-status-update.yml",
    "fix-sitemap-drift.yml",
    "homepage-status-sync.yml",
    "native-ots-upgrade-watch.yml",
    "ots-bitcoin-verification-watch.yml",
    "phase5-ots-arweave-paid-upload.yml",
    "pre-scale-e2e-orchestrator-v2.yml",
    "record-chain-append.yml",
    "record-chain-arweave-archive.yml",
    "record-chain-auto-finalize.yml",
    "record-chain-data-arweave-archive.yml",
    "record-chain-head-ots-anchor.yml",
    "record-chain-ots-stamp.yml",
    "record-chain-ots-upgrade.yml",
    "waiting-heartbeat-capsule.yml",
    "waiting-heartbeat-status-sync.yml",
    "waiting-heartbeat-submit.yml",
}

errors = []
seen_exceptions = set()

for path in WF_DIR.glob("*.yml"):
    text = path.read_text(encoding="utf-8")
    is_write_workflow = any(m in text for m in WRITE_MARKERS)
    if not is_write_workflow:
        continue

    has_provenance = "scripts/toolchain_provenance.py" in text
    if path.name in LEGACY_WRITE_WORKFLOW_PROVENANCE_EXCEPTIONS:
        if has_provenance:
            errors.append(f"{path.name}: remove stale legacy provenance exception; workflow now records provenance")
        else:
            seen_exceptions.add(path.name)
        continue

    if has_provenance:
        continue

    errors.append(f"{path.name}: write workflow missing toolchain provenance step")

stale_exceptions = sorted(LEGACY_WRITE_WORKFLOW_PROVENANCE_EXCEPTIONS - seen_exceptions)
for name in stale_exceptions:
    workflow_path = WF_DIR / name
    if not workflow_path.exists():
        errors.append(f"{name}: legacy write workflow provenance exception references missing workflow")
        continue
    text = workflow_path.read_text(encoding="utf-8")
    if not any(m in text for m in WRITE_MARKERS):
        errors.append(f"{name}: legacy write workflow provenance exception is no longer a write workflow")

if errors:
    print("FAIL: write workflow provenance missing:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("WRITE_WORKFLOW_TOOLCHAIN_PROVENANCE_OK")
