#!/usr/bin/env python3
"""Phase 11: Release Asset / Manifest Audit.

Validates release manifests for structure, boundaries, and consistency.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_OUTDIR = ROOT / "audit" / "redteam" / "e2e-agent-echo-verification"


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=str, default=str(DEFAULT_OUTDIR))
    parser.add_argument("--allow-network", action="store_true")
    args = parser.parse_args()

    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    findings = []
    total_checks = 0
    total_passed = 0
    total_failed = 0

    manifests = [
        "RELEASE-LARGE-DATA-MANIFEST.json",
        "archive/hash-manifest.json",
        "api/evidence-manifest.json",
        "evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json",
    ]

    for manifest_rel in manifests:
        manifest_path = ROOT / manifest_rel
        if not manifest_path.exists():
            continue

        try:
            data = json.loads(manifest_path.read_text())
        except json.JSONDecodeError as e:
            findings.append({"severity": "high", "title": f"Invalid JSON: {manifest_rel}", "description": str(e)})
            total_checks += 1
            total_failed += 1
            continue

        assets = data.get("assets", [])
        assets_total = data.get("assets_total", -1)

        # Check assets_total matches actual count
        total_checks += 1
        if assets_total == len(assets):
            total_passed += 1
        else:
            total_failed += 1
            findings.append({
                "severity": "medium",
                "title": f"assets_total mismatch: {manifest_rel}",
                "file": manifest_rel,
                "expected": f"assets_total = {len(assets)}",
                "actual": f"assets_total = {assets_total}",
            })

        # Check each asset has sha256 and size_bytes
        for asset in assets:
            total_checks += 1
            if "sha256" in asset and len(str(asset["sha256"])) == 64:
                total_passed += 1
            else:
                total_failed += 1
                findings.append({
                    "severity": "medium",
                    "title": f"Asset missing/invalid sha256 in {manifest_rel}",
                    "file": manifest_rel,
                    "description": f"Asset: {asset.get('logical_path', asset.get('filename', '?'))}",
                })

            total_checks += 1
            if "size_bytes" in asset and asset["size_bytes"] > 0:
                total_passed += 1
            else:
                total_failed += 1
                findings.append({
                    "severity": "medium",
                    "title": f"Asset missing/invalid size_bytes in {manifest_rel}",
                    "file": manifest_rel,
                })

            # Check non-amending boundary
            total_checks += 1
            text = json.dumps(asset).lower()
            if "non_amending" in text or "non-amending" in text:
                total_passed += 1
            else:
                total_failed += 1
                findings.append({
                    "severity": "medium",
                    "title": f"Asset missing non-amending boundary in {manifest_rel}",
                    "file": manifest_rel,
                })

            # Check source_path_exists=false assets have download URL
            if asset.get("source_path_exists") is False:
                total_checks += 1
                has_url = any(k in asset for k in ["download_url", "release_tag", "manifest_ref"])
                if has_url:
                    total_passed += 1
                else:
                    total_failed += 1
                    findings.append({
                        "severity": "high",
                        "title": f"Externalized asset missing download reference in {manifest_rel}",
                        "file": manifest_rel,
                        "description": f"Asset {asset.get('logical_path', '?')} has source_path_exists=false but no download_url/release_tag",
                    })

        # Check note field for boundary
        note = data.get("note", "")
        total_checks += 1
        note_lower = note.lower()
        if "non-amending" in note_lower or "non_amending" in note_lower or "mirror" in note_lower:
            total_passed += 1
        else:
            total_failed += 1
            findings.append({
                "severity": "medium",
                "title": f"Manifest note missing boundary: {manifest_rel}",
                "file": manifest_rel,
            })

    result = {
        "phase": "release",
        "checks": total_checks,
        "passed": total_passed,
        "failed": total_failed,
        "warnings": 0,
        "findings": findings,
    }
    (outdir / "release_results.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))

    print(f"Release Asset Audit: {total_checks} checks, {total_passed} passed, {total_failed} failed")
    for f in findings:
        print(f"  [{f['severity'].upper()}] {f['title']}")
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
