#!/usr/bin/env python3
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path.cwd()
LARGE_BYTES = int(os.environ.get("REPO_SIZE_AUDIT_LARGE_BYTES", "5000000"))
TOP_N = int(os.environ.get("REPO_SIZE_AUDIT_TOP_N", "200"))

BINARY_EXTS = {
    ".zip", ".tar", ".gz", ".tgz", ".xz", ".7z", ".rar",
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic",
    ".mp4", ".mov", ".mkv", ".avi", ".webm",
    ".pdf", ".pptx", ".docx", ".xlsx",
    ".bin", ".car", ".sqlite", ".db", ".wasm",
}

KNOWN_LARGE_PATHS = {
    "archive/evidence/flaw-archive-bundle.zip",
    "archive/evidence/public-covenant-archive.zip",
    "arweave-backup/files/public_covenant_archive.zip",
}
KNOWN_LARGE_PREFIXES = [
    "archive/evidence/flaw-images/指纹/",
]


def run(cmd: list[str], *, check: bool = True, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=ROOT,
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def try_run(cmd: list[str], input_text: str | None = None) -> dict[str, Any]:
    try:
        cp = run(cmd, check=False, input_text=input_text)
        return {
            "cmd": cmd,
            "returncode": cp.returncode,
            "stdout": cp.stdout.strip(),
            "stderr": cp.stderr.strip(),
        }
    except FileNotFoundError as e:
        return {"cmd": cmd, "returncode": 127, "stdout": "", "stderr": str(e)}


def human_size(n: int | float | None) -> str:
    if n is None:
        return "n/a"
    n = float(n)
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    for u in units:
        if abs(n) < 1024 or u == units[-1]:
            return f"{n:.1f} {u}" if u != "B" else f"{int(n)} B"
        n /= 1024
    return f"{n:.1f} TiB"


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def get_git_root() -> Path:
    cp = run(["git", "rev-parse", "--show-toplevel"])
    return Path(cp.stdout.strip())


def get_tracked_files() -> list[str]:
    cp = run(["git", "ls-files", "-z"])
    return [x for x in cp.stdout.split("\0") if x]


def get_current_blob_shas() -> dict[str, list[str]]:
    cp = run(["git", "ls-files", "-s", "-z"])
    out: dict[str, list[str]] = defaultdict(list)
    for rec in cp.stdout.split("\0"):
        if not rec:
            continue
        try:
            meta, path = rec.split("\t", 1)
            parts = meta.split()
            if len(parts) >= 2:
                out[parts[1]].append(path)
        except ValueError:
            continue
    return out


def disk_usage_bytes(path: Path, *, exclude_git: bool = False) -> int:
    total = 0
    if not path.exists():
        return 0
    for dirpath, dirnames, filenames in os.walk(path):
        p = Path(dirpath)
        if exclude_git and p == path:
            dirnames[:] = [d for d in dirnames if d != ".git"]
        if exclude_git and ".git" in p.parts:
            continue
        for name in filenames:
            fp = p / name
            try:
                if not fp.is_symlink():
                    total += fp.stat().st_size
            except FileNotFoundError:
                pass
    return total


def analyze_current_tree(outdir: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    files = get_tracked_files()
    rows: list[dict[str, Any]] = []
    dir_summary: dict[str, dict[str, Any]] = defaultdict(lambda: {"files": 0, "size_bytes": 0})
    ext_summary: dict[str, dict[str, Any]] = defaultdict(lambda: {"files": 0, "size_bytes": 0})

    for rel in files:
        p = ROOT / rel
        try:
            st = p.stat()
        except FileNotFoundError:
            continue
        if not p.is_file():
            continue
        size = st.st_size
        ext = p.suffix.lower() or "[no extension]"
        topdir = rel.split("/", 1)[0]
        is_known_large_path = rel in KNOWN_LARGE_PATHS or any(rel.startswith(prefix) for prefix in KNOWN_LARGE_PREFIXES)
        row = {
            "path": rel,
            "size_bytes": size,
            "size_human": human_size(size),
            "extension": ext,
            "topdir": topdir,
            "is_binary_ext": ext in BINARY_EXTS,
            "exceeds_large_threshold": size >= LARGE_BYTES,
            "known_large_path": is_known_large_path,
            "sha256": sha256_file(p) if size >= LARGE_BYTES else "",
        }
        rows.append(row)
        dir_summary[topdir]["files"] += 1
        dir_summary[topdir]["size_bytes"] += size
        ext_summary[ext]["files"] += 1
        ext_summary[ext]["size_bytes"] += size

    rows.sort(key=lambda r: r["size_bytes"], reverse=True)
    write_csv(outdir / "current_tracked_files.csv", rows, [
        "path", "size_bytes", "size_human", "extension", "topdir",
        "is_binary_ext", "exceeds_large_threshold", "known_large_path", "sha256",
    ])
    write_csv(outdir / "current_top_files.csv", rows[:TOP_N], [
        "path", "size_bytes", "size_human", "extension", "topdir",
        "is_binary_ext", "exceeds_large_threshold", "known_large_path", "sha256",
    ])

    dir_rows = [
        {"topdir": k, "files": v["files"], "size_bytes": v["size_bytes"], "size_human": human_size(v["size_bytes"])}
        for k, v in dir_summary.items()
    ]
    dir_rows.sort(key=lambda r: r["size_bytes"], reverse=True)
    write_csv(outdir / "current_dir_summary.csv", dir_rows, ["topdir", "files", "size_bytes", "size_human"])

    ext_rows = [
        {"extension": k, "files": v["files"], "size_bytes": v["size_bytes"], "size_human": human_size(v["size_bytes"])}
        for k, v in ext_summary.items()
    ]
    ext_rows.sort(key=lambda r: r["size_bytes"], reverse=True)
    write_csv(outdir / "current_ext_summary.csv", ext_rows, ["extension", "files", "size_bytes", "size_human"])

    summary = {
        "tracked_files": len(rows),
        "tracked_size_bytes": sum(r["size_bytes"] for r in rows),
        "tracked_large_files": sum(1 for r in rows if r["exceeds_large_threshold"]),
        "tracked_binary_ext_files": sum(1 for r in rows if r["is_binary_ext"]),
        "top_dirs": dir_rows[:20],
        "top_exts": ext_rows[:20],
    }
    return rows, summary


def analyze_history(outdir: Path, current_blob_shas: dict[str, list[str]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    cp = run(["git", "rev-list", "--objects", "--all"])
    sha_to_paths: dict[str, set[str]] = defaultdict(set)
    shas: list[str] = []
    for line in cp.stdout.splitlines():
        if not line:
            continue
        if " " in line:
            sha, rest = line.split(" ", 1)
            if rest:
                sha_to_paths[sha].add(rest)
        else:
            sha = line
        shas.append(sha)

    seen = set()
    unique_shas = []
    for sha in shas:
        if sha not in seen:
            seen.add(sha)
            unique_shas.append(sha)

    batch_input = "\n".join(unique_shas) + "\n"
    cat = run(["git", "cat-file", "--batch-check=%(objectname)\t%(objecttype)\t%(objectsize)"], input_text=batch_input)

    rows: list[dict[str, Any]] = []
    total_blob_bytes = 0
    large_removed_bytes = 0
    for line in cat.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        sha, typ, size_s = parts
        if typ != "blob":
            continue
        try:
            size = int(size_s)
        except ValueError:
            continue
        paths = sorted(sha_to_paths.get(sha, []))
        path_display = " | ".join(paths[:5])
        ext = Path(paths[0]).suffix.lower() if paths else ""
        present_current = sha in current_blob_shas
        total_blob_bytes += size
        if size >= LARGE_BYTES and not present_current:
            large_removed_bytes += size
        rows.append({
            "object_sha": sha,
            "size_bytes": size,
            "size_human": human_size(size),
            "present_in_current_tree": present_current,
            "current_paths": " | ".join(current_blob_shas.get(sha, [])[:5]),
            "historical_paths": path_display,
            "path_count_seen": len(paths),
            "extension_guess": ext,
            "is_binary_ext_guess": ext in BINARY_EXTS,
            "exceeds_large_threshold": size >= LARGE_BYTES,
            "known_large_path_guess": any(p in KNOWN_LARGE_PATHS or any(p.startswith(pr) for pr in KNOWN_LARGE_PREFIXES) for p in paths),
        })

    rows.sort(key=lambda r: r["size_bytes"], reverse=True)
    fields = [
        "object_sha", "size_bytes", "size_human", "present_in_current_tree", "current_paths",
        "historical_paths", "path_count_seen", "extension_guess", "is_binary_ext_guess",
        "exceeds_large_threshold", "known_large_path_guess",
    ]
    write_csv(outdir / "history_top_blobs.csv", rows[:TOP_N], fields)
    removed_large = [r for r in rows if r["exceeds_large_threshold"] and not r["present_in_current_tree"]]
    write_csv(outdir / "history_large_removed_blobs.csv", removed_large, fields)

    summary = {
        "unique_git_objects_seen": len(unique_shas),
        "unique_blobs_seen": len(rows),
        "total_uncompressed_blob_bytes_upper_bound": total_blob_bytes,
        "large_removed_blob_count": len(removed_large),
        "large_removed_blob_bytes_upper_bound": large_removed_bytes,
        "top_history_blobs": rows[:20],
    }
    return rows, summary


def load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def match_release_assets(outdir: Path, current_rows: list[dict[str, Any]], history_rows: list[dict[str, Any]]) -> dict[str, Any]:
    manifests = []
    for rel in ["RELEASE-LARGE-DATA-MANIFEST.json", "archive/hash-manifest.json", "api/evidence-manifest.json"]:
        data = load_json(ROOT / rel)
        if data is not None:
            manifests.append((rel, data))

    asset_refs: list[dict[str, Any]] = []
    for manifest_path, data in manifests:
        for key in ["assets", "release_assets", "files", "arweave_assets", "ipfs_assets"]:
            val = data.get(key) if isinstance(data, dict) else None
            if not isinstance(val, list):
                continue
            for item in val:
                if not isinstance(item, dict):
                    continue
                sha = str(item.get("sha256") or item.get("expected_sha256") or "").lower()
                if not sha:
                    continue
                asset_refs.append({
                    "manifest": manifest_path,
                    "manifest_section": key,
                    "logical_path": item.get("logical_path") or item.get("path") or "",
                    "asset_name": item.get("asset_name") or "",
                    "release_tag": item.get("release_tag") or data.get("release_tag") or "",
                    "storage_domain": item.get("storage_domain") or "",
                    "sha256": sha,
                    "size_bytes": item.get("size_bytes") or "",
                    "verified": item.get("verified"),
                    "arweave_tx": item.get("arweave_tx") or item.get("source_arweave_tx") or "",
                })

    current_by_sha = {str(r.get("sha256", "")).lower(): r for r in current_rows if r.get("sha256")}
    matches = []
    for a in asset_refs:
        sha = a["sha256"]
        cur = current_by_sha.get(sha)
        matches.append({
            **a,
            "matches_current_large_file_path": cur.get("path", "") if cur else "",
            "note": "Git blob SHA is not file SHA-256; historical blob matches require path/size/manual SHA from checked-out commit.",
        })

    write_csv(outdir / "release_asset_matches.csv", matches, [
        "manifest", "manifest_section", "logical_path", "asset_name", "release_tag", "storage_domain",
        "sha256", "size_bytes", "verified", "arweave_tx", "matches_current_large_file_path", "note",
    ])

    return {
        "manifests_found": [m[0] for m in manifests],
        "asset_refs_with_sha256": len(asset_refs),
        "matches_written": len(matches),
    }


def make_recommendations(current_summary: dict[str, Any], history_summary: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    current_large = current_summary["tracked_large_files"]
    removed_large_bytes = history_summary["large_removed_blob_bytes_upper_bound"]
    repo_git_bytes = baseline.get("git_dir_bytes") or 0

    recs = []
    severity = "low"
    should_rewrite = False

    if current_large:
        severity = "medium"
        recs.append({
            "type": "current-tree-large-files",
            "action": "Inspect current_top_files.csv. Move non-canonical large payloads to GitHub Release/Arweave/IPFS; keep only hashes/manifests in Git.",
            "safe_to_auto_pr": True,
        })

    if removed_large_bytes >= 20 * 1024 * 1024:
        severity = "medium"
        recs.append({
            "type": "historical-large-blobs",
            "action": "History contains large blobs no longer in current tree. This explains clone size. Prefer shallow clone and release-backed assets unless maintainers approve history rewrite.",
            "safe_to_auto_pr": False,
        })

    if repo_git_bytes and removed_large_bytes > repo_git_bytes * 0.35:
        severity = "high"
        recs.append({
            "type": "rewrite-candidate",
            "action": "History rewrite may materially shrink the repository, but it changes commit IDs and may conflict with provenance/audit continuity. Produce a separate rewrite plan; do not execute automatically.",
            "safe_to_auto_pr": False,
        })
        should_rewrite = "manual-review-only"

    if not recs:
        recs.append({
            "type": "no-major-size-issue",
            "action": "No large current files or obvious historical-only large blobs over threshold were found. Keep existing policy tests.",
            "safe_to_auto_pr": False,
        })

    return {
        "severity": severity,
        "rewrite_history_recommendation": should_rewrite or "not-recommended-by-default",
        "recommendations": recs,
        "notes": [
            "large_removed_blob_bytes_upper_bound is uncompressed blob size, not exact packfile savings.",
            "GitHub reported repository size may include packed history and may not equal working tree size.",
            "Do not use git filter-repo without explicit maintainer approval and a migration notice.",
        ],
    }


def write_report(outdir: Path, baseline: dict[str, Any], current_summary: dict[str, Any], history_summary: dict[str, Any], asset_summary: dict[str, Any], recommendations: dict[str, Any]) -> None:
    top_hist = history_summary.get("top_history_blobs", [])[:10]
    top_dirs = current_summary.get("top_dirs", [])[:10]
    top_exts = current_summary.get("top_exts", [])[:10]

    lines = []
    lines.append("# Repository Size Audit Report")
    lines.append("")
    lines.append(f"Generated: `{baseline['generated_at']}`")
    lines.append(f"Repository root: `{baseline['root']}`")
    lines.append("")
    lines.append("## Baseline")
    lines.append("")
    lines.append(f"- `.git` directory size: **{human_size(baseline.get('git_dir_bytes'))}**")
    lines.append(f"- Working tree size excluding `.git`: **{human_size(baseline.get('working_tree_bytes_excluding_git'))}**")
    lines.append(f"- Tracked file size sum: **{human_size(current_summary['tracked_size_bytes'])}**")
    lines.append(f"- Tracked files: **{current_summary['tracked_files']}**")
    lines.append(f"- Tracked files over {human_size(LARGE_BYTES)}: **{current_summary['tracked_large_files']}**")
    lines.append(f"- Historical large removed blobs over {human_size(LARGE_BYTES)}: **{history_summary['large_removed_blob_count']}**")
    lines.append(f"- Historical large removed blob bytes, uncompressed upper bound: **{human_size(history_summary['large_removed_blob_bytes_upper_bound'])}**")
    lines.append("")
    lines.append("## Top current directories")
    lines.append("")
    for r in top_dirs:
        lines.append(f"- `{r['topdir']}` — {r['files']} files, {r['size_human']}")
    lines.append("")
    lines.append("## Top current extensions")
    lines.append("")
    for r in top_exts:
        lines.append(f"- `{r['extension']}` — {r['files']} files, {r['size_human']}")
    lines.append("")
    lines.append("## Top historical blobs")
    lines.append("")
    for r in top_hist:
        paths = r.get("historical_paths") or "[path unknown]"
        current = "current" if r.get("present_in_current_tree") else "removed/history-only"
        lines.append(f"- {r['size_human']} — `{paths}` — `{r['object_sha']}` — {current}")
    lines.append("")
    lines.append("## External asset manifests")
    lines.append("")
    lines.append(f"- Manifests found: {', '.join(asset_summary.get('manifests_found', [])) or 'none'}")
    lines.append(f"- Asset refs with SHA-256: {asset_summary.get('asset_refs_with_sha256', 0)}")
    lines.append("")
    lines.append("## Recommendation")
    lines.append("")
    lines.append(f"Severity: **{recommendations['severity']}**")
    lines.append(f"History rewrite recommendation: **{recommendations['rewrite_history_recommendation']}**")
    lines.append("")
    for rec in recommendations["recommendations"]:
        lines.append(f"- **{rec['type']}**: {rec['action']} Safe auto-PR: `{rec['safe_to_auto_pr']}`")
    lines.append("")
    lines.append("## Files generated")
    lines.append("")
    for name in [
        "baseline.json", "current_tracked_files.csv", "current_top_files.csv",
        "current_dir_summary.csv", "current_ext_summary.csv", "history_top_blobs.csv",
        "history_large_removed_blobs.csv", "release_asset_matches.csv", "recommendations.json",
    ]:
        lines.append(f"- `{name}`")
    lines.append("")
    lines.append("## Manual-only cleanup commands")
    lines.append("")
    lines.append("Do **not** run these automatically. They are templates for a separate maintainer-approved migration plan.")
    lines.append("")
    lines.append("```bash")
    lines.append("# Example only: remove known historical large paths from all history")
    lines.append("# Requires: pipx install git-filter-repo, full backup, protected-branch/tag migration notice")
    lines.append("git filter-repo \\")
    lines.append("  --path archive/evidence/public-covenant-archive.zip \\")
    lines.append("  --path arweave-backup/files/public_covenant_archive.zip \\")
    lines.append("  --path archive/evidence/flaw-archive-bundle.zip \\")
    lines.append("  --path archive/evidence/flaw-images/指纹/ \\")
    lines.append("  --invert-paths")
    lines.append("# Then compare fresh clone size, run full CI, and only then consider force-push with explicit approval.")
    lines.append("```")
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    for note in recommendations["notes"]:
        lines.append(f"- {note}")

    (outdir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    git_root = get_git_root()
    if git_root.resolve() != ROOT.resolve():
        print(f"Please run from git root: {git_root}", file=sys.stderr)
        return 2

    ts = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    outdir = ROOT / "audit" / "repo-size" / ts
    outdir.mkdir(parents=True, exist_ok=True)

    baseline: dict[str, Any] = {
        "generated_at": ts,
        "root": str(ROOT),
        "large_threshold_bytes": LARGE_BYTES,
        "tools": {
            "git": try_run(["git", "--version"]),
            "python": sys.version,
            "git_lfs": try_run(["git", "lfs", "version"]),
            "git_sizer": try_run(["git-sizer", "--version"]),
        },
        "git_status_short": try_run(["git", "status", "--short"]),
        "git_count_objects": try_run(["git", "count-objects", "-vH"]),
        "commit_count_all": try_run(["git", "rev-list", "--count", "--all"]),
        "branch_count": try_run(["git", "branch", "-a"]),
        "tag_count": try_run(["git", "tag", "--list"]),
        "git_dir_bytes": disk_usage_bytes(ROOT / ".git"),
        "working_tree_bytes_excluding_git": disk_usage_bytes(ROOT, exclude_git=True),
    }

    print(f"Writing audit to {outdir}")
    current_rows, current_summary = analyze_current_tree(outdir)
    current_blob_shas = get_current_blob_shas()
    history_rows, history_summary = analyze_history(outdir, current_blob_shas)
    asset_summary = match_release_assets(outdir, current_rows, history_rows)
    recommendations = make_recommendations(current_summary, history_summary, baseline)

    (outdir / "baseline.json").write_text(json.dumps(baseline, indent=2, ensure_ascii=False), encoding="utf-8")
    (outdir / "recommendations.json").write_text(json.dumps(recommendations, indent=2, ensure_ascii=False), encoding="utf-8")
    write_report(outdir, baseline, current_summary, history_summary, asset_summary, recommendations)

    if shutil.which("git-sizer"):
        sizer = try_run(["git-sizer", "--verbose"])
        (outdir / "git-sizer.txt").write_text(sizer["stdout"] + "\n" + sizer["stderr"], encoding="utf-8")

    print(f"Done. Read: {outdir / 'report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
