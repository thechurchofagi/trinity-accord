#!/usr/bin/env python3
"""Reject direct workflow-dispatch input interpolation inside shell source.

GitHub expands `${{ inputs.* }}` and `${{ github.event.inputs.* }}` before the
runner shell parses a `run:` block. Embedded quotes and shell syntax can
therefore become executable source. Inputs must first be assigned through
`env:` and then consumed as quoted shell variables.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
UNSAFE = re.compile(r"\$\{\{\s*(?:github\.event\.inputs|inputs)\.")
BLOCK_RUN = re.compile(r"^(\s*)run:\s*[|>]\s*$")
INLINE_RUN = re.compile(r"^(\s*)run:\s*(.+)$")


def find_unsafe_run_interpolations(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    errors: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        block = BLOCK_RUN.match(line)
        if block:
            run_indent = len(block.group(1))
            index += 1
            while index < len(lines):
                candidate = lines[index]
                candidate_indent = len(candidate) - len(candidate.lstrip())
                if candidate.strip() and candidate_indent <= run_indent:
                    break
                if UNSAFE.search(candidate):
                    errors.append(
                        f"{path.relative_to(ROOT)}:{index + 1}: {candidate.strip()}"
                    )
                index += 1
            continue

        inline = INLINE_RUN.match(line)
        if inline and UNSAFE.search(inline.group(2)):
            errors.append(
                f"{path.relative_to(ROOT)}:{index + 1}: {inline.group(2).strip()}"
            )
        index += 1
    return errors


def main() -> int:
    errors: list[str] = []
    for path in sorted(WORKFLOWS.glob("*.y*ml")):
        errors.extend(find_unsafe_run_interpolations(path))
    if errors:
        print(
            "FAIL: workflow-dispatch inputs are interpolated directly into shell source:",
            file=sys.stderr,
        )
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        print(
            "Move each expression to env: and use a quoted shell variable instead.",
            file=sys.stderr,
        )
        return 1
    print("PASS: workflow-dispatch inputs are not interpolated directly into run blocks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
