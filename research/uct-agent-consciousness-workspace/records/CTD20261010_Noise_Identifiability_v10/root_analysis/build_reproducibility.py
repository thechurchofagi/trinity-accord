"""Create the frozen scientific ZIP; keep publication state outside this archive.

Run from any directory. The output defaults to the parent of the record, so it
cannot recursively enter its own inventory. No analysis, fit, or network call is
performed. The archive intentionally precedes DOI reservation; the separately
published Markdown and PDF bind the reserved DOI to this exact scientific text.
"""
from pathlib import Path
import argparse
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "CTD_TA26_v1.0.0"
STAMP = (2026, 10, 10, 0, 0, 0)
EXCLUDE_ROOT = {
    "FILE_MANIFEST.json", "FULL_RECORD_MANIFEST.json", "PERSISTENCE_RECEIPT.json",
    "PUBLICATION_COVERAGE_UPDATE.json", "HANDOFF_ZH.md",
}
EXCLUDE_PREFIX = (
    "release_review/main_sources/", "release_review/scu_sources/",
    "release_review/sources/", "release_review/TA26_PRESERVATION_TEMPLATE/",
    "review/preflight_pages/", "review/title-preflight-",
)


def permitted(path):
    rel = path.relative_to(ROOT).as_posix()
    if path.is_symlink() or not path.is_file():
        return False
    if any(part in {"__pycache__", ".git"} for part in path.relative_to(ROOT).parts):
        return False
    if path.name.endswith("_ZH.md") or rel in EXCLUDE_ROOT or rel.startswith(EXCLUDE_PREFIX):
        return False
    if path.name in {"PERSISTENCE_RECEIPT.json", "PUBLICATION_COVERAGE_UPDATE.json"}:
        return False
    if rel.startswith("release_review/") and rel not in {
        "release_review/PUBLICATION_WORKFLOW_AUDIT.md",
        "release_review/PUBLISHER_SAFETY_REVIEW.md",
        "release_review/PUBLISHER_REVIEW_RECEIPT.json",
        "release_review/SOURCE_RELOCATION_RECEIPT.json",
        "release_review/RELEASE_BUILDER_PREFLIGHT.json",
    }:
        return False
    if rel == "empirical/supplement.txt":
        return False  # Full third-party text; source URL/hash remain in omissions.
    if path.suffix in {".aux", ".log", ".out", ".toc", ".pyc", ".synctex"}:
        return False
    if rel.startswith("manuscript/"):
        return rel in {
            "manuscript/noise-identifiability-bodily-judgments-v1.0.0.md",
            "manuscript/preamble.tex",
        }
    return True


def digest(data):
    return hashlib.sha256(data).hexdigest()


def build(output):
    if ROOT == output or ROOT in output.parents:
        raise ValueError("Output ZIP must be outside the scientific record")
    paths = sorted((p for p in ROOT.rglob("*") if permitted(p)),
                   key=lambda p: p.relative_to(ROOT).as_posix())
    rows = [{"path": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size,
             "sha256": digest(p.read_bytes())} for p in paths]
    source = "manuscript/noise-identifiability-bodily-judgments-v1.0.0.md"
    assert next(r["sha256"] for r in rows if r["path"] == source) == (
        "6bc9dad5add7612735358236c9b7533cc8f54f6aa535443ee2d9e9f5d219c734")
    manifest = {
        "schema": "ctd-scientific-archive-manifest/1",
        "report_number": "TA-TR-2026-26", "version": "1.0.0",
        "result_version": "CTD-RESULT-v1.0.0",
        "scope": "Public scientific reproduction archive, excluding this manifest itself. Operational release state and exact DOI-bound PDF/Markdown are separate public assets.",
        "source_doi_status": "EXPLICIT_PRE_RESERVATION_TEMPLATE",
        "file_count_excluding_manifest": len(rows),
        "files": rows,
    }
    payload = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()
    (ROOT / "FILE_MANIFEST.json").write_bytes(payload)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for row in rows:
            data = (ROOT / row["path"]).read_bytes()
            if len(data) != row["bytes"] or digest(data) != row["sha256"]:
                raise RuntimeError("Input changed during packaging: " + row["path"])
            item = zipfile.ZipInfo(PREFIX + "/" + row["path"], STAMP)
            item.compress_type = zipfile.ZIP_DEFLATED
            item.external_attr = 0o100644 << 16
            z.writestr(item, data)
        item = zipfile.ZipInfo(PREFIX + "/FILE_MANIFEST.json", STAMP)
        item.compress_type = zipfile.ZIP_DEFLATED
        item.external_attr = 0o100644 << 16
        z.writestr(item, payload)
    with zipfile.ZipFile(output) as z:
        assert z.testzip() is None
        assert len(z.namelist()) == len(rows) + 1
        for row in rows:
            data = z.read(PREFIX + "/" + row["path"])
            assert len(data) == row["bytes"] and digest(data) == row["sha256"]
        assert z.read(PREFIX + "/FILE_MANIFEST.json") == payload
    print(json.dumps({"path": str(output), "bytes": output.stat().st_size,
                      "sha256": digest(output.read_bytes()),
                      "entries": len(rows) + 1,
                      "all_members_readback_verified": True}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path,
                        default=ROOT.parent / "reproducibility-v1.0.0.zip")
    args = parser.parse_args()
    build(args.output.resolve())
