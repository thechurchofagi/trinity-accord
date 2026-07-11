#!/usr/bin/env python3
"""Request and record Software Heritage preservation independently of Wayback."""

import argparse
import json
import sys
from pathlib import Path

from scripts.archive_public_web import (
    DEFAULT_REPOSITORY,
    request_software_heritage,
    write_result,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", default=DEFAULT_REPOSITORY)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=float, default=180.0)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        result = {"repository": args.repository, "status": "dry-run"}
    else:
        result = request_software_heritage(args.repository, args.timeout_seconds)
    write_result(args.output, result)
    print(json.dumps({"status": result["status"]}, sort_keys=True))
    return 0 if result["status"] in {"dry-run", "requested"} else 1


if __name__ == "__main__":
    sys.exit(main())
