#!/usr/bin/env python3
"""Live non-writing authorship closure using the current public Builder.

This compatibility entrypoint intentionally delegates to the current three-
route smoke. The retired formal-builder-bundles and /gateway/preflight paths
must never be treated as the active authorship closure again.
"""
from __future__ import annotations

import argparse

from smoke_live_external_agent_three_core_preflight import DEFAULT_SITE, run_live_smoke


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", default=DEFAULT_SITE)
    parser.add_argument("--timeout", type=int, default=90)
    # Kept so older scheduled invocations fail forward without changing their
    # argument list. Current runtime metadata is always required by the core smoke.
    parser.add_argument("--allow-missing-runtime-metadata", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()

    run_live_smoke(args.site, args.timeout)
    print("PASS: current zero-clone authorship closure accepted all signed core routes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
