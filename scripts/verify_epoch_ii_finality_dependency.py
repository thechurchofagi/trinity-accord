#!/usr/bin/env python3
"""Stream-verify every Polygon/Base Finality Release file with bounded disk use.

This preflight proves that every byte required for the second-institution copy is
publicly readable and matches its fixed SHA-256 and size.  It does not upload to,
modify or submit Harvard or Zenodo.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import shutil
import subprocess
import sys

import build_epoch_ii_content_candidate as content


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", type=pathlib.Path, required=True)
    parser.add_argument("--inventory-dir", type=pathlib.Path, required=True)
    parser.add_argument("--work-dir", type=pathlib.Path, required=True)
    parser.add_argument("--report", type=pathlib.Path, required=True)
    args = parser.parse_args()

    repo = args.repository_root.resolve()
    rows = content.load_json(args.inventory_dir.resolve() / "RELEASE-ASSETS.json")
    dependency = content.full_finality_dependency(rows)
    selected = [row for row in rows if row.get("family") == "sidechain_finality"]
    objects = content.validate_release_rows(selected)
    work = args.work_dir.resolve()
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)

    verified = []
    peak_object_bytes = 0
    try:
        for index, (sha, row) in enumerate(sorted(objects.items()), start=1):
            result = content.download_object(work, row)
            peak_object_bytes = max(peak_object_bytes, int(result["bytes"]))
            verified.append(
                {
                    "filename": str(row["filename"]),
                    "bytes": int(result["bytes"]),
                    "sha256": sha,
                    "release_tag": str(row["release_tag"]),
                    "source_locator": str(row["source_locator"]),
                    "verification": "public_release_byte_readback_sha256_and_size_match",
                }
            )
            content.object_path(work, sha).unlink()
            content.log(f"Finality {index}/{len(objects)} PASS bytes={result['bytes']} sha256={sha[:12]}")
    finally:
        shutil.rmtree(work, ignore_errors=True)

    source_sha = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()
    report = {
        "schema": "trinityaccord.epoch-ii-finality-full-byte-verification.v1",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_git_commit_sha": source_sha,
        "result": "pass",
        "scope": "every_public_polygon_base_finality_release_asset",
        "zenodo_version_doi": dependency["zenodo_version_doi"],
        "logical_assets": dependency["logical_assets"],
        "logical_bytes": dependency["logical_bytes"],
        "unique_objects": dependency["unique_objects"],
        "unique_bytes_verified": sum(item["bytes"] for item in verified),
        "bounded_disk_peak_object_bytes": peak_object_bytes,
        "institutional_copy_requirement": "copy_every_public_file_byte_for_byte_and_verify_anonymous_public_readback",
        "institutional_copy_completed": False,
        "harvard_mutated": False,
        "files": verified,
    }
    if len(verified) != dependency["unique_objects"] or report["unique_bytes_verified"] != dependency["unique_bytes"]:
        raise SystemExit("Finality full-byte verification total mismatch")
    content.write_json(args.report.resolve(), report)
    content.log(
        f"PASS Finality files={report['logical_assets']} bytes={report['unique_bytes_verified']} Harvard mutation=NONE"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
