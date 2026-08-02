#!/usr/bin/env python3
"""Migrate the repository-capsule test from legacy token to baseline semantics."""
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "tests/test_preservation_capsule.py"

OLD = '''    assert "exact_eight_file_capsule" in index["mirror_classes"][
        "repository_preservation_zenodo"
    ]
'''
NEW = '''    repository_mirror = index["mirror_classes"][
        "repository_preservation_zenodo"
    ]
    assert "publication-baseline" in repository_mirror
    assert "stable recovery catalog" in repository_mirror
    assert "public DOI-only restore" in repository_mirror
'''


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    if NEW in text:
        print("REPOSITORY_PRESERVATION_BASELINE_CONTRACT_ALREADY_CURRENT")
        return 0
    if OLD not in text:
        raise SystemExit(
            "repository preservation baseline test is neither legacy nor current"
        )
    TARGET.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
    print("REPOSITORY_PRESERVATION_BASELINE_CONTRACT_MIGRATED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
