#!/usr/bin/env python3
"""Reconcile derived Native OTS state after a branch rebase.

This script never upgrades an OTS proof and never uploads to Arweave. It only
rebuilds derived views from already-committed anchor/registry/wallet evidence so
a write workflow cannot push stale API, backlog, or wallet status after main
advances while the workflow is running.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from run_native_ots_upgrade_verify import (  # noqa: E402
    NATIVE_API_REGISTRY,
    NATIVE_REGISTRY,
    read_json,
    sync_native_latest_from_anchor,
    validate_native_latest_ots,
    validate_native_registry,
)

RunFn = Callable[..., subprocess.CompletedProcess[str]]


def require_registry_parity() -> dict[str, Any]:
    registry = validate_native_registry()
    if not NATIVE_API_REGISTRY.exists():
        raise SystemExit("native OTS API registry missing")
    api_registry = read_json(NATIVE_API_REGISTRY)
    if registry != api_registry:
        raise SystemExit("native OTS registry/API projection mismatch after reconciliation")
    return registry


def reconcile(*, run: RunFn = subprocess.run) -> dict[str, Any]:
    latest = validate_native_latest_ots()
    anchor_rel = latest.get("latest_anchor_file")
    if not isinstance(anchor_rel, str) or not anchor_rel:
        raise SystemExit("native OTS latest view is missing latest_anchor_file")

    # Rebuild the latest API projection from the rebased tree's current anchor,
    # not from whichever anchor happened to be processed before the rebase.
    latest = sync_native_latest_from_anchor(anchor_rel)
    registry = require_registry_parity()

    commands = [
        [sys.executable, "scripts/detect_archive_backlog.py", "--write"],
        [sys.executable, "scripts/generate_arweave_wallet_status.py"],
    ]
    for command in commands:
        run(command, cwd=ROOT, check=True, text=True)

    # The generators must not disturb registry parity.
    require_registry_parity()

    return {
        "result": "pass",
        "latest_anchor_file": anchor_rel,
        "latest_ots_status": latest.get("ots_status"),
        "latest_bitcoin_verified": latest.get("bitcoin_verified"),
        "registry_entries": len(registry.get("entries", [])),
        "paid_upload_performed": False,
        "ots_upgrade_performed": False,
        "derived_state_reconciled": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Reconcile derived Native OTS state without upgrading or uploading")
    parser.parse_args()
    print(json.dumps(reconcile(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
