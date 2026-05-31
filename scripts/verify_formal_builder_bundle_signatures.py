#!/usr/bin/env python3
"""Verify integrity of zero-clone builder bundle manifests.

Checks that all files listed in each manifest exist and match their SHA256 hashes.
RSA detached signatures have been removed; manifest SHA256 hashes are the
integrity mechanism.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MANIFESTS = [
    ROOT / "builder-bundles" / "trinity-pure-echo-builder-bundle.manifest.json",
    ROOT / "builder-bundles" / "trinity-v0v5-builder-bundle.manifest.json",
    ROOT / "builder-bundles" / "trinity-guardian-stage1-builder-bundle.manifest.json",
    ROOT / "builder-bundles" / "trinity-guardian-stage2-builder-bundle.manifest.json",
    ROOT / "builder-bundles" / "trinity-guardian-signed-echo-builder-bundle.manifest.json",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    errors: list[str] = []

    for manifest_path in MANIFESTS:
        if not manifest_path.exists():
            errors.append(f"manifest missing: {manifest_path.relative_to(ROOT)}")
            continue

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        bundle = manifest.get("bundle", manifest_path.stem)

        # Verify archive hash if present
        archive_rel = manifest.get("archive")
        if archive_rel:
            archive_path = manifest_path.parent / archive_rel
            if archive_path.exists():
                actual = sha256_file(archive_path)
                expected = manifest.get("archive_sha256")
                if expected and actual != expected:
                    errors.append(
                        f"{bundle}: archive hash mismatch: "
                        f"expected {expected}, got {actual}"
                    )

        # Verify individual file hashes
        for entry in manifest.get("files", []):
            file_rel = entry.get("path", "")
            expected_hash = entry.get("sha256")
            file_path = ROOT / file_rel

            if not file_path.exists():
                errors.append(f"{bundle}: file missing: {file_rel}")
                continue

            actual_hash = sha256_file(file_path)
            if expected_hash and actual_hash != expected_hash:
                errors.append(
                    f"{bundle}: hash mismatch for {file_rel}: "
                    f"expected {expected_hash}, got {actual_hash}"
                )

    if errors:
        print("FAIL: builder bundle integrity verification errors:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"PASS: all {len(MANIFESTS)} builder bundle manifests verified (SHA256)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
