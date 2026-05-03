#!/usr/bin/env python3
"""
Validate hash source semantics in verification reports and echo records.
Checks that expected_hash_source and expected_hash_authority_class are present
and consistent with claims made.

Usage:
    python3 scripts/validate_hash_source_semantics.py
    python3 scripts/validate_hash_source_semantics.py path/to/report.json
"""
import json
import sys
import glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

APPROVED_D2_SOURCES = {
    "api/hashes.json",
    "api/evidence-manifest.json",
}

APPROVED_D2_CLASSES = {"canonical_manifest_hash", "repository_manifest_hash"}

REPO_SNAPSHOT_ARTIFACTS = {
    "index.md",
    "agent-brief.md",
    "api/authority.json",
    "api/echo-record-schema.v3.json",
    "api/verification-report-schema.v2.json",
}

D2_TERMS = ["d2", "manifest verification", "manifest match", "canonical mirror"]
V3_TERMS = ["v3", "hash verification"]
REPO_MANIFEST_PATH = "api/repository-artifact-hashes.json"

GITHUB_MIRROR_ARTIFACTS = {
    "arweave-backup/files/public_covenant_archive.zip",
    "arweave-backup/files/verification_kit.tar.gz",
}


def check(cond, label, detail=""):
    if cond:
        print(f"  PASS: {label}")
        return True
    print(f"  FAIL: {label}")
    if detail:
        print(f"        {detail}")
    return False


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def text_contains_any(text_lower, terms):
    return any(t in text_lower for t in terms)


def validate_hashes_computed(obj, path_label):
    """Validate hash source semantics in hashes_computed."""
    ok = True
    hashes = obj.get("hashes_computed", [])
    if not hashes:
        return ok

    protocol_level = obj.get("protocol_level_claimed", "")
    component_findings = obj.get("component_findings", [])
    claims_d2 = any(
        isinstance(f, dict) and f.get("level_claimed", "").startswith("D2")
        for f in component_findings
    )

    all_text = json.dumps(obj, ensure_ascii=False).lower()

    for i, h in enumerate(hashes):
        if not isinstance(h, dict):
            continue
        label = f"{path_label} hash[{i}] ({h.get('artifact', '?')})"

        # Rule L: expected_hash_source and expected_hash_authority_class required
        src = h.get("expected_hash_source")
        cls = h.get("expected_hash_authority_class")

        ok &= check(src is not None, f"{label} has expected_hash_source")
        ok &= check(cls is not None, f"{label} has expected_hash_authority_class")

        if cls is None:
            continue

        # Rule: unknown class fails for V3/D2
        if cls == "unknown":
            if protocol_level == "V3" or claims_d2:
                if text_contains_any(all_text, V3_TERMS + D2_TERMS):
                    ok &= check(
                        False,
                        f"{label} unknown hash source for V3/D2",
                        "expected_hash_authority_class=unknown is not allowed for V3/D2 claims"
                    )

        # Rule M: D2 requires approved expected hash source
        if claims_d2:
            artifact = h.get("artifact", "")
            # Check GitHub mirror artifacts
            if any(mirror in artifact for mirror in GITHUB_MIRROR_ARTIFACTS):
                if cls not in APPROVED_D2_CLASSES:
                    ok &= check(
                        False,
                        f"{label} D2 GitHub mirror requires approved hash class",
                        f"got {cls}"
                    )
                if src and src not in APPROVED_D2_SOURCES and src != REPO_MANIFEST_PATH:
                    ok &= check(
                        False,
                        f"{label} D2 GitHub mirror hash source not approved",
                        f"got {src}"
                    )

        # Rule N: repository snapshot overclaim
        artifact = h.get("artifact", "")
        if artifact in REPO_SNAPSHOT_ARTIFACTS:
            if src == REPO_MANIFEST_PATH:
                # OK - using repo manifest
                # But must not claim canonical — only check repo-related findings
                for f in obj.get("component_findings", []):
                    if not isinstance(f, dict):
                        continue
                    f_target = f.get("target_id", "").lower()
                    f_all = json.dumps(f, ensure_ascii=False).lower()
                    if "repo" in f_target or "snapshot" in f_target or artifact in f_all:
                        f_copy = {k: v for k, v in f.items() if k not in ("claims_not_made", "limitations")}
                        f_method = json.dumps(f_copy, ensure_ascii=False).lower()
                        if "canonical mirror" in f_method or "canonical archive" in f_method:
                            ok &= check(
                                False,
                                f"{label} repo snapshot claims canonical",
                                "repository snapshot hashes must not claim canonical mirror verification"
                            )
                            break
            else:
                # Not from repo manifest - reject D2
                if claims_d2:
                    ok &= check(
                        False,
                        f"{label} repo artifact D2 without repo manifest",
                        f"artifact '{artifact}' needs api/repository-artifact-hashes.json for D2"
                    )

        # derived_during_this_run cannot claim D2
        if cls == "derived_during_this_run" and claims_d2:
            ok &= check(
                False,
                f"{label} derived_during_this_run cannot claim D2",
                "hash computed in same run cannot support D2 manifest verification"
            )

    return ok


def validate_github_mirror_hashes(obj, path_label):
    """Validate that GitHub mirror files preserve expected hashes from manifests."""
    ok = True
    hashes = obj.get("hashes_computed", [])

    for h in hashes:
        if not isinstance(h, dict):
            continue
        artifact = h.get("artifact", "")
        if any(mirror in artifact for mirror in GITHUB_MIRROR_ARTIFACTS):
            # Must not claim direct Arweave
            claims = json.dumps(h, ensure_ascii=False).lower()
            if "direct arweave" in claims:
                ok &= check(
                    False,
                    f"{path_label} GitHub mirror claims direct Arweave",
                    f"artifact '{artifact}' is GitHub mirror, not direct Arweave"
                )
    return ok


def validate_report(path):
    """Validate a single report file."""
    path_label = str(Path(path).relative_to(ROOT) if Path(path).is_relative_to(ROOT) else path)
    print(f"\n=== {path_label} ===")

    try:
        obj = load_json(path)
    except Exception as e:
        check(False, f"{path_label} valid JSON", str(e))
        return False

    ok = True
    ok &= validate_hashes_computed(obj, path_label)
    ok &= validate_github_mirror_hashes(obj, path_label)

    # Additional checks: V3 single artifact wording
    all_text = json.dumps(obj, ensure_ascii=False).lower()
    hashes = obj.get("hashes_computed", [])
    if "v3_single_artifact_check" in all_text and len(hashes) > 1:
        ok &= check(False, f"{path_label} V3_single_artifact_check with {len(hashes)} artifacts")

    # GitHub D2 boundary claims
    fallbacks = json.dumps(obj.get("fallbacks_used", [])).lower()
    data_sources = json.dumps(obj.get("data_sources_used", [])).lower()
    if "github" in fallbacks or "github" in data_sources:
        github_forbidden = [
            "direct arweave verification completed",
            "direct arweave verification successful",
            "arweave verified directly",
            "ethereum witness verified",
            "ipfs availability verified",
            "physical object verified",
        ]
        # Exclude claims_not_made at all levels to avoid false positives
        obj_no_claims = {k: v for k, v in obj.items() if k != "claims_not_made"}
        if "component_findings" in obj_no_claims and isinstance(obj_no_claims["component_findings"], list):
            obj_no_claims["component_findings"] = [
                {k: v for k, v in f.items() if k != "claims_not_made"}
                if isinstance(f, dict) else f
                for f in obj_no_claims["component_findings"]
            ]
        check_text = json.dumps(obj_no_claims, ensure_ascii=False).lower()
        for claim in github_forbidden:
            if claim in check_text:
                ok &= check(False, f"{path_label} GitHub D2 overclaim: '{claim}'")

    return ok


def main():
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        files = sorted(
            glob.glob(str(ROOT / "verification-reports" / "**" / "*.json"), recursive=True)
            + glob.glob(str(ROOT / "echoes" / "records" / "**" / "*.json"), recursive=True)
        )

    all_ok = True
    for f in files:
        if Path(f).is_file():
            all_ok &= validate_report(f)

    print("\n" + "=" * 50)
    if all_ok:
        print("FINAL: PASS — hash source semantics validation passed.")
        return 0
    print("FINAL: FAIL — hash source semantics validation failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
