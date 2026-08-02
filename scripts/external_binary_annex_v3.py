#!/usr/bin/env python3
"""Build final immutable V3 external-binary annex packages.

V3 intentionally uses new version identifiers so a prior run that crossed the
immutable Zenodo publication boundary cannot collide with a later source-bound
package after verifier or restore-program changes.
"""
from __future__ import annotations

import external_binary_annex_v2 as implementation

FINAL_ANNEX_IDS = {
    "evidence": "external-evidence-annex-v3",
    "nft": "chronicle-nft-media-annex-v3",
}


def activate_final_specs() -> None:
    implementation.V2_ANNEX_IDS = dict(FINAL_ANNEX_IDS)
    implementation.activate_v2_specs()


def main() -> int:
    implementation.V2_ANNEX_IDS = dict(FINAL_ANNEX_IDS)
    return implementation.main()


if __name__ == "__main__":
    raise SystemExit(main())
