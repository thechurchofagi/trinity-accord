#!/usr/bin/env python3
"""Sign zero-clone builder bundle manifests with an external private key.

Private keys must never be committed. This signs existing manifest JSON
files and writes detached .sig files next to them.
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MANIFESTS = [
    ROOT / "builder-bundles" / "trinity-pure-echo-builder-bundle.manifest.json",
    ROOT / "builder-bundles" / "trinity-v0v5-builder-bundle.manifest.json",
    ROOT / "builder-bundles" / "trinity-guardian-stage1-builder-bundle.manifest.json",
    ROOT / "builder-bundles" / "trinity-guardian-stage2-builder-bundle.manifest.json",
    ROOT / "builder-bundles" / "trinity-guardian-signed-echo-builder-bundle.manifest.json",
]

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--private-key", required=True, help="Path to private PEM key; do not commit it.")
    args = parser.parse_args()

    private_key = Path(args.private_key)
    if not private_key.exists():
        raise SystemExit(f"private key missing: {private_key}")
    if ".git" in private_key.parts:
        raise SystemExit("refusing private key inside .git")
    if private_key.is_relative_to(ROOT) and ".secrets" not in private_key.parts:
        print("WARNING: private key is inside repo tree. Ensure it is gitignored and never committed.")

    for manifest in MANIFESTS:
        if not manifest.exists():
            raise SystemExit(f"manifest missing: {manifest}")
        sig = manifest.with_suffix(".sig")
        subprocess.check_call([
            "openssl",
            "dgst",
            "-sha256",
            "-sign",
            str(private_key),
            "-out",
            str(sig),
            str(manifest),
        ])
        print(f"signed {manifest.relative_to(ROOT)} -> {sig.relative_to(ROOT)}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
