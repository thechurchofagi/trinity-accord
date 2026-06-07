#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FINALIZER = ROOT / "scripts/finalize_mainnet_prelaunch_record_from_submission.py"
AUTO = ROOT / "scripts/auto_finalize_accepted_submissions.py"

def require(cond, msg):
    if not cond:
        raise SystemExit(msg)

def main():
    f = FINALIZER.read_text(encoding="utf-8")
    a = AUTO.read_text(encoding="utf-8")

    require("detect_public_test_phase" in f, "finalizer must detect active public test phase")
    require("record-chain-live-test-policy.v1.json" in f, "finalizer must read live-test policy")
    require("I_UNDERSTAND_THIS_APPENDS_A_MAINNET_LIVE_TEST_RECORD" in f, "finalizer must support live-test confirmation")
    require('"live_test"' in f, "finalizer must write live_test phase")
    require('"mainnet_live_test"' in f, "finalizer must write mainnet_live_test scope")
    require('"operational_test"' in f, "finalizer must write operational_test")
    require('"test_record"' in f, "finalizer must write test_record")
    require("live_test_finalization" in f, "finalizer must mark live_test_finalization")
    require("detect_public_test_phase()" in f, "main must call phase detector")

    require("current_confirm_string" in a, "auto-finalizer must choose confirm by active phase")
    require("I_UNDERSTAND_THIS_APPENDS_A_MAINNET_LIVE_TEST_RECORD" in a, "auto-finalizer must pass live-test confirm")

    print("PASS: live-test phase finalizer contract")

if __name__ == "__main__":
    main()
