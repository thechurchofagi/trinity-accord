#!/usr/bin/env python3
"""Build the exact Harvard Preservation Epoch II file-layout manifest.

This is a read-only planner. It never calls Harvard, creates a Dataset, uploads,
submits for review or resubmits. Payload rows retain their original Release URL and
byte identity so a later authorized staging/upload step can fail closed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from collections import Counter
from typing import Any

MAX_HARVARD_FILE_BYTES = 2_500_000_000
SCHEMA = "trinityaccord.harvard-preservation-epoch-ii-file-layout.v1"


def load(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def local_row(repo: pathlib.Path, relative: str, directory: str) -> dict[str, Any]:
    path = repo / relative
    if not path.is_file():
        raise SystemExit(f"required researcher-readable file missing: {relative}")
    return {
        "directory_label": directory,
        "filename": path.name,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "source_kind": "repository_file",
        "source_locator": relative,
        "logical_role": "researcher_readable",
    }


def candidate_row(path: pathlib.Path, candidate: pathlib.Path, directory: str) -> dict[str, Any]:
    return {
        "directory_label": directory,
        "filename": path.name,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "source_kind": "verified_candidate_file",
        "source_locator": path.relative_to(candidate).as_posix(),
        "logical_role": "verification_or_cold_recovery",
    }


def safe_component(value: str, label: str) -> str:
    if not value or value in {".", ".."} or "/" in value or "\\" in value:
        raise SystemExit(f"unsafe {label}: {value!r}")
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise SystemExit(f"unsupported {label}: {value!r}")
    return value


def public_release_row(row: dict[str, Any], directory: str) -> dict[str, Any]:
    filename = safe_component(str(row["filename"]), "Release filename")
    tag = safe_component(str(row["release_tag"]), "Release tag")
    return {
        "directory_label": f"{directory}/{tag}",
        "filename": filename,
        "bytes": int(row["size_bytes"]),
        "sha256": str(row["declared_sha256"]),
        "source_kind": "public_github_release_asset",
        "source_locator": str(row["source_locator"]),
        "logical_role": str(row["family"]),
    }


def finality_row(row: dict[str, Any]) -> dict[str, Any]:
    filename = safe_component(str(row["filename"]), "Finality filename")
    tag = safe_component(str(row["release_tag"]), "Finality Release tag")
    return {
        "directory_label": f"60-polygon-base-finality/{tag}",
        "filename": filename,
        "bytes": int(row["bytes"]),
        "sha256": str(row["sha256"]),
        "source_kind": "public_github_release_asset",
        "source_locator": str(row["source_locator"]),
        "logical_role": "noncanonical_polygon_base_finality_dependency",
    }


def researcher_files(repo: pathlib.Path) -> list[tuple[str, str]]:
    result = [
        ("preservation/epoch-ii/START-HERE.md", "00-start-here"),
        ("preservation/epoch-ii/AUTHORITY-AND-SCOPE.md", "00-start-here"),
        ("preservation/epoch-ii/LIMITATIONS-AND-EXCLUSIONS.md", "00-start-here"),
        ("preservation/epoch-ii/AI-DISCLOSURE.md", "00-start-here"),
        ("preservation/epoch-ii/HARVARD-DATASET-DESCRIPTION.md", "00-start-here"),
        ("preservation/epoch-ii/HARVARD-TERMS-OF-USE.txt", "00-start-here"),
        ("preservation/epoch-ii/HARVARD-DRAFT-METADATA.json", "00-start-here"),
        ("preservation/HARVARD-EPOCH-II-CAPACITY-AND-ACCEPTANCE.md", "00-start-here"),
        ("preservation/PRESERVATION-EPOCH-II-CONTENT-SCOPE.md", "00-start-here"),
        ("preservation/epoch-ii-publication-scope-decision-20260912.json", "00-start-here"),
        ("preservation/epoch-ii-historical-recovery-search-20260912.json", "00-start-here"),
        ("CITATION.cff", "00-start-here"),
        ("bitcoin-inscription-mirrors/README.md", "10-bitcoin-originals-verbatim"),
        ("bitcoin-inscription-mirrors/manifests/bitcoin-inscription-mirror-manifest.json", "10-bitcoin-originals-verbatim"),
        ("bitcoin-inscription-mirrors/canonical-originals/97631551-protocol-axioms.json", "10-bitcoin-originals-verbatim"),
        ("bitcoin-inscription-mirrors/canonical-originals/98369145-covenant-of-the-flaw.json", "10-bitcoin-originals-verbatim"),
        ("bitcoin-inscription-mirrors/canonical-originals/98387475-trinity-accord-meta-record.json", "10-bitcoin-originals-verbatim"),
        ("bitcoin-inscription-mirrors/raw/97631551.txt", "10-bitcoin-originals-verbatim"),
        ("bitcoin-inscription-mirrors/raw/98369145.txt", "10-bitcoin-originals-verbatim"),
        ("bitcoin-inscription-mirrors/raw/98387475.txt", "10-bitcoin-originals-verbatim"),
        ("physical-verification.md", "20-physical-anchor-guide"),
        ("covenant-proof.md", "20-physical-anchor-guide"),
        ("api/context-packs/physical-anchor-context.json", "20-physical-anchor-guide"),
        ("museum/dist/data/public-flaws.json", "20-physical-anchor-guide"),
        ("evidence/core-object-alpha-shenzhen-notary-2026-05-06.md", "20-physical-anchor-guide"),
        ("nft-text-descriptions/chronicle-full.md", "40-chronicle-175-guide"),
        ("nft-text-descriptions/nft-cars-manifest.json", "40-chronicle-175-guide"),
        ("archive/encrypted-witness-archives.v1.json", "50-computationally-delayed-witnesses"),
        ("archive/first-star-moon-zenodo-state.json", "50-computationally-delayed-witnesses"),
        ("archive/second-star-moon-zenodo-state.json", "50-computationally-delayed-witnesses"),
        ("archive/bubble-constellation-zenodo-state.json", "50-computationally-delayed-witnesses"),
    ]
    for path in sorted((repo / "nft-text-descriptions").glob("0x*.md")):
        result.append((path.relative_to(repo).as_posix(), "40-chronicle-175-texts"))
    return result


def build(repo: pathlib.Path, candidate: pathlib.Path) -> dict[str, Any]:
    content = load(candidate / "CONTENT-CANDIDATE.json")
    scope = load(candidate / "HISTORICAL-PUBLICATION-SCOPE-RESOLUTION.json")
    witness = load(candidate / "ENCRYPTED-DELAYED-ACCESS-VERIFICATION.json")
    if scope.get("status") != "pass" or scope.get("unresolved_scope_decisions") != 0:
        raise SystemExit("historical publication scope is not resolved")
    if witness.get("status") != "pass" or witness.get("logical_files") != 48:
        raise SystemExit("encrypted delayed-access archive verification is incomplete")
    rows: list[dict[str, Any]] = [
        local_row(repo, relative, directory)
        for relative, directory in researcher_files(repo)
    ]
    selected = load(candidate / "SELECTED-RELEASE-ASSETS.json")
    family_directories = {
        "evidence_or_content": "30-public-project-content",
        "encrypted_witness_ciphertext": "50-computationally-delayed-witnesses",
        "presentation_current": "70-museum-reconstruction",
        "research_context": "80-research-context",
    }
    for item in selected:
        family = str(item["family"])
        if family == "sidechain_finality":
            continue
        if family not in family_directories:
            raise SystemExit(f"unexpected selected family: {family}")
        rows.append(public_release_row(item, family_directories[family]))
    finality = load(candidate / "FULL-FINALITY-INSTITUTIONAL-COPY-MANIFEST.json")
    if finality.get("institutional_copy_requirement") != "copy_every_public_file_byte_for_byte":
        raise SystemExit("Finality institutional-copy requirement is missing")
    rows.extend(finality_row(item) for item in finality["files"])
    for path in sorted(candidate.iterdir()):
        if path.is_file():
            rows.append(candidate_row(path, candidate, "90-verification-reports"))
    capsule = candidate / "source-capsule"
    if not capsule.is_dir():
        raise SystemExit("candidate lacks the cold-restored source capsule")
    for path in sorted(capsule.iterdir()):
        if path.is_file():
            rows.append(candidate_row(path, candidate, "95-source-cold-recovery"))
    paths = [f"{row['directory_label']}/{row['filename']}" for row in rows]
    duplicates = sorted(path for path, count in Counter(paths).items() if count > 1)
    if duplicates:
        raise SystemExit(f"duplicate Harvard logical paths: {duplicates}")
    oversize = [path for path, row in zip(paths, rows) if row["bytes"] > MAX_HARVARD_FILE_BYTES]
    if oversize:
        raise SystemExit(f"Harvard per-file size limit exceeded: {oversize}")
    total = sum(int(row["bytes"]) for row in rows)
    by_directory: dict[str, dict[str, int]] = {}
    for directory in sorted({str(row["directory_label"]) for row in rows}):
        matching = [row for row in rows if row["directory_label"] == directory]
        by_directory[directory] = {
            "files": len(matching),
            "bytes": sum(int(row["bytes"]) for row in matching),
        }
    manifest = {
        "schema": SCHEMA,
        "dataset_title": "Trinity Accord — Research Corpus and Preservation Mirror · Preservation Epoch II",
        "role": "new_non_amending_public_research_dataset_and_institutional_mirror",
        "source_git_commit_sha": content["source_git_commit_sha"],
        "candidate_identity_sha256": content["candidate_identity_sha256"],
        "old_harvard_doi_unchanged": "10.7910/DVN/YUCG12",
        "harvard_dataset_created_or_mutated": False,
        "automatic_submit_or_resubmit_allowed": False,
        "all_files_publicly_accessible": True,
        "custom_terms_complete": True,
        "file_count": len(rows),
        "total_bytes": total,
        "control_files_not_counted": [
            "DATASET-MANIFEST.json",
            "SHA256SUMS"
        ],
        "planned_control_file_count": 2,
        "planned_harvard_file_count": len(rows) + 2,
        "largest_file_bytes": max(int(row["bytes"]) for row in rows),
        "harvard_per_file_limit_bytes": MAX_HARVARD_FILE_BYTES,
        "all_files_within_per_file_limit": True,
        "polygon_base_finality_files": len(finality["files"]),
        "polygon_base_finality_bytes": int(finality["logical_bytes"]),
        "encrypted_delayed_access_files": int(witness["logical_files"]),
        "encrypted_delayed_access_bytes": int(witness["logical_bytes"]),
        "historical_scope_decisions_unresolved": int(scope["unresolved_scope_decisions"]),
        "directory_summary": by_directory,
        "files": rows,
    }
    identity = json.dumps(
        manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()
    manifest["layout_identity_sha256"] = hashlib.sha256(identity).hexdigest()
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", type=pathlib.Path, default=pathlib.Path("."))
    parser.add_argument("--candidate-dir", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--sha256sums-output", type=pathlib.Path)
    args = parser.parse_args()
    manifest = build(args.repository_root.resolve(), args.candidate_dir.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if args.sha256sums_output:
        args.sha256sums_output.parent.mkdir(parents=True, exist_ok=True)
        args.sha256sums_output.write_text(
            "".join(
                f"{row['sha256']}  {row['directory_label']}/{row['filename']}\n"
                for row in manifest["files"]
            ),
            encoding="utf-8",
        )
    print(
        f"PASS files={manifest['file_count']} bytes={manifest['total_bytes']} "
        f"identity={manifest['layout_identity_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
