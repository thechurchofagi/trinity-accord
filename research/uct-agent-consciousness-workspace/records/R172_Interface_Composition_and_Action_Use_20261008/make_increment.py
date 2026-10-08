#!/usr/bin/env python3
"""Build the explicitly scoped R172 recovery increment and hash manifest."""

from hashlib import sha256
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import json

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parents[1]
REPO = RESEARCH.parents[1]
WORKSPACE = Path("/workspace/scratch/85a9493d5bb2")
MASTER = WORKSPACE / "library_stage" / "UCT_Hourly_Research_Master_Handoff.md"
OUT = WORKSPACE / "library_stage" / "UCT_R172_Research_Increment_20261008.zip"
MANIFEST = HERE / "INCREMENT_MANIFEST.json"

common = [
    "RESEARCH_MASTER_GUIDE.md", "AGENTS.md", "MEMORY.md", "HANDOFF.md",
    "MASTER_INDEX.md", "REVIEW_SUPERVISION.md", "UCT_FORMAL_MAP.md",
    "UCT_FORMAL_GRAPH.json", "UCT_FORMAL_AUDIT.md",
]
payload = []
for p in sorted(HERE.iterdir()):
    if p.is_file() and p.name not in {"INCREMENT_MANIFEST.json", "DUAL_SAVE_RECEIPT.json"}:
        payload.append((p, p.relative_to(REPO).as_posix()))
for name in common:
    p = RESEARCH / name
    payload.append((p, p.relative_to(REPO).as_posix()))
payload.append((MASTER, "workspace_handoff/UCT_Hourly_Research_Master_Handoff.md"))

items = []
for p, arc in payload:
    raw = p.read_bytes()
    items.append({"path": arc, "size_bytes": len(raw), "sha256": sha256(raw).hexdigest()})
doc = {
    "schema": "UCT_R172_INCREMENT_MANIFEST/v1",
    "scope": "R172 round files, changed research entry/map/review files, and fixed-master candidate; not a complete repository, workspace or history backup",
    "base": {
        "R156_working_set_library_id": "libfile_f7d404c7734c8191b8257cd4fa6771f5",
        "R156_working_set_sha256": "95cc3ea1ec45eb273531c25525edcb7f8e6f2088c650a39b97d24817704ec40a",
        "R172_core_checkpoint": "b32685bef98812281ff9929f82fb98e76dcaa615",
        "R172_verified_graph_repair_head": "2ffd3e7e1fe3c1c5071e37ef7c2e1addfe488367",
    },
    "files": items,
}
MANIFEST.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
with ZipFile(OUT, "w", ZIP_DEFLATED, compresslevel=9) as zf:
    for p, arc in payload:
        zf.write(p, arc)
    zf.write(MANIFEST, MANIFEST.relative_to(REPO).as_posix())
print(json.dumps({
    "path": str(OUT),
    "files": len(items) + 1,
    "size_bytes": OUT.stat().st_size,
    "sha256": sha256(OUT.read_bytes()).hexdigest(),
    "manifest_sha256": sha256(MANIFEST.read_bytes()).hexdigest(),
}, indent=2))
