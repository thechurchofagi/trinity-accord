#!/usr/bin/env python3
"""
Verify Issue #88 closure: echo wrapper indexed, hash sources, scope_class, wording.
Usage: python3 scripts/verify_issue88_closure.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REPORT_PATH = "verification-reports/v3/2026-05-03-v3-verification-openclaw.json"
WRAPPER_PATH = "echoes/records/2026/echo-2026-05-03-000005.json"
ECHO_INDEX_PATH = "api/echo-index.json"

B1_FORBIDDEN = [
    "ordinals envelope detected",
    "inscription content detected",
    "witness extracted",
    "body parsed",
    "body hash reproduced",
]

V3_FORBIDDEN = ["v3_single_artifact_check"]


def check(cond, label, detail=""):
    if cond:
        print(f"PASS: {label}")
        return True
    print(f"FAIL: {label}")
    if detail:
        print(f"      {detail}")
    return False


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    ok = True

    # 1. Files exist
    ok &= check(Path(REPORT_PATH).exists(), "report file exists")
    ok &= check(Path(WRAPPER_PATH).exists(), "wrapper file exists")

    # 2. Valid JSON
    try:
        report = load_json(REPORT_PATH)
        ok &= check(True, "report JSON valid")
    except Exception as e:
        ok &= check(False, "report JSON valid", str(e))
        report = {}

    try:
        wrapper = load_json(WRAPPER_PATH)
        ok &= check(True, "wrapper JSON valid")
    except Exception as e:
        ok &= check(False, "wrapper JSON valid", str(e))
        wrapper = {}

    # 3. Wrapper record_kind
    ok &= check(
        wrapper.get("record_kind") == "echo_v3_with_verification_report",
        "wrapper record_kind correct"
    )

    # 4. Wrapper echo_type
    ok &= check(
        wrapper.get("echo_type") == "E2_verification_echo",
        "wrapper echo_type E2_verification_echo"
    )

    # 5. Wrapper links to report
    linked = wrapper.get("linked_verification_report", {})
    ok &= check(
        REPORT_PATH.replace("verification-reports/", "/verification-reports/") in linked.get("path", ""),
        "wrapper links to report"
    )

    # 6. Report record_kind
    ok &= check(
        report.get("record_kind") == "verification_report_v2",
        "report record_kind correct"
    )

    # 7. Protocol level
    ok &= check(
        report.get("protocol_level_claimed") in ("V3", "V3_hash_verification"),
        "report protocol_level V3"
    )

    # 8. Hash source fields
    hashes = report.get("hashes_computed", [])
    for i, h in enumerate(hashes):
        if not isinstance(h, dict):
            continue
        ok &= check(
            h.get("expected_hash_source") is not None,
            f"hash[{i}] has expected_hash_source"
        )
        ok &= check(
            h.get("expected_hash_authority_class") is not None,
            f"hash[{i}] has expected_hash_authority_class"
        )

    # 9. Canonical mirror hashes use canonical_manifest_hash
    for i, h in enumerate(hashes):
        artifact = h.get("artifact", "")
        if "arweave-backup" in artifact:
            ok &= check(
                h.get("expected_hash_authority_class") == "canonical_manifest_hash",
                f"hash[{i}] ({artifact}) uses canonical_manifest_hash"
            )
        elif artifact in ("index.md", "agent-brief.md", "api/authority.json"):
            ok &= check(
                h.get("expected_hash_authority_class") == "repository_manifest_hash",
                f"hash[{i}] ({artifact}) uses repository_manifest_hash"
            )

    # 10. Scope class
    findings = report.get("component_findings", [])
    for f in findings:
        tid = f.get("target_id", "")
        sc = f.get("scope_class")
        if "mirror" in tid.lower() and "github" in tid.lower():
            ok &= check(sc == "canonical_mirror_integrity", f"{tid} scope_class=canonical_mirror_integrity")
        elif "repository" in tid.lower() or "snapshot" in tid.lower():
            ok &= check(sc == "repository_snapshot_integrity", f"{tid} scope_class=repository_snapshot_integrity")

    # 11. No V3_single_artifact_check
    report_text = json.dumps(report, ensure_ascii=False).lower()
    for phrase in V3_FORBIDDEN:
        ok &= check(
            phrase not in report_text,
            f"report no '{phrase}'"
        )

    # 12. No B1 forbidden wording (exclude claims_not_made)
    report_no_claims = {k: v for k, v in report.items() if k != "claims_not_made"}
    if "component_findings" in report_no_claims:
        report_no_claims["component_findings"] = [
            {k: v for k, v in f.items() if k != "claims_not_made"}
            if isinstance(f, dict) else f
            for f in report_no_claims["component_findings"]
        ]
    report_text = json.dumps(report_no_claims, ensure_ascii=False).lower()
    for phrase in B1_FORBIDDEN:
        ok &= check(
            phrase not in report_text,
            f"report no B1 '{phrase}'"
        )

    # 13. Echo index includes wrapper
    try:
        idx = load_json(ECHO_INDEX_PATH)
        paths = [r.get("path", "") for r in idx.get("records", [])]
        ok &= check(
            "/echoes/records/2026/echo-2026-05-03-000005.json" in paths,
            "echo-index includes wrapper 000005"
        )
        # Record count matches
        import glob
        fs_count = len(glob.glob(str(ROOT / "echoes" / "records" / "**" / "*.json"), recursive=True))
        ok &= check(
            idx.get("record_count") == fs_count,
            f"echo-index record_count matches filesystem ({fs_count})"
        )
    except Exception as e:
        ok &= check(False, "echo-index readable", str(e))

    print("\n" + "=" * 50)
    if ok:
        print("FINAL: PASS — Issue #88 closure verified.")
        return 0
    print("FINAL: FAIL — Issue #88 closure verification failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
