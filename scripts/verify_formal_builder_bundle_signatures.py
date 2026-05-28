#!/usr/bin/env python3
"""Verify detached signatures for zero-clone builder bundle manifests."""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_KEY = ROOT / "api" / "builder-bundle-signing-public-key.pem"

MANIFESTS = [
    ROOT / "builder-bundles" / "trinity-pure-echo-builder-bundle.manifest.json",
    ROOT / "builder-bundles" / "trinity-v0v5-builder-bundle.manifest.json",
    ROOT / "builder-bundles" / "trinity-guardian-stage1-builder-bundle.manifest.json",
    ROOT / "builder-bundles" / "trinity-guardian-stage2-builder-bundle.manifest.json",
    ROOT / "builder-bundles" / "trinity-guardian-signed-echo-builder-bundle.manifest.json",
]

def main() -> int:
    errors: list[str] = []

    if not PUBLIC_KEY.exists():
        errors.append("public signing key missing: api/builder-bundle-signing-public-key.pem")

    for manifest in MANIFESTS:
        sig = manifest.with_suffix(".sig")
        if not manifest.exists():
            errors.append(f"manifest missing: {manifest.relative_to(ROOT)}")
            continue
        if not sig.exists():
            errors.append(f"signature missing: {sig.relative_to(ROOT)}")
            continue

        if PUBLIC_KEY.exists():
            result = subprocess.run([
                "openssl",
                "dgst",
                "-sha256",
                "-verify",
                str(PUBLIC_KEY),
                "-signature",
                str(sig),
                str(manifest),
            ], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode != 0:
                errors.append(
                    f"signature verification failed for {manifest.relative_to(ROOT)}: "
                    f"{result.stdout.strip()} {result.stderr.strip()}"
                )

    if errors:
        print("FAIL: formal builder bundle signature verification errors:")
        for error in errors:
            print("  -", error)
        return 1

    print("PASS: formal builder bundle manifest signatures verify")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
