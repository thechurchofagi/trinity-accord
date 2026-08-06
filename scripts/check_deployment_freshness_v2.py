#!/usr/bin/env python3
"""Run the byte-exact deployment contract plus executable Builder smoke."""
from __future__ import annotations

import argparse
from pathlib import Path

import check_deployment_freshness_v2_core as core
from smoke_live_builder_download import verify_builder


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--site-dir", type=Path)
    source.add_argument("--site")
    parser.add_argument("--timeout", type=int, default=20)
    return parser.parse_known_args()[0]


def main() -> int:
    result = core.main()
    if result != 0:
        return result
    args = _arguments()
    errors = verify_builder(site=args.site, site_dir=args.site_dir, timeout=args.timeout)
    if errors:
        print("FAIL: executable canonical Builder deployment checks:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("PASS: deployed canonical Builder is manifest-bound and executable from one file")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
