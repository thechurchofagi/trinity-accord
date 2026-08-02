#!/usr/bin/env python3
"""Publish or reconcile final immutable V3 external-binary annexes."""
from __future__ import annotations

import external_binary_annex_v2 as builder_implementation
from external_binary_annex_v3 import FINAL_ANNEX_IDS

# The verified V2 publisher imports this same module object and activates its
# configured version identifiers before reading either package.
builder_implementation.V2_ANNEX_IDS = dict(FINAL_ANNEX_IDS)

import publish_external_binary_annexes_to_zenodo_v2 as publisher  # noqa: E402


def main() -> int:
    builder_implementation.V2_ANNEX_IDS = dict(FINAL_ANNEX_IDS)
    return publisher.main()


if __name__ == "__main__":
    raise SystemExit(main())
