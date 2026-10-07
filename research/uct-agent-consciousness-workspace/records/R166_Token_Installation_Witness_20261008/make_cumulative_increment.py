#!/usr/bin/env python3
"""Build the R157-R166 cumulative overlay relative to the exact R156 base."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import zipfile


HERE = Path(__file__).resolve().parent
RESEARCH_ROOT = HERE.parents[1]
REPO = RESEARCH_ROOT.parents[1]
BASE_COMMIT = "d80d08a4c0c09559e2122da38e24956b17bb711b"
BASE_LIBRARY_ID = "libfile_f7d404c7734c8191b8257cd4fa6771f5"
BASE_SHA256 = "95cc3ea1ec45eb273531c25525edcb7f8e6f2088c650a39b97d24817704ec40a"
PREFIX = str(RESEARCH_ROOT.relative_to(REPO)) + "/"
MANIFEST_NAME = "_R157_R166_CUMULATIVE_MANIFEST.json"


def run(*args: str) -> str:
    return subprocess.check_output(args, cwd=REPO, text=True).strip()


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


if len(sys.argv) != 2:
    raise SystemExit("usage: make_cumulative_increment.py /absolute/output.zip")

output = Path(sys.argv[1]).resolve()
if not output.parent.is_dir():
    raise SystemExit(f"output parent missing: {output.parent}")

head = run("git", "rev-parse", "HEAD")
status = run("git", "status", "--porcelain", "--", PREFIX)
if status:
    raise SystemExit("research tree must be clean before packaging")

raw = subprocess.check_output(["git", "diff", "--name-status", "-z", f"{BASE_COMMIT}..{head}", "--", PREFIX], cwd=REPO)
parts = raw.decode("utf-8").split("\0")
members, deleted = [], []
index = 0
while index < len(parts) - 1:
    status_code = parts[index]
    index += 1
    if not status_code:
        break
    if status_code.startswith(("R", "C")):
        old_path, new_path = parts[index], parts[index + 1]
        index += 2
        if status_code.startswith("R"):
            deleted.append(old_path.removeprefix(PREFIX))
        members.append(new_path.removeprefix(PREFIX))
    else:
        path = parts[index]
        index += 1
        relative = path.removeprefix(PREFIX)
        (deleted if status_code == "D" else members).append(relative)

members, deleted = sorted(set(members)), sorted(set(deleted))
manifest_members = []
for relative in members:
    path = RESEARCH_ROOT / relative
    if not path.is_file():
        raise SystemExit(f"missing payload member: {relative}")
    manifest_members.append({"path": relative, "bytes": path.stat().st_size, "sha256": digest(path)})

manifest = {
    "schema": "UCT_CUMULATIVE_INCREMENT_MANIFEST/v1",
    "rounds": [f"R{value}" for value in range(157, 167)],
    "scope": "Cumulative increment relative to exact recovered R156 working-set base; not full working-set, repository or history backup.",
    "required_baseline": {
        "library_file_id": BASE_LIBRARY_ID,
        "filename": "UCT_R156_Working_Set_20261007.zip",
        "sha256": BASE_SHA256,
        "bytes": 3493643,
        "working_set_files": 384
    },
    "github_research_commit": head,
    "map_revision": "R166-v1.0",
    "nodes": 452,
    "rules": 217,
    "members": manifest_members,
    "deleted_paths": deleted,
    "member_count": len(manifest_members),
    "restore": "Verify/extract the exact R156 baseline, overlay every listed member, apply deleted_paths, verify member hashes, then fetch later receipt commits before continuing."
}
manifest_bytes = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")

with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for relative in members:
        archive.write(RESEARCH_ROOT / relative, relative)
    archive.writestr(MANIFEST_NAME, manifest_bytes)

with zipfile.ZipFile(output) as archive:
    names = archive.namelist()
    assert names[-1] == MANIFEST_NAME and len(names) == len(members) + 1
    for item in manifest_members:
        assert len(archive.read(item["path"])) == item["bytes"]
        assert sha256(archive.read(item["path"])).hexdigest() == item["sha256"]

print(json.dumps({
    "output": str(output),
    "bytes": output.stat().st_size,
    "sha256": digest(output),
    "payload_members": len(members),
    "zip_members": len(members) + 1,
    "deleted_paths": len(deleted),
    "github_research_commit": head
}, indent=2))
