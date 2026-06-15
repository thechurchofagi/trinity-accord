#!/usr/bin/env python3
"""Contract test: builder rejects guardian-key-rotation as reserved."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILDER = ROOT / "downloads" / "record-chain-builder.mjs"


def require(cond, msg):
    if not cond:
        raise AssertionError(msg)


def main():
    result = subprocess.run(
        ["node", str(BUILDER), "guardian-key-rotation"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
    )

    require(result.returncode != 0, "guardian-key-rotation command must fail while reserved")
    combined = result.stdout + result.stderr
    require("reserved" in combined.lower(), f"expected 'reserved' in output: {combined}")
    require("old-key" in combined.lower() or "transition" in combined.lower(), f"expected old-key/transition reference: {combined}")

    print("PASS: builder guardian-key-rotation reserved command")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
