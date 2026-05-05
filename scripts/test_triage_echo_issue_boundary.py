#!/usr/bin/env python3
"""ET-005: Triage boundary and V0 overclaim regression tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from triage_echo_issue import (
    detect_boundary,
    detect_boundary_semantic_near_miss,
    detect_v0_overclaim_wording,
)


def test_exact_boundary_passes():
    body = "Bitcoin Originals are final; all mirrors and echoes are non-amending."
    assert detect_boundary(body) is True, "Exact canonical boundary should pass"


def test_exact_boundary_chinese_passes():
    body = "比特币三本体为最终权威；所有镜像与回响均为非修订。"
    assert detect_boundary(body) is True, "Exact Chinese boundary should pass"


def test_94_style_near_boundary_soft_review():
    body = """
    Bitcoin Originals remain final authority.
    This echo is a non-amending mirror; it does not amend, override, or claim canonical status.
    """
    assert detect_boundary(body) is False, "#94 style should NOT pass exact gate"
    assert detect_boundary_semantic_near_miss(body) is True, "#94 style should be near-miss"


def test_no_boundary_is_not_near_miss():
    body = "This is my Echo. I read the repo."
    assert detect_boundary(body) is False
    assert detect_boundary_semantic_near_miss(body) is False, "No boundary should not be near-miss"


def test_partial_boundary_not_near_miss():
    """Only Bitcoin final, no non-amending → not near-miss."""
    body = "Bitcoin Originals are final authority. I read the files."
    assert detect_boundary(body) is False
    assert detect_boundary_semantic_near_miss(body) is False


def test_v0_verification_result_wording_warns():
    body = """
    Echo type: E2 Verification Echo
    Verification level: V0
    Bitcoin Originals are final; all mirrors and echoes are non-amending.
    CI Verification Result: success.
    Limitations: I did not run scripts locally.
    """
    found = detect_v0_overclaim_wording(body)
    assert found, "Expected V0 overclaim wording warning"


def test_v0_ci_status_observed_does_not_warn():
    body = """
    Echo type: E2 Verification Echo
    Verification level: V0
    Bitcoin Originals are final; all mirrors and echoes are non-amending.
    CI Status Observed: success.
    Limitations: I did not run scripts locally.
    """
    found = detect_v0_overclaim_wording(body)
    assert not found, f"CI Status Observed should not warn: {found}"


def test_v3_hash_verified_does_not_warn():
    """V3 using 'hash verified' should NOT trigger V0 overclaim."""
    body = """
    Echo type: E2 Verification Echo
    Verification level: V3
    Bitcoin Originals are final; all mirrors and echoes are non-amending.
    Hash verified: index.md SHA-256 match confirmed.
    """
    found = detect_v0_overclaim_wording(body)
    assert not found, f"V3 hash verified should not trigger V0 warning: {found}"


def main():
    test_exact_boundary_passes()
    test_exact_boundary_chinese_passes()
    test_94_style_near_boundary_soft_review()
    test_no_boundary_is_not_near_miss()
    test_partial_boundary_not_near_miss()
    test_v0_verification_result_wording_warns()
    test_v0_ci_status_observed_does_not_warn()
    test_v3_hash_verified_does_not_warn()
    print("PASS: Echo triage boundary and V0 wording tests")


if __name__ == "__main__":
    main()
