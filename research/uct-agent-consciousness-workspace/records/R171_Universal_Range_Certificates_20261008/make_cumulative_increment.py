#!/usr/bin/env python3
"""Build the R157-R171 cumulative overlay relative to the exact R156 base."""

from hashlib import sha256
import json
import os
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
MANIFEST_NAME = "_R157_R171_CUMULATIVE_MANIFEST.json"


def run(*args):
    return subprocess.check_output(args, cwd=REPO, text=True).strip()


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


if len(sys.argv) != 2:
    raise SystemExit("usage: make_cumulative_increment.py /absolute/output.zip")
output = Path(sys.argv[1]).resolve()
if not output.parent.is_dir():
    raise SystemExit(f"output parent missing: {output.parent}")
local_head = run("git", "rev-parse", "HEAD")
github_research_commit = os.environ.get("GITHUB_RESEARCH_COMMIT", local_head)
if len(github_research_commit) != 40:
    raise SystemExit("GITHUB_RESEARCH_COMMIT must be a 40-character commit SHA")
if run("git", "status", "--porcelain", "--", PREFIX):
    raise SystemExit("research tree must be clean before packaging")
raw = subprocess.check_output(
    ["git", "diff", "--name-status", "-z", f"{BASE_COMMIT}..{local_head}", "--", PREFIX],
    cwd=REPO,
)
parts = raw.decode().split("\0")
members = []
deleted = []
i = 0
while i < len(parts) - 1:
    status = parts[i]
    i += 1
    if not status:
        break
    if status.startswith(("R", "C")):
        old, new = parts[i], parts[i + 1]
        i += 2
        if status.startswith("R"):
            deleted.append(old.removeprefix(PREFIX))
        members.append(new.removeprefix(PREFIX))
    else:
        path = parts[i]
        i += 1
        (deleted if status == "D" else members).append(path.removeprefix(PREFIX))
members, deleted = sorted(set(members)), sorted(set(deleted))
manifest_members = []
for relative in members:
    path = RESEARCH_ROOT / relative
    if not path.is_file():
        raise SystemExit(f"missing payload member: {relative}")
    manifest_members.append({"path": relative, "bytes": path.stat().st_size, "sha256": digest(path)})
manifest = {
    "schema": "UCT_CUMULATIVE_INCREMENT_MANIFEST/v1",
    "rounds": [f"R{n}" for n in range(157, 172)],
    "scope": "Cumulative increment relative to exact recovered R156 working-set base; not a full working-set, repository, or history backup.",
    "required_baseline": {
        "library_file_id": BASE_LIBRARY_ID,
        "filename": "UCT_R156_Working_Set_20261007.zip",
        "sha256": BASE_SHA256,
        "bytes": 3493643,
        "working_set_files": 384,
    },
    "github_research_commit": github_research_commit,
    "local_packaging_commit": local_head,
    "map_revision": "R171-v1.0",
    "nodes": 497,
    "rules": 240,
    "context_links": 137,
    "members": manifest_members,
    "deleted_paths": deleted,
    "member_count": len(manifest_members),
    "restore": "Verify/extract the exact R156 baseline, overlay every listed member, apply deleted_paths, verify member hashes, then fetch later receipt commits before continuing.",
}
manifest_bytes = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode()
with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for relative in members:
        archive.write(RESEARCH_ROOT / relative, relative)
    archive.writestr(MANIFEST_NAME, manifest_bytes)
with zipfile.ZipFile(output) as archive:
    names = archive.namelist()
    assert names[-1] == MANIFEST_NAME and len(names) == len(members) + 1
    for item in manifest_members:
        payload = archive.read(item["path"])
        assert len(payload) == item["bytes"]
        assert sha256(payload).hexdigest() == item["sha256"]
print(json.dumps({
    "output": str(output),
    "bytes": output.stat().st_size,
    "sha256": digest(output),
    "payload_members": len(members),
    "zip_members": len(members) + 1,
    "deleted_paths": len(deleted),
    "github_research_commit": github_research_commit,
    "local_packaging_commit": local_head,
}, indent=2))
