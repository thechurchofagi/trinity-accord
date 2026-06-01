#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WF = ROOT / ".github" / "workflows" / "echo-triage.yml"


def check(cond, label):
    if cond:
        print(f"PASS: {label}")
        return True
    print(f"FAIL: {label}")
    return False


def main():
    text = WF.read_text(encoding="utf-8")

    ok = True
    ok &= check("managed_labels" in text, "workflow reads managed_labels")
    ok &= check("removeLabel" in text, "workflow removes stale managed labels")
    ok &= check("updateComment" in text, "workflow updates existing triage comment")
    ok &= check("trinity-echo-triage-v2" in text, "workflow recognizes v2 triage marker")
    ok &= check("trinity-echo-triage-v1" in text, "workflow can update old v1 marker comment")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
