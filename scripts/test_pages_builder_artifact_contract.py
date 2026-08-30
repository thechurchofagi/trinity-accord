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

    witness_index_path = ROOT / "archive/encrypted-witness-archives.v1.json"
    witness_index = json.loads(witness_index_path.read_text(encoding="utf-8"))
    published_index = site_dir / "archive/encrypted-witness-archives.v1.json"
    if not published_index.is_file():
        fail(f"missing encrypted-witness machine index: {published_index}")
    if published_index.read_bytes() != witness_index_path.read_bytes():
        fail("published encrypted-witness machine index differs from source")

    archives = witness_index.get("archives")
    if not isinstance(archives, dict) or set(archives) != {
        "first_star_moon_witness",
        "second_star_moon_witness",
        "bubble_constellation",
    }:
        fail("encrypted-witness machine index does not contain the exact archive set")
    for archive in archives.values():
        state_record = archive.get("state_record")
        if not isinstance(state_record, str) or not state_record.startswith("archive/"):
            fail("encrypted-witness archive has an invalid state_record")
        source_state = ROOT / state_record
        published_state = site_dir / state_record
        if not published_state.is_file():
            fail(f"missing encrypted-witness state record: {published_state}")
        if published_state.read_bytes() != source_state.read_bytes():
            fail(f"published encrypted-witness state differs from source: {state_record}")

    subprocess.run(["node", "--check", str(canonical)], check=True)
    print("PASS: Pages builder artifact contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
