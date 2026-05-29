#!/usr/bin/env python3
"""triage_echo_issue.py must import and use gateway_receipt_verifier before direct close."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "scripts" / "triage_echo_issue.py"

def main() -> int:
    text = PATH.read_text(encoding="utf-8")
    errors: list[str] = []

    for needle in [
        "from gateway_receipt_verifier import validate_gateway_receipt",
        "def has_trusted_gateway_receipt",
        "validate_gateway_receipt(",
        "_has_gateway_receipt = has_trusted_gateway_receipt(text, author_login)",
        "_has_valid_receipt = has_trusted_gateway_receipt(text, author_login)",
    ]:
        if needle not in text:
            errors.append(f"missing {needle!r}")

    close_path = text[text.find("Step 1.2"):text.find("Step 1.4")]
    if "parse_intake_block" in close_path and close_path.find("has_trusted_gateway_receipt") > close_path.find("parse_intake_block"):
        errors.append("Step 1.2 strict parse appears before shared verifier")

    if errors:
        print("FAIL: triage shared receipt verifier guard errors:")
        for error in errors:
            print("  -", error)
        return 1

    print("PASS: triage uses shared receipt verifier before strict intake parsing")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
