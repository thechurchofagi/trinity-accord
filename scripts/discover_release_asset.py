#!/usr/bin/env python3
"""Discover a GitHub Release asset by candidate names.

Requires gh CLI. Outputs JSON:
- found: true/false
- release_tag
- asset_name
- size_bytes if available
"""

import argparse
import json
import shutil
import subprocess
import sys

def run(cmd):
    p = subprocess.run(cmd, text=True, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\nSTDOUT:\n{p.stdout}\nSTDERR:\n{p.stderr}")
    return p.stdout

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="thechurchofagi/trinity-accord")
    ap.add_argument("--names", nargs="+", required=True)
    ap.add_argument("--limit", type=int, default=100)
    args = ap.parse_args()

    if shutil.which("gh") is None:
        print(json.dumps({"found": False, "error": "gh not available"}))
        return 2

    releases = json.loads(run([
        "gh", "release", "list",
        "--repo", args.repo,
        "--limit", str(args.limit),
        "--json", "tagName"
    ]))

    wanted = set(args.names)

    for rel in releases:
        tag = rel["tagName"]
        view = json.loads(run([
            "gh", "release", "view", tag,
            "--repo", args.repo,
            "--json", "tagName,assets"
        ]))
        for asset in view.get("assets", []):
            name = asset.get("name")
            if name in wanted:
                print(json.dumps({
                    "found": True,
                    "release_tag": tag,
                    "asset_name": name,
                    "size_bytes": asset.get("size")
                }, indent=2))
                return 0

    print(json.dumps({"found": False}, indent=2))
    return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(json.dumps({"found": False, "error": str(e)}, indent=2))
        sys.exit(2)
