#!/usr/bin/env python3
"""Build a byte-reproducible repository preservation capsule.

The base builder already fixes commit dates, gzip timestamps, tree ordering, and
JSON serialization. Git's pack delta search can still vary when it uses more
than one worker, causing semantically identical recovery bundles to differ by a
few bytes. This wrapper pins pack generation to one thread without changing the
preserved source commit, recovery commit, file set, or rights boundary.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

import build_preservation_capsule as builder


GitText = Callable[..., str]
ORIGINAL_GIT_TEXT: GitText = builder.git_text


def deterministic_git_text(root: Path, *args: str) -> str:
    if len(args) >= 2 and args[0] == "bundle" and args[1] == "create":
        return ORIGINAL_GIT_TEXT(root, "-c", "pack.threads=1", *args)
    return ORIGINAL_GIT_TEXT(root, *args)


def main() -> int:
    builder.git_text = deterministic_git_text
    return builder.main()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        raise SystemExit(130)
