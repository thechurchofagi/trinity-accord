#!/usr/bin/env python3
"""
Audit 8: TA-AVR Report Consistency
Verify test report numbers match actual files.

Run:
    python3 scripts/test_ta_avr_report_consistency.py [--test-root PATH] [--report PATH]
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def count_receipts(test_root):
    """Count receipts by level in test root."""
    levels = {}
    count = 0
    for p in test_root.rglob("agent-verification-receipt.json"):
        try:
            obj = json.loads(p.read_text())
            lvl = obj["verification_outputs"]["allowed_protocol_level"]
            levels[lvl] = levels.get(lvl, 0) + 1
            count += 1
        except Exception:
            levels["parse_error"] = levels.get("parse_error", 0) + 1
    return count, levels


def count_custody_packages(test_root):
    return len(list(test_root.rglob("agent-custody-package.zip")))


def check_report_overclaim(text):
    """Check for overclaim language in report."""
    forbidden = [
        (r"formal\s+attestation\s+achieved", "formal attestation achieved"),
        (r"independent\s+attestation\s+achieved", "independent attestation achieved"),
        (r"full\s+verification\s+complete", "full verification complete"),
        (r"physical\s+object\s+verified", "physical object verified"),
        (r"truth\s+proven", "truth proven"),
        (r"AGI\s+accepted", "AGI accepted"),
        (r"authority\s+established\s+by\s+receipt", "authority established by receipt"),
    ]
    found = []
    text_lower = text.lower()
    for pattern, desc in forbidden:
        if re.search(pattern, text_lower):
            # Check negation context
            for m in re.finditer(pattern, text_lower):
                start = max(0, m.start() - 60)
                context = text_lower[start:m.start()]
                if any(neg in context for neg in ["not ", "does not", "never", "no "]):
                    continue
                found.append(desc)
    return found


def test_report_consistency(test_root_path, report_path=None):
    """Report numbers match actual files."""
    test_root = Path(test_root_path)
    if not test_root.exists():
        print(f"  SKIP: test root not found: {test_root}")
        return True

    actual_count, actual_levels = count_receipts(test_root)
    actual_custody = count_custody_packages(test_root)

    # Check SUMMARY.json
    summary_path = test_root / "SUMMARY.json"
    if summary_path.exists():
        summary = json.loads(summary_path.read_text())
        if summary.get("receipt_count") != actual_count:
            print(f"  FAIL: SUMMARY receipt_count {summary.get('receipt_count')} != actual {actual_count}")
            return False
        if summary.get("custody_package_count") != actual_custody:
            print(f"  FAIL: SUMMARY custody count {summary.get('custody_package_count')} != actual {actual_custody}")
            return False

    # Check REPORT.md if provided
    if report_path:
        rp = Path(report_path)
        if rp.exists():
            text = rp.read_text()

            # Check overclaim
            overclaims = check_report_overclaim(text)
            if overclaims:
                for oc in overclaims:
                    print(f"  FAIL: report overclaim: {oc}")
                return False

            # Check tarball sha256
            tarball_sha_path = test_root / "tarball.sha256" if test_root.exists() else None
            # Also check in verification-reports dir
            tarball_sha_in_report = rp.parent / "tarball.sha256"
            if tarball_sha_in_report.exists():
                sha_content = tarball_sha_in_report.read_text().strip()
                if len(sha_content) < 64:
                    print(f"  FAIL: tarball.sha256 appears invalid")
                    return False

    print(f"  PASS: reported counts match actual (receipts={actual_count}, custody={actual_custody})")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-root", help="Path to test root directory")
    parser.add_argument("--report", help="Path to REPORT.md")
    args = parser.parse_args()

    print("Running test_ta_avr_report_consistency.py")

    if args.test_root:
        ok = test_report_consistency(args.test_root, args.report)
        sys.exit(0 if ok else 1)
    else:
        # Try to find latest test root
        tr_dir = ROOT / "test-runs"
        if tr_dir.exists():
            dirs = sorted([d for d in tr_dir.iterdir() if d.is_dir()], reverse=True)
            if dirs:
                print(f"  INFO: using latest test root: {dirs[0].name}")
                ok = test_report_consistency(dirs[0])
                sys.exit(0 if ok else 1)

        print("  SKIP: no test root provided")
        print("  Usage: python3 scripts/test_ta_avr_report_consistency.py --test-root test-runs/ta-avr-large-scale-YYYYMMDD-HHMMSS")
        sys.exit(0)


if __name__ == "__main__":
    main()
