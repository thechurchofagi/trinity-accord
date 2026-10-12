#!/usr/bin/env python3
"""Build a deterministic A5F science increment and external manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path


def run(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=repo, text=True).strip()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--zip", dest="zip_path", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()

    repo = args.repo.resolve()
    base = run(repo, "rev-parse", args.base)
    target = run(repo, "rev-parse", args.target)
    tree = run(repo, "rev-parse", f"{target}^{{tree}}")
    paths = run(repo, "diff", "--name-only", base, target).splitlines()
    if not paths:
        raise SystemExit("empty increment")

    entries = []
    for rel in paths:
        path = repo / rel
        if not path.is_file():
            raise SystemExit(f"unsupported non-file delta: {rel}")
        working_blob = run(repo, "hash-object", rel)
        target_blob = run(repo, "rev-parse", f"{target}:{rel}")
        if working_blob != target_blob:
            raise SystemExit(f"working file differs from target: {rel}")
        entries.append({"path": rel, "sha256": sha256(path), "bytes": path.stat().st_size, "git_blob": target_blob})

    args.zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for item in entries:
            data = (repo / item["path"]).read_bytes()
            info = zipfile.ZipInfo(item["path"], date_time=(1980, 1, 1, 0, 0, 0))
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data, compresslevel=9)

    manifest = {
        "schema": "uct-increment-manifest/1",
        "research_id": "A5F20261012",
        "scope": "INCREMENT_ONLY_NOT_FULL_REPOSITORY",
        "base_commit": base,
        "target_science_commit": target,
        "target_tree": tree,
        "path_count": len(entries),
        "entries": entries,
        "archive": {"filename": args.zip_path.name, "bytes": args.zip_path.stat().st_size, "sha256": sha256(args.zip_path)},
        "recovery": "Check out base_commit, extract the archive at repository root, stage all paths, and verify git write-tree equals target_tree."
    }
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"paths": len(entries), "tree": tree, **manifest["archive"]}, sort_keys=True))


if __name__ == "__main__":
    main()
