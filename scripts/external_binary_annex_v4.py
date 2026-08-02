#!/usr/bin/env python3
"""Build final immutable V4 external-binary annex packages.

V4 follows the publicly published Evidence V3 record after correcting the
Zenodo direct-record metadata normalization boundary. Both evidence and NFT
packages use new immutable version identifiers so their source-bound bytes are
never compared with or substituted for an earlier published version.
"""
from __future__ import annotations

import external_binary_annex_v2 as implementation

FINAL_ANNEX_IDS = {
    "evidence": "external-evidence-annex-v4",
    "nft": "chronicle-nft-media-annex-v4",
}


def activate_final_specs() -> None:
    implementation.V2_ANNEX_IDS = dict(FINAL_ANNEX_IDS)
    implementation.activate_v2_specs()


def main() -> int:
    implementation.V2_ANNEX_IDS = dict(FINAL_ANNEX_IDS)
    return implementation.main()


if __name__ == "__main__":
    raise SystemExit(main())
