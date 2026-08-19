#!/usr/bin/env python3
"""Global workflow action pinning contract.

All GitHub Actions workflows must:
- Use ubuntu-24.04 (not ubuntu-latest) for runs-on
- Pin all actions to full SHA (40-char hex)
- Not use bare tag refs like @v4, @v5
- Not use third-party actions unless allowlisted

The `uses:` parser is intentionally anchored to the YAML key.  Do not use a
substring search here: permission keys such as `statuses: write` contain the
letters `uses:` and used to produce false action-pinning failures.
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
    # actions/setup-node
    "49933ea5288caeca8642d1e84afbd3f7d6820020",
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
# Match only an actual YAML `uses` key, optionally in a list item.  Anchoring
# prevents `statuses: write`, comments, shell text, and other substrings from
# being interpreted as action references.
USES_PATTERN = re.compile(r"^\s*(?:-\s*)?uses:\s*([^\s#]+)")


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def ok(msg: str) -> None:
    print(f"PASS: {msg}")


def _uses_ref(line: str) -> str | None:
    match = USES_PATTERN.match(line)
    return match.group(1) if match else None


def verify_parser_regressions(errors: list[str]) -> None:
    """Guard against broadening the parser back into substring matching."""
    false_positives = [
        "  statuses: write",
        "  issues: write",
        "  # uses: actions/checkout@not-real",
        "  run: echo 'uses: actions/checkout@not-real'",
    ]
    for sample in false_positives:
        if _uses_ref(sample) is not None:
            errors.append(f"action-pinning parser false positive for line: {sample!r}")

    positive = "      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5"
    if _uses_ref(positive) != "actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5":
        errors.append("action-pinning parser regression: real `uses:` key was not recognized")


def main() -> int:
    errors: list[str] = []
    verify_parser_regressions(errors)

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

        # Check actual YAML `uses:` keys only.
        for i, line in enumerate(lines, 1):
            action_ref = _uses_ref(line)
            if action_ref is None:
                continue

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
