#!/usr/bin/env python3
"""Run entrypoint discovery smoke plus the actual Builder acquisition journey."""
from __future__ import annotations

import argparse

import smoke_external_agent_entrypoint_journeys_core as core
from smoke_live_builder_download import verify_builder


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--site", default=core.DEFAULT_SITE)
    parser.add_argument("--timeout", type=int, default=30)
    return parser.parse_known_args()[0]


def main() -> int:
    result = core.main()
    if result != 0:
        return result
    args = _arguments()
    errors = verify_builder(site=args.site, timeout=args.timeout)
    if errors:
        print("FAIL: external agent Builder acquisition journey errors:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("PASS: external agent downloaded and executed the manifest-pinned Builder")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
