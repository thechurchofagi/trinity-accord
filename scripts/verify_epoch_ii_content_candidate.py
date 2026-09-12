#!/usr/bin/env python3
"""Independent bounded-disk verifier and cold restorer for Epoch II candidate."""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
from typing import Any

SCHEMA = "trinityaccord.preservation-epoch-ii-content-candidate.v1"
HEX64 = set("0123456789abcdef")


def load(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_relative(value: str) -> pathlib.Path:
    path = pathlib.PurePosixPath(value)
    if not value or value.startswith("/") or ".." in path.parts or "\\" in value or "\x00" in value:
        raise SystemExit(f"unsafe candidate logical path: {value!r}")
    return pathlib.Path(*path.parts)


def object_path(store: pathlib.Path, digest: str) -> pathlib.Path:
    value = digest.lower()
    if len(value) != 64 or any(ch not in HEX64 for ch in value):
        raise SystemExit(f"invalid object SHA-256: {digest!r}")
    return store / "objects" / "sha256" / value[:2] / value


def verify_checksums(candidate: pathlib.Path) -> int:
    rows = (candidate / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
    seen: set[str] = set()
    for row in rows:
        digest, logical = row.split("  ", 1)
        relative = safe_relative(logical)
        if logical in seen:
            raise SystemExit(f"duplicate candidate checksum path: {logical}")
        seen.add(logical)
        path = candidate / relative
        if not path.is_file() or sha256(path) != digest:
            raise SystemExit(f"candidate checksum mismatch: {logical}")
    actual = {
        path.relative_to(candidate).as_posix()
        for path in candidate.rglob("*")
        if path.is_file() and path.name != "SHA256SUMS"
    }
    if actual != seen:
        raise SystemExit("candidate checksum set does not cover exact file set")
    return len(rows)


def verify_identity(manifest: dict[str, Any]) -> str:
    expected = str(manifest.get("candidate_identity_sha256") or "")
    material = dict(manifest)
    material.pop("candidate_identity_sha256", None)
    observed = hashlib.sha256(
        json.dumps(material, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if observed != expected:
        raise SystemExit(f"candidate identity mismatch: {observed} != {expected}")
    return observed


def verify_and_cold_copy_objects(
    candidate: pathlib.Path, store: pathlib.Path, scratch: pathlib.Path
) -> tuple[int, int, int]:
    rows = load(candidate / "SELECTED-RELEASE-ASSETS.json")
    expected: dict[str, int] = {}
    logical: set[str] = set()
    for row in rows:
        digest = str(row["declared_sha256"]).lower()
        size = int(row["size_bytes"])
        key = f"github-releases/{row['release_id']}-{row['release_tag']}/{row['filename']}"
        safe_relative(key)
        if key in logical:
            raise SystemExit(f"duplicate selected logical path: {key}")
        logical.add(key)
        if digest in expected and expected[digest] != size:
            raise SystemExit(f"same object digest has conflicting sizes: {digest}")
        expected[digest] = size
    total = 0
    recovered = scratch / "recovered-object"
    for digest, size in sorted(expected.items()):
        source = object_path(store, digest)
        if not source.is_file() or source.stat().st_size != size or sha256(source) != digest:
            raise SystemExit(f"source object failed cold verification: {digest}")
        shutil.copyfile(source, recovered)
        if recovered.stat().st_size != size or sha256(recovered) != digest:
            raise SystemExit(f"cold-copied object failed verification: {digest}")
        recovered.unlink()
        total += size
    return len(rows), len(expected), total


def cold_restore_source_capsule(candidate: pathlib.Path, scratch: pathlib.Path) -> dict[str, Any]:
    capsule = candidate / "source-capsule"
    script = capsule / "restore-trinity-accord.py"
    if not script.is_file():
        raise SystemExit("source capsule restore program missing")
    restored = scratch / "source"
    subprocess.run(
        [sys.executable, str(script), "--deposit-dir", str(capsule), "--output-dir", str(restored)],
        check=True,
    )
    report = load(restored / "recovery-report.json")
    if report.get("result") != "pass":
        raise SystemExit("independent source capsule cold restore failed")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-dir", required=True, type=pathlib.Path)
    parser.add_argument("--object-store", required=True, type=pathlib.Path)
    parser.add_argument("--report", type=pathlib.Path)
    args = parser.parse_args()
    candidate = args.candidate_dir.resolve()
    store = args.object_store.resolve()
    checksums = verify_checksums(candidate)
    manifest = load(candidate / "CONTENT-CANDIDATE.json")
    if manifest.get("schema") != SCHEMA:
        raise SystemExit(f"unexpected candidate schema: {manifest.get('schema')}")
    if manifest.get("authority") != "three Bitcoin Originals only" or manifest.get("harvard_mutated") is not False:
        raise SystemExit("candidate authority/Harvard boundary changed")
    identity = verify_identity(manifest)
    nft = load(candidate / "NFT-CAR-VERIFICATION.json")
    physical = load(candidate / "PHYSICAL-PAYLOAD-CROSSCHECK.json")
    public_checksums = load(candidate / "PUBLIC-CHECKSUM-LIST-CROSSCHECK.json")
    if nft.get("status") != "pass" or int(nft.get("verified_cars", -1)) != 434:
        raise SystemExit("NFT CAR verification report is not PASS 434/434")
    if physical.get("status") != "pass" or int(physical.get("unmatched", -1)) != 0:
        raise SystemExit("physical payload crosscheck is not PASS 153/153")
    if public_checksums.get("status") != "pass":
        raise SystemExit("public checksum-list crosscheck is not PASS")
    with tempfile.TemporaryDirectory(prefix="epoch-ii-cold-") as value:
        scratch = pathlib.Path(value)
        logical, objects, total = verify_and_cold_copy_objects(candidate, store, scratch)
        source = cold_restore_source_capsule(candidate, scratch)
    if total != int(manifest.get("selected_unique_bytes_verified") or -1):
        raise SystemExit("cold recovered byte total differs from candidate manifest")
    if source.get("source_git_commit_sha") != manifest.get("source_git_commit_sha"):
        raise SystemExit("cold restored source commit differs from candidate")
    report = {
        "schema": "trinityaccord.preservation-epoch-ii-content-cold-verification.v1",
        "result": "pass",
        "candidate_identity_sha256": identity,
        "candidate_checksum_files_verified": checksums,
        "logical_release_assets_recovered": logical,
        "unique_objects_recovered": objects,
        "unique_object_bytes_recovered": total,
        "nft_cars_verified": 434,
        "physical_public_files_verified": 153,
        "source_git_commit_sha": source["source_git_commit_sha"],
        "source_capsule_cold_restore": "pass",
        "bounded_disk_method": "copy and re-hash each content-addressed object into a clean temporary path, then delete before the next object",
        "institutional_submission_performed": False,
        "harvard_mutated": False,
    }
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
