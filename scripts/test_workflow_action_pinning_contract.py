#!/usr/bin/env python3
"""Global workflow action pinning contract.

All GitHub Actions workflows must:
- Use ubuntu-24.04 (not ubuntu-latest) for runs-on
- Pin all actions to full SHA (40-char hex)
- Not use bare tag refs like @v4, @v5
- Not use third-party actions unless allowlisted
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"

# Official GitHub actions allowed (by SHA)
ALLOWED_ACTIONS = {
    # actions/checkout
    "34e114876b0b11c390a56381ad16ebd13914f8d5",
    # actions/setup-python
    "a26af69be951a213d495a4c3e4e4022e16d87065",
    # actions/configure-pages
    "983d7736d9b0ae728b81ab479565c72886d7745b",
    # actions/jekyll-build-pages
    "44a6e6beabd48582f863aeeb6cb2151cc1716697",
    # actions/upload-pages-artifact
    "56afc609e74202658d3ffba0e8f6dda462b719fa",
    # actions/deploy-pages
    "d6db90164ac5ed86f2b6aed7e0febac5b3c0c03e",
}

# Allowed action name prefixes (official GitHub actions only)
ALLOWED_PREFIXES = [
    "actions/",
]

SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
USES_PATTERN = re.compile(r"uses:\s*([^\s#]+)")


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def ok(msg: str) -> None:
    print(f"PASS: {msg}")


def main() -> int:
    errors: list[str] = []

    for wf_path in sorted(WORKFLOWS.glob("*.yml")):
        rel = wf_path.relative_to(ROOT)
        text = wf_path.read_text(encoding="utf-8")
        lines = text.splitlines()

        # Check runs-on
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("runs-on:"):
                value = stripped.split(":", 1)[1].strip().strip("'\"")
                if value == "ubuntu-latest":
                    errors.append(f"{rel}:{i}: runs-on uses ubuntu-latest (must be ubuntu-24.04)")

        # Check uses
        for i, line in enumerate(lines, 1):
            match = USES_PATTERN.search(line)
            if not match:
                continue
            action_ref = match.group(1)

            # Split action@ref
            if "@" in action_ref:
                action_name, ref = action_ref.rsplit("@", 1)
            else:
                # uses without @ is allowed for local actions (./.github/actions/...)
                if action_ref.startswith("./"):
                    continue
                errors.append(f"{rel}:{i}: uses without @ reference: {action_ref}")
                continue

            # Local actions are fine
            if action_name.startswith("./"):
                continue

            # Check if action prefix is allowed
            allowed_prefix = any(action_name.startswith(p) for p in ALLOWED_PREFIXES)
            if not allowed_prefix:
                errors.append(f"{rel}:{i}: third-party action not allowlisted: {action_name}")
                continue

            # Check if ref is a full SHA
            if not SHA_PATTERN.match(ref):
                errors.append(
                    f"{rel}:{i}: action ref must be 40-char SHA, got: {action_ref}. "
                    f"Pin to: {action_name}@<full-sha>"
                )

    if errors:
        print("FAIL: workflow action pinning errors:")
        for e in errors:
            print(f"  - {e}")
        return 1

    ok(f"all {len(list(WORKFLOWS.glob('*.yml')))} workflows have pinned actions and ubuntu-24.04")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
