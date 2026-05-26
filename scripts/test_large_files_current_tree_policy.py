#!/usr/bin/env python3
"""Guardrail: no unapproved large binary files in current Git tree."""
import subprocess
import sys
from pathlib import Path

MAX_WARN = 5 * 1024 * 1024
MAX_FAIL = 10 * 1024 * 1024

ALLOWLIST = {
    # path: max_bytes — owner-approved small assets retained in Git
}

BINARY_EXTS = {
    ".zip", ".tar", ".gz", ".tgz", ".7z",
    ".jpg", ".jpeg", ".png", ".gif", ".webp",
    ".mp4", ".mov", ".avi", ".car", ".pdf",
}


def main():
    out = subprocess.check_output(["git", "ls-tree", "-r", "-l", "HEAD"], text=True)
    failures = []
    warnings = []

    for line in out.splitlines():
        parts = line.split(None, 4)
        if len(parts) < 5:
            continue
        size_s, path = parts[3], parts[4]
        if size_s == "-":
            continue
        size = int(size_s)
        ext = Path(path).suffix.lower()

        if path in ALLOWLIST:
            if size > ALLOWLIST[path]:
                failures.append(
                    f"{path} is {size} bytes; allowlist max {ALLOWLIST[path]}"
                )
            continue

        if ext in BINARY_EXTS and size > MAX_FAIL:
            failures.append(
                f"{path} is binary {ext} and {size} bytes > 10MB; move to Release"
            )
        elif ext in BINARY_EXTS and size > MAX_WARN:
            warnings.append(
                f"{path} is binary {ext} and {size} bytes > 5MB; review for Release"
            )

    for w in warnings:
        print("WARN:", w)

    if failures:
        for f in failures:
            print("FAIL:", f)
        sys.exit(1)

    print("PASS: current tree large-file policy")


if __name__ == "__main__":
    main()
