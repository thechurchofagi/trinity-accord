#!/usr/bin/env python3
"""Guard: guardian-join.md must not document authorship-first + guardian --fill-registration second.

If the official docs show the wrong proof ordering, agents will reproduce
signed_payload_sha256 mismatch in the field.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "guardian-join.md"


def main():
    text = DOC.read_text(encoding="utf-8")

    # Find all code blocks
    code_blocks = re.findall(r"```bash\n(.*?)```", text, re.DOTALL)

    # Look for the pattern: authorship builder appears BEFORE guardian builder
    authorship_idx = None
    guardian_fill_idx = None

    for i, block in enumerate(code_blocks):
        if "build_agent_authorship_proof.mjs" in block:
            if authorship_idx is None:
                authorship_idx = i
        if "build_guardian_presence_proof.mjs" in block and "--fill-registration" in block:
            if guardian_fill_idx is None:
                guardian_fill_idx = i

    if authorship_idx is not None and guardian_fill_idx is not None:
        if authorship_idx < guardian_fill_idx:
            print(f"FAIL: guardian-join.md shows authorship builder (block {authorship_idx}) "
                  f"before guardian --fill-registration (block {guardian_fill_idx}). "
                  f"This ordering causes signed_payload_sha256 mismatch. "
                  f"Guardian --fill-registration must come first.")
            sys.exit(1)

    # Also verify that the recommended flow mentions Guardian first
    if "Guardian proof first" not in text and "guardian first" not in text.lower():
        # Check that at least guardian builder appears before authorship builder in the docs
        guardian_pos = text.find("build_guardian_presence_proof.mjs")
        authorship_pos = text.find("build_agent_authorship_proof.mjs")
        if guardian_pos != -1 and authorship_pos != -1:
            if authorship_pos < guardian_pos:
                print("FAIL: In guardian-join.md, authorship builder appears before guardian builder. "
                      "Recommended order is Guardian first, authorship second.")
                sys.exit(1)

    print("DUAL_PROOF_ORDERING_POLICY_OK")


if __name__ == "__main__":
    main()
