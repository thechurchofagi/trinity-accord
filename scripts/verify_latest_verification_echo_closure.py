#!/usr/bin/env python3
"""
Verify latest verification Echo closure: wrapper indexed, JSON valid, schema fields, wording.
Generic — not hardcoded to any specific issue number.

Usage:
  python3 scripts/verify_latest_verification_echo_closure.py
  python3 scripts/verify_latest_verification_echo_closure.py \
    --wrapper echoes/records/2026/echo-2026-05-03-000006.json \
    --report verification-reports/v3/2026-05-03-v3-verification-141906.json \
    --issue-title "Echo v3: E2 Verification Echo — V3/D2/B1 — 2026-05-03 14:19 (OpenClaw Agent)"
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

B1_FORBIDDEN = [
    "ordinals envelope detected",
    "inscription content detected",
    "witness extracted",
    "body parsed",
    "body hash reproduced",
]

V3_FORBIDDEN = ["v3_single_artifact_check"]

TITLE_POLICY_PATH = "api/submission-title-policy.json"
ECHO_INDEX_PATH = "api/echo-index.json"


def check(cond, label, detail=""):
    if cond:
        print(f"PASS: {label}")
        return True
    print(f"FAIL: {label}")
    if detail:
        print(f"      {detail}")
    return False


def load_json(path):
    return json.loads(Path(ROOT / path).read_text(encoding="utf-8"))


def find_latest_wrapper():
    records_dir = ROOT / "echoes" / "records"
    candidates = []
    for f in records_dir.rglob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if data.get("record_kind") == "echo_v3_with_verification_report" and \
               data.get("echo_type") == "E2_verification_echo":
                candidates.append(f)
        except Exception:
            continue
    if not candidates:
        return None, None
    candidates.sort(key=lambda p: p.name, reverse=True)
    wrapper_path = candidates[0]
    wrapper = json.loads(wrapper_path.read_text(encoding="utf-8"))
    return wrapper_path, wrapper


def find_linked_report(wrapper):
    linked = wrapper.get("linked_verification_report", {})
    path = linked.get("path", "")
    if path.startswith("/"):
        path = path[1:]
    return path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--wrapper", type=str, default=None)
    parser.add_argument("--report", type=str, default=None)
    parser.add_argument("--issue-title", type=str, default=None)
    args = parser.parse_args()

    ok = True

    # 1. Find or use provided wrapper
    if args.wrapper:
        wrapper_path = Path(args.wrapper)
        if not wrapper_path.is_absolute():
            wrapper_path = ROOT / wrapper_path
        wrapper = json.loads(wrapper_path.read_text(encoding="utf-8"))
    else:
        wrapper_path, wrapper = find_latest_wrapper()
        if wrapper_path is None:
            print("FAIL: No latest verification Echo wrapper found")
            return 1

    ok &= check(True, f"wrapper found: {wrapper_path.relative_to(ROOT)}")

    # 2. Wrapper JSON valid
    try:
        json.dumps(wrapper)
        ok &= check(True, "wrapper JSON valid")
    except Exception as e:
        ok &= check(False, "wrapper JSON valid", str(e))
        print("\n" + "=" * 50)
        print("FINAL: FAIL — latest verification Echo closure verification failed.")
        return 1

    # 3. Wrapper record_kind
    ok &= check(
        wrapper.get("record_kind") == "echo_v3_with_verification_report",
        "wrapper record_kind = echo_v3_with_verification_report"
    )

    # 4. Wrapper echo_type
    ok &= check(
        wrapper.get("echo_type") == "E2_verification_echo",
        "wrapper echo_type = E2_verification_echo"
    )

    # 5. Find linked report
    report_rel = find_linked_report(wrapper)
    if args.report:
        report_rel = args.report
    if report_rel.startswith("/"):
        report_rel = report_rel[1:]
    report_path = ROOT / report_rel

    ok &= check(report_path.exists(), f"linked report exists: {report_rel}")

    if not report_path.exists():
        print("\n" + "=" * 50)
        print("FINAL: FAIL — latest verification Echo closure verification failed.")
        return 1

    # 6. Report JSON valid
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        ok &= check(True, "report JSON valid")
    except Exception as e:
        ok &= check(False, "report JSON valid", str(e))
        print("\n" + "=" * 50)
        print("FINAL: FAIL — latest verification Echo closure verification failed.")
        return 1

    # 7. Wrapper indexed in echo-index
    try:
        idx = load_json(ECHO_INDEX_PATH)
        paths = [r.get("path", "") for r in idx.get("records", [])]
        wrapper_public = "/" + wrapper_path.relative_to(ROOT).as_posix()
        ok &= check(
            wrapper_public in paths,
            f"echo-index includes wrapper {wrapper_public}"
        )
    except Exception as e:
        ok &= check(False, "echo-index readable", str(e))

    # 8. Echo-index record_count matches filesystem
    try:
        import glob
        fs_count = len(glob.glob(str(ROOT / "echoes" / "records" / "**" / "*.json"), recursive=True))
        ok &= check(
            idx.get("record_count") == fs_count,
            f"echo-index record_count matches filesystem ({fs_count})"
        )
    except Exception:
        ok &= check(False, "echo-index record_count check")

    # 9. Wrapper provenance for human_solicited
    independence = wrapper.get("independence_class", "")
    if independence == "human_solicited_agent_response":
        provenance = wrapper.get("discovery_provenance", {})
        ok &= check(
            provenance.get("solicited") is True or provenance.get("source") == "human_directed",
            "wrapper has non-independent provenance for human_solicited"
        )

    # 10. Report hash source fields
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

    # 11. Report scope_class
    findings = report.get("component_findings", [])
    for f in findings:
        if not isinstance(f, dict):
            continue
        ok &= check(
            f.get("scope_class") is not None,
            f"finding '{f.get('component', '?')}' has scope_class"
        )

    # 12. No positive B1 overclaim (exclude claims_not_made)
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
            f"no positive B1 '{phrase}'"
        )

    # 13. No V3_single_artifact_check
    full_text = json.dumps(report, ensure_ascii=False).lower()
    for phrase in V3_FORBIDDEN:
        ok &= check(
            phrase not in full_text,
            f"no '{phrase}'"
        )

    # 14. Title policy check (if title provided)
    title = args.issue_title
    if title:
        try:
            policy = load_json(TITLE_POLICY_PATH)
            patterns = policy.get("title_patterns", [])

            # Determine expected prefix based on record_kind
            rk = wrapper.get("record_kind", "echo_v3_with_verification_report")
            matched = False
            for tp in patterns:
                if tp.get("record_kind") == rk:
                    prefixes = tp.get("required_prefixes", [])
                    for prefix in prefixes:
                        if title.startswith(prefix):
                            matched = True
                            break
                    break

            if not matched:
                # Check anti-patterns
                ambiguous = any(
                    re.match(ap.get("pattern", "").replace("...", ".*"), title)
                    for ap in policy.get("anti_patterns", [])
                    if "V3 Verification" in ap.get("pattern", "")
                )
                ok &= check(
                    False,
                    "issue title matches title policy",
                    f"Ambiguous title: '{title}'"
                )
            else:
                ok &= check(True, "issue title matches title policy")
        except Exception as e:
            ok &= check(False, "title policy check", str(e))

    print("\n" + "=" * 50)
    if ok:
        print("FINAL: PASS — latest verification Echo closure verified.")
        return 0
    print("FINAL: FAIL — latest verification Echo closure verification failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
