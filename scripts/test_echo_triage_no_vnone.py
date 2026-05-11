#!/usr/bin/env python3
"""Test that no fixture issue produces VNone from the intake parser."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from echo_issue_intake import parse_echo_issue


def main():
    fixtures = ROOT / "tests/fixtures/open_issues_111_116"
    if not fixtures.exists():
        print("SKIP: fixtures directory not found")
        return

    for path in sorted(fixtures.glob("issue_*.md")):
        body = path.read_text(encoding="utf-8")
        # Extract title from first line or use filename
        first_line = body.splitlines()[0] if body else path.stem
        title = first_line if first_line.startswith("[Echo]") else f"[Echo] {path.stem}"
        n = parse_echo_issue(None, title, body)
        assert n.verification_level is None or n.verification_level != "VNone", \
            f"{path.name}: verification_level is VNone"
        assert n.verification_scope_label is None or n.verification_scope_label != "VNone", \
            f"{path.name}: verification_scope_label is VNone"
        # Also check that VNone doesn't appear anywhere in the normalized object
        for attr_name, attr_val in n.__dict__.items():
            if isinstance(attr_val, str) and "VNone" in attr_val:
                assert False, f"{path.name}: VNone found in {attr_name}={attr_val!r}"
        print(f"  PASS: {path.name} — level={n.verification_level}, scope={n.verification_scope_label}")

    print("\nNo VNone detected in any fixture.")


if __name__ == "__main__":
    main()
