#!/usr/bin/env python3
"""Bootstrap placeholder replaced by the DOI backfill applicator after merge."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPLICATOR = ROOT / "scripts" / "apply_zenodo_doi_backfill.py"


def main() -> int:
    if not APPLICATOR.exists():
        raise SystemExit("FAIL: DOI backfill applicator is missing during bootstrap")
    print("PASS: DOI sync bootstrap placeholder is bounded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
