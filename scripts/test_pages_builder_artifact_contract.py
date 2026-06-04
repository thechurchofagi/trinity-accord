from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-dir", required=True)
    args = parser.parse_args()

    site_dir = Path(args.site_dir)
    contract = json.loads(
        (ROOT / "api/record-chain-builder-bundles.v1.json").read_text(encoding="utf-8")
    )
    builder = contract["canonical_builder"]

    if builder["url"] != "/downloads/record-chain-builder.mjs":
        fail(f"unexpected canonical builder URL: {builder['url']}")

    canonical = site_dir / builder["url"].lstrip("/")
    mirror = site_dir / "builder-bundles/record-chain-builder.mjs"

    if not canonical.is_file():
        fail(f"missing canonical builder: {canonical}")
    if not mirror.is_file():
        fail(f"missing compatibility builder mirror: {mirror}")

    canonical_bytes = canonical.read_bytes()
    if canonical_bytes != mirror.read_bytes():
        fail("canonical builder and compatibility mirror differ")

    if hashlib.sha256(canonical_bytes).hexdigest() != builder["sha256"]:
        fail("canonical builder SHA-256 differs from API contract")
    if len(canonical_bytes) != builder["size_bytes"]:
        fail("canonical builder size differs from API contract")

    subprocess.run(["node", "--check", str(canonical)], check=True)
    print("PASS: Pages builder artifact contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
