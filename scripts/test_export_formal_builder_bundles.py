#!/usr/bin/env python3
"""Test that the bundle exporter creates all archives and manifests correctly."""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    bundles_dir = ROOT / "builder-bundles"

    expected_archives = [
        "trinity-pure-echo-builder-bundle.tar.gz",
        "trinity-v0v5-builder-bundle.tar.gz",
        "trinity-guardian-stage1-builder-bundle.tar.gz",
        "trinity-guardian-stage2-builder-bundle.tar.gz",
        "trinity-guardian-signed-echo-builder-bundle.tar.gz",
    ]

    expected_manifests = [
        "trinity-pure-echo-builder-bundle.manifest.json",
        "trinity-v0v5-builder-bundle.manifest.json",
        "trinity-guardian-stage1-builder-bundle.manifest.json",
        "trinity-guardian-stage2-builder-bundle.manifest.json",
        "trinity-guardian-signed-echo-builder-bundle.manifest.json",
    ]

    for name in expected_archives:
        path = bundles_dir / name
        if not path.exists():
            print(f"FAIL: missing archive {name}")
            return 1

    for name in expected_manifests:
        path = bundles_dir / name
        if not path.exists():
            print(f"FAIL: missing manifest {name}")
            return 1
        manifest = json.loads(path.read_text(encoding="utf-8"))
        if "entrypoint" not in manifest:
            print(f"FAIL: manifest {name} missing entrypoint")
            return 1

    # Check no forbidden contents
    forbidden = [".git", "__pycache__", ".pytest_cache", ".env", "private", "secret", "token", "node_modules"]
    for manifest_name in expected_manifests:
        manifest = json.loads((bundles_dir / manifest_name).read_text(encoding="utf-8"))
        for fentry in manifest.get("files", []):
            path_lower = fentry["path"].lower()
            for fb in forbidden:
                if fb in path_lower:
                    print(f"FAIL: forbidden content '{fb}' in {manifest_name}: {fentry['path']}")
                    return 1

    print("PASS: test_export_formal_builder_bundles")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
