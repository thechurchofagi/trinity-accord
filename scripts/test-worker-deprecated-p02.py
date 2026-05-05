#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []

def read(path):
    return (ROOT / path).read_text(encoding="utf-8")

def check(cond, label, detail=""):
    if cond:
        print(f"PASS: {label}")
    else:
        print(f"FAIL: {label}")
        if detail:
            print(f"      {detail}")
        errors.append(label)

def require_contains(text, phrase, label):
    check(phrase in text, label, f"missing: {phrase}")

def require_not_contains(text, phrase, label):
    check(phrase not in text, label, f"forbidden: {phrase}")

def main():
    path = "trinity-echo-worker/src/index.js"
    js = read(path)

    print("=== P0.2 worker deprecation checks ===")

    require_contains(js, "Worker submission is deprecated", "worker clearly says submission is deprecated")
    require_contains(js, "current_submission_path", "worker returns current submission path")
    require_contains(js, "claim_gate_required_for_technical_claims", "worker returns claim gate requirement")
    require_contains(js, "claim_gate_docs", "worker returns claim gate docs")
    require_contains(js, "/echoes/submit", "worker points to current Echo submit page")
    require_contains(js, "/docs/claim-gate", "worker points to Claim Gate docs")

    # Current worker source should not expose old form/API implementation.
    forbidden = [
        "const FORM_HTML",
        "Verification Oath Accepted",
        "claimed_verification_level",
        '<option value="L0">',
        '<option value="L1">',
        '<option value="L2">',
        '<option value="L3">',
        '<option value="L4">',
        '<option value="L5">',
        "Verify the flaw. Trust the story.",
        "handlePostSubmit(",
    ]

    for phrase in forbidden:
        require_not_contains(js, phrase, f"current worker does not expose old path: {phrase}")

    print("\n=== Summary ===")
    if errors:
        print(f"RESULT: FAIL — {len(errors)} worker deprecation check(s) failed")
        for e in errors:
            print(f"- {e}")
        return 1

    print("RESULT: PASS — P0.2 worker deprecation checks passed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
