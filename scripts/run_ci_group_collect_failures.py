#!/usr/bin/env python3
"""Run every command in an existing CI group and report all failures.

This is a diagnostic companion to run_ci_group.py. The canonical group runner
remains fail-fast; this wrapper is used only where collecting the complete
failure set is more useful than stopping at the first error.
"""
from __future__ import annotations

import argparse
import sys

from run_ci_group import GROUPS, run_command


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a CI group without stopping at the first failure")
    parser.add_argument("group", choices=sorted(GROUPS), help="Test group to run")
    args = parser.parse_args()

    failures: list[tuple[list[str], int]] = []
    for cmd in GROUPS[args.group]:
        print(f"::group::{args.group}: {' '.join(cmd)}", flush=True)
        rc = run_command(cmd)
        print("::endgroup::", flush=True)
        if rc != 0:
            failures.append((cmd, rc))

    if failures:
        print(f"CI_GROUP_{args.group.upper().replace('-', '_')}_FAILURES={len(failures)}", file=sys.stderr)
        for cmd, code in failures:
            print(f"FAILED ({code}): {' '.join(cmd)}", file=sys.stderr)
        return 1

    marker = args.group.upper().replace("-", "_")
    print(f"CI_GROUP_{marker}_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
